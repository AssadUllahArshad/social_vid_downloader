from __future__ import annotations

import asyncio
import hashlib
import hmac
import ipaddress
import os
import re
import secrets
import shutil
import threading
import time
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..media_errors import MediaError
from .capabilities import supported_operations
from .engine import OPERATIONS, Options, diagnostic, inspect, process_files

router = APIRouter(prefix="/processing")
running = {}


def context():
    from .. import main

    return main.store, main.root / "_processing"


async def guard(request: Request):
    if not settings.processing_enabled:
        raise MediaError("processing_disabled", "File-processing tools are not yet available.", 503)
    store, _ = context()
    peer = request.client.host if request.client else "unknown"
    if peer in settings.trusted_proxy_ips.split(","):
        try:
            peer = str(ipaddress.ip_address(request.headers.get("X-Forwarded-For", "").split(",")[0].strip()))
        except ValueError:
            pass
    identity = hmac.new(settings.ip_hash_secret.encode(), peer.encode(), hashlib.sha256).hexdigest()
    try:
        limit = 180 if request.method == "GET" else settings.rate_limit_per_minute
        bucket = "read:" if request.method == "GET" else "write:"
        if await store.increment("processing-rate:" + bucket + identity, 60) > limit:
            raise MediaError("rate_limited", "Too many requests. Please wait a minute.", 429)
    except MediaError:
        raise
    except Exception as exc:
        raise MediaError("service_unavailable", "File processing is temporarily unavailable.", 503) from exc


async def record(kind, token):
    if not re.fullmatch(r"[a-f0-9]{32}", token):
        raise MediaError("invalid_token", "This file reference is invalid.", 400)
    store, root = context()
    item = await store.get(f"processing-{kind}:" + token)
    if not item:
        raise MediaError("file_expired", "This file expired. Upload it again.", 410)
    return item, root / token


@router.get("/capabilities", dependencies=[Depends(guard)])
async def capabilities():
    return {
        "operations": sorted(supported_operations()),
        "maxInputBytes": settings.max_file_bytes,
        "maxDurationSeconds": settings.max_duration_seconds,
        "retentionSeconds": settings.file_ttl_seconds,
    }


@router.post("/uploads", dependencies=[Depends(guard)])
async def upload(request: Request):
    if request.headers.get("content-type", "").split(";")[0] != "application/octet-stream":
        raise MediaError("invalid_upload", "Send one media file as a binary upload.", 415)
    store, root = context()
    token = secrets.token_hex(16)
    slot = None
    for index in range(settings.max_concurrent_jobs):
        name = f"processing-upload-slot:{index}"
        if await store.set(name, token, settings.download_timeout_seconds + 60, nx=True):
            slot = name
            break
    if not slot:
        raise MediaError("server_busy", "Uploads are busy. Please try again shortly.", 503)
    folder = root / token
    try:
        if root.is_symlink():
            raise MediaError("storage_unavailable", "File storage is unavailable.", 503)
        total = sum(p.stat().st_size for p in root.parent.rglob("*") if p.is_file())
        active = sum([bool(await store.get(f"processing-upload-slot:{i}")) for i in range(settings.max_concurrent_jobs)])
        if (
            total
            + active * settings.max_file_bytes
            + sum([bool(await store.get(f"download-slot:{i}")) for i in range(settings.max_concurrent_jobs)]) * settings.max_file_bytes * 2
            > settings.max_storage_bytes
        ):
            raise MediaError("storage_busy", "File storage is busy. Please try again later.", 503)
        folder.mkdir(mode=0o700, parents=True, exist_ok=False)
        path = folder / "input.bin"
        size = 0
        async with asyncio.timeout(settings.download_timeout_seconds):
            with path.open("xb") as handle:
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > settings.max_file_bytes:
                        raise MediaError("file_too_large", "This upload exceeds the file size limit.", 413)
                    handle.write(chunk)
        if not size:
            raise MediaError("empty_upload", "Choose a nonempty media file.", 400)
        os.chmod(path, 0o600)
        measured = await run_in_threadpool(inspect, path)
        await store.set("processing-upload:" + token, {"bytes": size, "metadata": measured}, settings.file_ttl_seconds)
        diagnostic(folder, "upload", success=True, bytes=size)
        return {"uploadId": token, "filesize": size, "metadata": measured, "expiresIn": settings.file_ttl_seconds}
    except TimeoutError as exc:
        shutil.rmtree(folder, ignore_errors=True)
        raise MediaError("upload_timeout", "The upload took too long. Try again.", 408) from exc
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    finally:
        await store.compare_delete(slot, token)


class JobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: str
    upload_ids: list[str] = Field(min_length=1, max_length=8)
    options: Options = Field(default_factory=Options)


async def perform(token, payload, paths, slot, cancel):
    store, root = context()
    try:
        result = await run_in_threadpool(process_files, payload.operation, paths, payload.options, root / token, cancel)
        if cancel.is_set():
            shutil.rmtree(root / token, ignore_errors=True)
            raise MediaError("cancelled", "Processing was cancelled.", 409)
        await store.set(
            "processing-job:" + token, {"status": "ready", **{k: v for k, v in result.items() if k != "path"}}, settings.file_ttl_seconds
        )
    except BaseException as exc:
        shutil.rmtree(root / token, ignore_errors=True)
        failure = (
            exc if isinstance(exc, MediaError) else MediaError("processing_failed", "Processing could not finish. Try another input.", 422)
        )
        diagnostic(root / token, "job", operation=payload.operation, success=False, error_category=failure.code)
        await store.set(
            "processing-job:" + token,
            {
                "status": "cancelled" if failure.code == "cancelled" else "error",
                "error": {"code": failure.code, "message": failure.message},
            },
            settings.file_ttl_seconds,
        )
    finally:
        await store.compare_delete(slot, token)
        running.pop(token, None)


@router.post("/jobs", dependencies=[Depends(guard)], status_code=202)
async def create_job(request: Request):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 8192:
            raise MediaError("request_too_large", "This settings request is too large.", 413)
    try:
        payload = JobRequest.model_validate_json(data)
    except ValueError as exc:
        raise MediaError("invalid_settings", "Check the selected files and processing settings.", 400) from exc
    if payload.operation not in OPERATIONS or payload.operation not in supported_operations():
        raise MediaError("operation_unavailable", "This operation is not yet available.", 501)
    paths = []
    for token in payload.upload_ids:
        _, folder = await record("upload", token)
        path = folder / "input.bin"
        if not path.is_file() or path.is_symlink():
            raise MediaError("file_expired", "This upload expired. Upload it again.", 410)
        paths.append(path)
    store, root = context()
    token = secrets.token_hex(16)
    for index in range(settings.max_concurrent_jobs):
        slot = f"download-slot:{index}"
        if await store.set(slot, token, settings.download_timeout_seconds + 60, nx=True):
            break
    else:
        raise MediaError("server_busy", "Processing is busy. Please try again shortly.", 503)
    total = sum(p.stat().st_size for p in root.parent.rglob("*") if p.is_file())
    active_jobs = sum([bool(await store.get(f"download-slot:{i}")) for i in range(settings.max_concurrent_jobs)])
    active_uploads = sum([bool(await store.get(f"processing-upload-slot:{i}")) for i in range(settings.max_concurrent_jobs)])
    if total + active_jobs * settings.max_file_bytes * 2 + active_uploads * settings.max_file_bytes > settings.max_storage_bytes:
        await store.compare_delete(slot, token)
        raise MediaError("storage_busy", "File storage is busy. Please try again later.", 503)
    await store.set("processing-job:" + token, {"status": "processing"}, settings.download_timeout_seconds + settings.file_ttl_seconds)
    cancel = threading.Event()
    task = asyncio.create_task(perform(token, payload, paths, slot, cancel))
    running[token] = (task, cancel)
    diagnostic(root / token, "job_creation", operation=payload.operation, success=True,
               inputs=[hashlib.sha256(path.parent.name.encode()).hexdigest()[:16] for path in paths])
    return {"jobId": token, "status": "processing", "statusUrl": f"/processing/jobs/{token}"}


@router.get("/jobs/{token}", dependencies=[Depends(guard)])
async def status(token: str):
    item, _ = await record("job", token)
    if item["status"] == "ready":
        item = {**item, "downloadUrl": f"/processing/files/{token}"}
    return item


@router.post("/jobs/{token}/cancel", dependencies=[Depends(guard)])
async def cancel_job(token: str):
    item, folder = await record("job", token)
    if token in running:
        running[token][1].set()
        return {"status": "cancelling"}
    shutil.rmtree(folder, ignore_errors=True)
    store, _ = context()
    await store.set("processing-job:" + token, {"status": "cancelled"}, settings.file_ttl_seconds)
    return {"status": "cancelled"}


@router.get("/files/{token}", dependencies=[Depends(guard)])
async def output(token: str):
    item, folder = await record("job", token)
    if item["status"] != "ready" or not re.fullmatch(r"output\.(mp4|webm|mov|mp3|gif|png|srt|json|zip)", item.get("filename", "")):
        raise MediaError("output_unavailable", "This output is not ready or has expired.", 410)
    path = folder / item["filename"]
    if not path.is_file() or path.is_symlink() or folder.is_symlink():
        raise MediaError("file_expired", "This output expired. Process the input again.", 410)
    diagnostic(folder, "delivery", success=True, bytes=path.stat().st_size)
    return FileResponse(path, filename=item["filename"], headers={"Cache-Control": "no-store"})


def sweep(root: Path):
    if not root.is_dir() or root.is_symlink():
        return
    for folder in root.iterdir():
        if re.fullmatch(r"[a-f0-9]{32}", folder.name) and not folder.is_symlink():
            try:
                if time.time() - folder.stat().st_mtime > settings.file_ttl_seconds + settings.download_timeout_seconds:
                    shutil.rmtree(folder, ignore_errors=True)
            except FileNotFoundError:
                pass


async def shutdown():
    for _, cancel in list(running.values()):
        cancel.set()
    if running:
        await asyncio.gather(*[task for task, _ in list(running.values())], return_exceptions=True)
