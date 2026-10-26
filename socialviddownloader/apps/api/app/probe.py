import json
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .audio import audio_catalog
from .config import settings
from .media_errors import MediaError
from .transport import SafeTransport


def inspect_file(path, require_video=True, timeout=12):
    executable = shutil.which(settings.ffprobe_path)
    if not executable:
        raise MediaError("probe_unavailable", "Media verification is unavailable on this server.", 503)
    try:
        result = subprocess.run(
            [
                executable,
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-format_whitelist",
                "mov,matroska,webm,ogg",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=timeout,
            check=True,
        )
        info = json.loads(result.stdout)
        if not any(s.get("codec_type") == "video" for s in info.get("streams", [])) and require_video:
            raise ValueError("No video stream")
        if not any(s.get("codec_type") in {"video", "audio"} for s in info.get("streams", [])):
            raise ValueError("No media stream")
        return info
    except (subprocess.SubprocessError, ValueError) as exc:
        raise MediaError("invalid_media", "The source did not return a valid supported video file.", 502) from exc


def fill_missing_formats(info, platform):
    raw = info.get("formats") or []
    candidates = [
        fmt
        for fmt in raw
        if not fmt.get("has_drm")
        and fmt.get("protocol", "https") in {"http", "https"}
        and fmt.get("vcodec") != "none"
        and not (fmt.get("height") and fmt.get("vcodec") and fmt.get("acodec"))
        and fmt.get("url")
        and fmt.get("ext") in {"mp4", "webm"}
    ][:8]
    # Even a format with known codecs may contain alternate embedded audio.
    # Inspect one combined source when the extractor has not already exposed alternatives.
    eligible = [
        fmt
        for fmt in raw
        if fmt.get("url")
        and not fmt.get("has_drm")
        and fmt.get("protocol", "https") in {"http", "https"}
        and fmt.get("ext") in {"mp4", "webm"}
    ]
    if len(audio_catalog(eligible, platform)) <= 1:
        combined = next(
            (
                fmt
                for fmt in eligible
                if fmt.get("vcodec") not in {None, "none"} and fmt.get("acodec") not in {None, "none"} and "audio_streams" not in fmt
            ),
            None,
        )
        if combined is not None and not any(fmt is combined for fmt in candidates):
            candidates = [combined, *candidates][:8]

    def measure(fmt):
        try:
            with tempfile.TemporaryDirectory(prefix="socialvid-probe-") as folder:
                target = Path(folder) / ("source." + fmt["ext"])
                body, _, status, _ = SafeTransport(platform, max_bytes=8 * 1024 * 1024, timeout=5).open(
                    fmt["url"], headers={**fmt.get("http_headers", {}), "Range": "bytes=0-8388607"}
                )
                try:
                    if status not in {200, 206}:
                        return
                    measured = None
                    with target.open("wb") as output:
                        while chunk := body.read(64 * 1024 if output.tell() == 0 else 256 * 1024):
                            output.write(chunk)
                            if output.tell() == len(chunk):
                                output.flush()
                                try:
                                    measured = inspect_file(target)
                                    break  # Fast-start MP4 headers already identify real streams.
                                except MediaError:
                                    pass  # Some sources put their MP4 index at the end.

                finally:
                    body.close()
                measured = measured or inspect_file(target)
                video = next(s for s in measured["streams"] if s.get("codec_type") == "video")
                audio = next((s for s in measured["streams"] if s.get("codec_type") == "audio"), None)
                fmt.update(
                    height=video["height"],
                    width=video["width"],
                    vcodec=video["codec_name"],
                    acodec=audio["codec_name"] if audio else "none",
                    audio_streams=[
                        {
                            "codec_name": s.get("codec_name"),
                            "bit_rate": s.get("bit_rate"),
                            "tags": s.get("tags", {}),
                            "disposition": s.get("disposition", {}),
                        }
                        for s in measured["streams"]
                        if s.get("codec_type") == "audio"
                    ],
                )
                duration = measured.get("format", {}).get("duration")
                if not info.get("duration") and duration:
                    info["duration"] = float(duration)
        except (MediaError, OSError):
            return  # Unknown dimensions/codecs stay unknown; never infer an HD label.

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(measure, candidates))
