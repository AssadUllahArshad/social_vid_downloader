from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import re
import secrets
import shutil
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import create_engine, text
from starlette.concurrency import run_in_threadpool
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .audio import download_plan
from .config import settings
from .media import generate_file
from .media_errors import MediaError, platform_name
from .processing.api import router as processing_router
from .processing.api import shutdown as processing_shutdown
from .processing.api import sweep as processing_sweep
from .provider_health import STATES, baseline, observe, observe_audio
from .providers import providers
from .security import InvalidUrl, validate_media_url
from .store import store
from .transport import SafeTransport

logger = logging.getLogger("socialvid.api")
logging.basicConfig(level=logging.INFO, format="%(message)s")
engine = create_engine(settings.database_url, pool_pre_ping=True)
work = asyncio.Semaphore(settings.max_concurrent_jobs)
tasks = set()
root = Path(settings.media_root)


def error(code, message, status):
    return JSONResponse(
        {"success": False, "error": {"code": code, "message": message}}, status_code=status,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer"}
    )


def sweep_stale_media(media_root, now, ttl):
    if not media_root.exists() or media_root.is_symlink():
        return
    for folder in media_root.iterdir():
        try:
            if (re.fullmatch(r"[a-f0-9]{32}", folder.name) and not folder.is_symlink()
                    and folder.is_dir() and now - folder.stat().st_mtime > ttl):
                shutil.rmtree(folder, ignore_errors=True)
        except FileNotFoundError:
            # A completed/failed worker may remove its directory during a sweep.
            continue


async def cleanup():
    while True:
        await run_in_threadpool(sweep_stale_media, root, time.time(), settings.file_ttl_seconds + settings.download_timeout_seconds)
        await run_in_threadpool(processing_sweep, root / "_processing")
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app):
    if root.is_symlink():
        raise RuntimeError("Media root must not be a symlink")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    sweeper = asyncio.create_task(cleanup())
    yield
    sweeper.cancel()
    await processing_shutdown()
    if tasks:
        await asyncio.gather(*list(tasks), return_exceptions=True)
    await store.close()
    engine.dispose()


app = FastAPI(
    title="SocialVidDownloader API",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.environment == "development" else None,
)
app.include_router(processing_router)
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization", "Range"], allow_credentials=False)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[host.strip() for host in settings.allowed_hosts.split(",") if host.strip()],
                   www_redirect=False)


@app.middleware("http")
async def protect(request: Request, call_next):
    started = time.monotonic()
    if request.url.path.startswith("/api/"):
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 8192:
                return error("payload_too_large", "This request is too large.", 413)
        request._body = bytes(body)
        peer = request.client.host if request.client else "unknown"
        # Only a configured trusted ingress can supply a client identity.
        if peer in settings.trusted_proxy_ips.split(","):
            candidate = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            import ipaddress

            try:
                peer = str(ipaddress.ip_address(candidate))
            except ValueError:
                pass
        identity = hmac.new(settings.ip_hash_secret.encode(), peer.encode(), hashlib.sha256).hexdigest()
        bucket = "download" if request.url.path.endswith("/download") else "extract" if request.url.path.endswith("/extract") else "read"
        limit = settings.rate_limit_per_minute if bucket != "read" else 180
        try:
            if await store.increment(f"rate:{bucket}:{identity}", 60) > limit:
                response = error("rate_limited", "Too many requests. Please wait a minute.", 429)
                response.headers["Retry-After"] = "60"
                return response
        except Exception:
            return error("service_unavailable", "The video service is currently unavailable. Please try again later.", 503)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    logger.info(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "request", "status": response.status_code, "duration_ms": round((time.monotonic() - started) * 1000)}))
    return response


@app.exception_handler(RequestValidationError)
async def malformed(request, exc):
    return error("invalid_request", "This request is invalid. Please submit the video link again and choose an available quality.", 422)


@app.exception_handler(MediaError)
async def media_failure(request, exc):
    if request.url.path.startswith("/processing/"):
        logger.info(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "processing_rejection",
                               "status": exc.status, "error_category": exc.code}))
    return error(exc.code, exc.message, exc.status)


class ExtractRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)
    platform: Optional[str] = None
    contentType: Optional[str] = None
    model_config = ConfigDict(extra="forbid")


class DownloadRequest(BaseModel):
    sessionId: str = Field(pattern=r"^[a-f0-9]{32}$")
    formatId: str = Field(pattern=r"^[a-f0-9]{20}$")
    audio_mode: Literal["single", "dual", "multi"] = "single"
    audio_track_ids: Optional[list[str]] = Field(default=None, max_length=8)
    model_config = ConfigDict(extra="forbid")


async def session(token):
    if len(token) != 32 or any(c not in "0123456789abcdef" for c in token):
        raise MediaError("invalid_token", "This link is invalid.", 400)
    record = await store.get("session:" + token)
    if not record:
        raise MediaError("session_expired", "This analysis expired. Paste the source link again.", 410)
    return record


@app.post("/api/v1/extract")
async def extract(payload: ExtractRequest):
    try:
        url, platform, kind = validate_media_url(payload.url, payload.platform, payload.contentType)
    except InvalidUrl as exc:
        return error("invalid_url", str(exc), 400)
    provider = providers[platform]
    if platform == "snapchat" and kind == "story":
        return error(
            "content_unsupported", "Snapchat Story downloading is not supported. Only public Spotlight clips are currently supported.", 501
        )
    if not provider.capabilities.enabled or kind == "story":
        return error("provider_disabled", f"This {platform_name(platform)} content type is not currently supported.", 501)
    key = "metadata:audio-v1:" + hashlib.sha256(url.encode()).hexdigest()
    record = await store.get(key)
    started = time.monotonic()
    if not record:
        if work.locked():
            raise MediaError("server_busy", "The video service is busy. Please try again shortly.", 503)
        async with work:
            try:
                record = await run_in_threadpool(provider.extract, url)
            except MediaError as exc:
                await observe(store, platform, "extraction", False, exc.code)
                raise
            await observe(store, platform, "extraction", True)
            await observe_audio(store, platform, metadata=record["metadata"])
        await store.set(key, record, settings.metadata_cache_ttl_seconds)
    token = secrets.token_hex(16)
    await store.set("session:" + token, record, settings.session_ttl_seconds)
    metadata = {k: v for k, v in record["metadata"].items() if k != "thumbnailSource"}
    metadata["contentType"] = record["metadata"].get("contentType", kind)
    metadata["capabilityState"] = STATES.get(platform, {}).get(metadata["contentType"], "UNSUPPORTED")
    metadata["thumbnail"] = f"/api/v1/thumbnail/{token}/" if record["metadata"].get("thumbnailSource") else None
    logger.info(
        json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "extract", "provider": platform, "duration_ms": round((time.monotonic() - started) * 1000), "success": True})
    )
    return {"success": True, "sessionId": token, "expiresIn": settings.session_ttl_seconds, **metadata}


async def prepare(job, record, format_id, slot, audio_mode="single", audio_track_ids=None):
    started = time.monotonic()
    try:
        await store.set("job:" + job, {"status": "processing"}, settings.download_timeout_seconds + settings.file_ttl_seconds)
        async with work:
            result = await run_in_threadpool(generate_file, record, format_id, root / job, audio_mode, audio_track_ids)
        await store.set("job:" + job, {"status": "ready", **result}, settings.file_ttl_seconds)
        await observe(store, record["platform"], "download", True)
        await observe_audio(store, record["platform"], result=result)
        logger.info(
            json.dumps(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event": "download",
                    "provider": record["platform"],
                    "duration_ms": round((time.monotonic() - started) * 1000),
                    "success": True,
                }
            )
        )
    except Exception as exc:
        failure = exc if isinstance(exc, MediaError) else MediaError("processing_failed", "The file could not be prepared.", 502)
        await store.set(
            "job:" + job, {"status": "error", "error": {"code": failure.code, "message": failure.message}}, settings.file_ttl_seconds
        )
        await observe(store, record["platform"], "download", False, failure.code)
        logger.info(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "download", "provider": record["platform"], "error_category": failure.code, "success": False}))
    finally:
        await store.compare_delete(slot, job)


@app.post("/api/v1/download", status_code=202)
async def download(payload: DownloadRequest):
    record = await session(payload.sessionId)
    plan = download_plan(record, payload.formatId, payload.audio_mode, payload.audio_track_ids)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
    if total > settings.max_storage_bytes:
        raise MediaError("storage_busy", "The download service is temporarily unavailable. Please try again later.", 503)
    job = secrets.token_hex(16)
    slot = None
    for index in range(settings.max_concurrent_jobs):
        candidate = f"download-slot:{index}"
        if await store.set(candidate, job, settings.download_timeout_seconds + settings.extract_timeout_seconds + 60, nx=True):
            slot = candidate
            break
    if not slot:
        raise MediaError("server_busy", "The download service is busy. Please try again shortly.", 503)
    # Reserve room for input streams plus the merged output for every claimed
    # slot. Count after claiming so concurrent workers cannot both see no work.
    active_slots = sum([bool(await store.get(f"download-slot:{index}")) for index in range(settings.max_concurrent_jobs)])
    upload_slots = sum([bool(await store.get(f"processing-upload-slot:{index}")) for index in range(settings.max_concurrent_jobs)])
    if total + active_slots * settings.max_file_bytes * 2 + upload_slots * settings.max_file_bytes > settings.max_storage_bytes:
        await store.compare_delete(slot, job)
        raise MediaError("storage_busy", "The download service is temporarily unavailable. Please try again later.", 503)
    await store.set("job:" + job, {"status": "queued"}, settings.download_timeout_seconds + settings.file_ttl_seconds)
    task = asyncio.create_task(prepare(job, record, payload.formatId, slot, payload.audio_mode, payload.audio_track_ids))
    tasks.add(task)
    task.add_done_callback(tasks.discard)
    return {"success": True, "jobId": job, "status": "queued", "statusUrl": f"/api/v1/jobs/{job}/",
            "extension": plan["format"]["extension"], "audio_mode": plan["audio_mode"], "audio_tracks": plan["selected_audio"]}


async def get_job(token):
    if len(token) != 32 or any(c not in "0123456789abcdef" for c in token):
        raise MediaError("invalid_token", "This download link is invalid.", 400)
    record = await store.get("job:" + token)
    if not record:
        raise MediaError("download_expired", "This download expired. Analyze the source again.", 410)
    return record


@app.get("/api/v1/jobs/{token}")
async def job_status(token: str):
    record = await get_job(token)
    public = {k: v for k, v in record.items() if k != "path"}
    if record["status"] == "ready":
        path = Path(record["path"])
        if path.parent != root / token or not path.is_file() or path.is_symlink():
            raise MediaError("download_expired", "This file is no longer available. Analyze the source again.", 410)
        public["downloadUrl"] = f"/api/v1/files/{token}/"
        public["previewUrl"] = f"/api/v1/files/{token}/?inline=1"
    return {"success": True, **public}


@app.get("/api/v1/files/{token}")
async def file(token: str, inline: bool = False):
    record = await get_job(token)
    if record["status"] != "ready":
        raise MediaError("file_not_ready", "This file is not ready yet.", 409)
    path = Path(record["path"])
    if path.parent != root / token or not path.is_file() or path.is_symlink():
        raise MediaError("download_expired", "This file is no longer available.", 410)
    return FileResponse(
        path,
        media_type={"mp4": "video/mp4", "webm": "video/webm", "mkv": "video/x-matroska"}[record["extension"]],
        filename=record["filename"],
        content_disposition_type="inline" if inline else "attachment",
    )


def fetch_thumbnail(record):
    body, headers, status, _ = SafeTransport(record["platform"], max_bytes=2 * 1024 * 1024).open(record["metadata"]["thumbnailSource"])
    try:
        mime = headers.get("Content-Type", "").split(";")[0]
        if status != 200 or mime not in {"image/jpeg", "image/png", "image/webp", "image/avif"}:
            raise MediaError("thumbnail_unavailable", "The source thumbnail is unavailable.", 404)
        return body.read(), mime
    finally:
        body.close()


@app.get("/api/v1/thumbnail/{token}")
async def thumbnail(token: str):
    record = await session(token)
    if not record["metadata"].get("thumbnailSource"):
        raise MediaError("thumbnail_unavailable", "No thumbnail was provided.", 404)
    async with work:
        data, mime = await run_in_threadpool(fetch_thumbnail, record)
    return Response(data, media_type=mime)


@app.get("/api/v1/capabilities")
async def capabilities():
    public = []
    for provider in providers.values():
        observed = await store.get("provider-health:" + provider.name)
        notice = None
        if observed and observed.get("status") == "degraded":
            notice = f"{platform_name(provider.name)} is having trouble processing some public videos. You can try another link or come back later."
        public.append({**provider.public_status(), "contentTypes": STATES[provider.name], "availabilityNotice": notice})
    return {"providers": public}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    try:
        await store.ping()
        if not shutil.which(settings.ffmpeg_path) or not shutil.which(settings.ffprobe_path):
            raise RuntimeError("FFmpeg unavailable")
        if settings.state_backend != "sqlite":

            def check_database():
                with engine.connect() as connection:
                    connection.execute(text("SELECT 1 FROM seo_pages LIMIT 1"))

            await run_in_threadpool(check_database)
    except Exception:
        return error("not_ready", "The video service is not ready. Please try again later.", 503)
    return {"status": "ready", "stateBackend": settings.state_backend}


@app.exception_handler(Exception)
async def unexpected(request, exc):
    logger.error(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "request_failed", "error_category": "internal_error"}))
    return error("internal_error", "The video service could not process this request. Please try again later.", 500)


@app.get("/internal/provider-status")
async def provider_status(request: Request):
    token = settings.admin_provider_token
    supplied = request.headers.get("Authorization", "")
    if not token:
        return error("not_found", "Provider administration is not configured.", 404)
    if not hmac.compare_digest(supplied.encode(), ("Bearer " + token).encode()):
        return error("unauthorized", "Administrator access is required.", 401)
    records = [await store.get("provider-health:" + name) or baseline(name) for name in providers]
    return {"providers": records}
