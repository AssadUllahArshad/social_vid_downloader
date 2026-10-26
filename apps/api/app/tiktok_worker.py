"""Bounded yt-dlp native TikTok download; no unrestricted downloader or user authentication."""

import json
import resource
import sys
import time
from pathlib import Path

from yt_dlp import YoutubeDL

from .audio import language_code
from .config import settings
from .extractor import GuardedRH, QuietLogger
from .media_errors import MediaError, provider_error
from .security import validate_media_url


def download(payload):
    if "+" in payload["selector"]:
        raise MediaError("quality_unavailable", "Choose an available TikTok quality that includes both video and audio.", 400)
    source, platform, _ = validate_media_url(payload["source"], "tiktok")
    directory = Path(payload["directory"])
    deadline = time.monotonic() + settings.download_timeout_seconds

    def progress(event):
        if time.monotonic() > deadline:
            raise MediaError("processing_timeout", "TikTok preparation took too long.", 504)
        total = sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
        if total > settings.max_file_bytes or event.get("downloaded_bytes", 0) > settings.max_file_bytes:
            raise MediaError("file_too_large", "This video exceeds the size limit.", 413)

    options = {
        "quiet": True,
        "logger": QuietLogger(),
        "noplaylist": True,
        "cachedir": False,
        "proxy": "",
        "usenetrc": False,
        "retries": 1,
        "extractor_retries": 1,
        "socket_timeout": 15,
        "format": payload["selector"],
        "outtmpl": str(directory / "native.%(ext)s"),
        "fixup": "never",
        "max_filesize": settings.max_file_bytes,
        "progress_hooks": [progress],
        "overwrites": False,
        "external_downloader": {},
        "remote_components": [],
    }
    with YoutubeDL(options) as ydl:
        director = ydl._request_director
        director.close()
        handler = GuardedRH(platform, deadline, logger=QuietLogger(), proxies={}, cookiejar=ydl.cookiejar)
        handler.transport.max_bytes = settings.max_file_bytes
        director.add_handler(handler)
        info = ydl.extract_info(source, download=False)
        if not info or info.get("_type") in {"playlist", "multi_video"} or info.get("is_live"):
            raise MediaError("content_unsupported", "Only one public TikTok video is supported.")
        if info.get("duration", 0) and info["duration"] > settings.max_duration_seconds:
            raise MediaError("video_too_long", "This video exceeds the duration limit.", 413)
        raw = {str(f.get("format_id")): f for f in info.get("formats", [])}
        inputs = payload.get("inputs") or [{"format_id": payload["selector"], "height": payload["height"]}]
        outputs = []
        for index, requested in enumerate(inputs):
            selector = requested["format_id"]
            fmt = raw.get(selector)
            if not fmt or fmt.get("has_drm") or fmt.get("protocol", "https") not in {"http", "https"}:
                raise MediaError("quality_unavailable", "This TikTok format changed. Analyze the link again.", 410)
            if requested.get("extension") and fmt.get("ext") != requested["extension"]:
                raise MediaError("quality_unavailable", "This TikTok file format changed. Analyze the link again.", 410)
            if payload.get("inputs") and language_code(fmt.get("language")) != language_code(requested.get("language")):
                raise MediaError("audio_track_unavailable", "The selected TikTok audio changed. Analyze the link again.", 410)
            if requested.get("audio_streams") and fmt.get("audio_streams") != requested["audio_streams"]:
                # Embedded stream indices must be remeasured before they can be reused.
                from .probe import fill_missing_formats

                probe = {"formats": [{**fmt, "acodec": None}]}
                fill_missing_formats(probe, platform)
                if probe["formats"][0].get("audio_streams") != requested["audio_streams"]:
                    raise MediaError("audio_track_unavailable", "The selected TikTok audio tracks changed. Analyze the link again.", 410)
            if fmt.get("vcodec") != "none" and requested.get("height") and fmt.get("height") != requested["height"]:
                raise MediaError("quality_unavailable", "This TikTok resolution changed. Analyze the link again.", 410)
            ydl.params["format"] = selector
            ydl.format_selector = ydl.build_format_selector(selector)
            if payload.get("inputs"):
                ydl.params["outtmpl"]["default"] = str(directory / f"native-{index}.%(ext)s")
            before = set(directory.iterdir())
            ydl.process_ie_result({**info, "formats": [fmt]}, download=True)
            created = [
                p
                for p in set(directory.iterdir()) - before
                if p.suffix in {".mp4", ".webm", ".m4a", ".ogg", ".opus"} and not p.is_symlink()
            ]
            if len(created) != 1:
                raise MediaError("invalid_media", "TikTok did not create the selected media file.", 502)
            outputs.extend(created)
    return outputs if payload.get("inputs") else outputs[0]


def main():
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    resource.setrlimit(resource.RLIMIT_FSIZE, (settings.max_file_bytes, settings.max_file_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (settings.download_timeout_seconds, settings.download_timeout_seconds))
    payload = json.loads(sys.stdin.read(8192))
    try:
        path = download(payload)
        print(json.dumps({"success": True, **({"paths": [str(p) for p in path]} if isinstance(path, list) else {"path": str(path)})}))
    except Exception as exc:
        failure = exc if isinstance(exc, MediaError) else provider_error(exc, "tiktok")
        print(json.dumps({"success": False, "error": {"code": failure.code, "message": failure.message, "status": failure.status}}))


if __name__ == "__main__":
    main()
