from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from ..config import settings
from ..media_errors import MediaError

logger = logging.getLogger("socialvid.processing")


def diagnostic(directory, stage, **fields):
    # Never log capability tokens, filenames, commands, source URLs or raw stderr.
    correlation = hashlib.sha256(directory.name.encode()).hexdigest()[:16]
    logger.info(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": "processing",
                            "correlation": correlation, "stage": stage, **fields}))


def execution_failure(returncode, stderr):
    text = stderr.lower()
    if returncode == -signal.SIGXCPU or f"received signal {signal.SIGXCPU}" in text:
        return MediaError("processing_timeout", "Processing reached its CPU limit. Try a shorter file.", 504)
    if returncode == -signal.SIGXFSZ or "file too large" in text:
        return MediaError("output_too_large", "The output exceeds the file size limit. Try a shorter file.", 413)
    if "no space left" in text:
        return MediaError("storage_busy", "File storage is busy. Please try again later.", 503)
    if "cannot allocate memory" in text or "out of memory" in text:
        return MediaError("processing_capacity", "This file exceeds available processing memory. Try a smaller file.", 413)
    if any(term in text for term in ("unknown encoder", "unknown decoder", "decoder not found", "encoder not found")):
        return MediaError("unsupported_codec", "The required codec is unavailable. Choose another format.", 422)
    return MediaError("processing_failed", "Output could not be generated. Check the input and settings.", 422)


FORMATS = "mov,matroska,webm,ogg,mp3,wav,flac,gif,png_pipe,jpeg_pipe,srt"


class Options(BaseModel):
    model_config = ConfigDict(extra="forbid")
    output_format: str = Field(default="mp4", pattern=r"^(mp4|webm|mov)$")
    quality: int = Field(default=28, ge=18, le=40)
    start: float = Field(default=0, ge=0, le=1800)
    end: float | None = Field(default=None, gt=0, le=1800)
    speed: float = Field(default=1, ge=0.5, le=2)
    preserve_audio: bool = True
    fps: int = Field(default=10, ge=1, le=30)
    width: int = Field(default=480, ge=64, le=1920)
    height: int = Field(default=360, ge=64, le=1080)
    frames: int = Field(default=12, ge=2, le=40)
    columns: int = Field(default=4, ge=1, le=8)
    segment_seconds: float = Field(default=10, ge=0.5, le=600)
    image_seconds: float = Field(default=2, ge=0.1, le=60)
    text: str = Field(default="", max_length=300)
    font_size: int = Field(default=24, ge=10, le=100)
    brightness: float = Field(default=0, ge=-0.5, le=0.5)
    contrast: float = Field(default=1, ge=0.5, le=2)
    sharpen: float = Field(default=0, ge=0, le=2)
    silence_db: float = Field(default=-35, ge=-60, le=-10)
    silence_seconds: float = Field(default=0.5, ge=0.1, le=5)
    subtitle_track: int = Field(default=0, ge=0, le=7)


ESSENTIAL = {"converter", "compressor", "trimmer", "merger", "mp3", "remove-audio", "video-to-gif", "speed"}
OPERATIONS = ESSENTIAL | {
    "splitter",
    "gif-to-video",
    "thumbnail",
    "thumbnail-grid",
    "images",
    "image-watermark",
    "text-watermark",
    "burn-subtitles",
    "extract-subtitles",
    "information",
    "filters",
    "stabilizer",
    "trim-silence",
    "storyboard",
}


def inspect(path: Path):
    executable = shutil.which(settings.ffprobe_path)
    if not executable:
        raise MediaError("probe_unavailable", "File inspection is unavailable.", 503)
    try:
        result = subprocess.run(
            [
                executable,
                "-v",
                "error",
                "-protocol_whitelist",
                "file,pipe",
                "-format_whitelist",
                FORMATS,
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=12,
            check=True,
        )
        info = json.loads(result.stdout)
        streams = info.get("streams", [])
        if not streams or len(streams) > 16:
            raise ValueError("streams")
        duration = float(info.get("format", {}).get("duration") or 0)
        if duration > settings.max_duration_seconds:
            raise MediaError("video_too_long", "This media exceeds the duration limit.", 413)
        if any(int(stream.get("width", 0)) * int(stream.get("height", 0)) > 4096 * 4096 for stream in streams):
            raise MediaError("dimensions_too_large", "This media exceeds the image dimension limit.", 413)
        return {
            "duration": duration,
            "format": info.get("format", {}).get("format_name"),
            "streams": [
                {k: stream.get(k) for k in ("codec_type", "codec_name", "width", "height", "sample_rate", "channels", "avg_frame_rate")} for stream in streams
            ],
        }
    except MediaError:
        raise
    except (ValueError, subprocess.SubprocessError, OSError) as exc:
        raise MediaError("invalid_media", "Upload a valid supported media file.", 422) from exc


def execute(arguments: list[str], directory: Path, cancelled, timeout: float, diagnostic_output: Path | None = None):
    executable = shutil.which(settings.ffmpeg_path)
    if not executable:
        raise MediaError("processing_unavailable", "Media processing is unavailable.", 503)
    # Limits are installed in a fresh Python child, never preexec_fn in a
    # threaded web process. The child then replaces itself with FFmpeg.
    command = [
        executable,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "info",
        "-nostats",
        "-y",
        "-threads",
        "1",
        "-filter_threads",
        "1",
        "-filter_complex_threads",
        "1",
        # FFmpeg codec options are scoped: apply decoder threads to EACH input
        # and encoder threads to the output, not just before the first -i.
        *[part for arg in arguments[:-1] for part in (["-threads", "1", arg] if arg == "-i" else [arg])],
        "-threads", "1", arguments[-1],
    ]
    log = diagnostic_output or directory / "diagnostic.log"
    started = time.monotonic()
    with log.open("wb") as stderr:
        process = subprocess.Popen(
            [sys.executable, "-m", "app.processing.worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=stderr,
            start_new_session=True,
            cwd=Path(__file__).resolve().parents[2],
        )
        try:
            process.stdin.write(
                json.dumps(
                    {"command": command, "bytes": settings.max_file_bytes, "seconds": max(1, int(timeout)), "cwd": str(directory.resolve())}
                ).encode()
            )
            process.stdin.close()
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                if cancelled.is_set():
                    raise MediaError("cancelled", "Processing was cancelled.", 409)
                if time.monotonic() > deadline:
                    raise MediaError("processing_timeout", "Processing took too long. Try a shorter file.", 504)
                time.sleep(0.05)
            if process.returncode:
                with log.open("rb") as details:
                    details.seek(max(0, log.stat().st_size - 65536))
                    failure = execution_failure(process.returncode, details.read().decode(errors="replace"))
                diagnostic(directory, "processing", exit_code=process.returncode, error_category=failure.code,
                           elapsed_seconds=round(time.monotonic() - started, 2))
                raise failure
            diagnostic(directory, "processing", exit_code=0, elapsed_seconds=round(time.monotonic() - started, 2))
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    if diagnostic_output is None:
        log.unlink(missing_ok=True)


def process_essential(operation: str, inputs: list[Path], options: Options, directory: Path, cancelled):
    if operation not in ESSENTIAL:
        raise MediaError("operation_unavailable", "This operation is not yet available.", 501)
    if not inputs or len(inputs) > 8 or (operation != "merger" and len(inputs) != 1):
        raise MediaError("invalid_inputs", "Choose the required input files.", 400)
    if any(not path.is_file() or path.is_symlink() for path in inputs):
        raise MediaError("invalid_media", "The uploaded file is unavailable.", 410)
    if sum(path.stat().st_size for path in inputs) > settings.max_file_bytes:
        raise MediaError("file_too_large", "The combined inputs exceed the job size limit.", 413)
    metadata = [inspect(path) for path in inputs]
    if any(not any(stream["codec_type"] == "video" for stream in item["streams"]) for item in metadata):
        raise MediaError("video_required", "This operation requires a video input.", 422)
    duration = sum(item["duration"] for item in metadata)
    if duration <= 0 or duration / options.speed > settings.max_duration_seconds:
        raise MediaError("invalid_duration", "The duration is unavailable or exceeds the processing limit.", 422)
    if options.end is not None and (options.end <= options.start or options.end > metadata[0]["duration"] + 0.05):
        raise MediaError("invalid_range", "Choose an end after the start within the video duration.", 400)
    if options.start >= metadata[0]["duration"]:
        raise MediaError("invalid_range", "Choose a start within the video duration.", 400)
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    extension = "mp3" if operation == "mp3" else "gif" if operation == "video-to-gif" else options.output_format
    output = directory / f"output.{extension}"
    try:
        codec = next(s["codec_name"] for s in metadata[0]["streams"] if s["codec_type"] == "video")
        copy_video = operation == "remove-audio" and (
            (extension in {"mp4", "mov"} and codec in {"h264", "hevc"})
            or (extension == "webm" and codec in {"vp8", "vp9", "av1"})
        )
        args = []
        for path in inputs:
            args += ["-protocol_whitelist", "file,pipe", "-format_whitelist", FORMATS, "-i", str(path)]
        audio = all(any(stream["codec_type"] == "audio" for stream in item["streams"]) for item in metadata)
        video_filter = "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1"
        if operation == "merger":
            # Normalize all segments; missing audio is rejected rather than
            # silently dropping another clip's soundtrack.
            if any(any(s["codec_type"] == "audio" for s in item["streams"]) != audio for item in metadata):
                raise MediaError("incompatible_audio", "Merge videos that either all have audio or all have no audio.", 422)
            width = min(1920, metadata[0]["streams"][0].get("width") or 640)
            height = min(1080, metadata[0]["streams"][0].get("height") or 360)
            width -= width % 2
            height -= height % 2
            parts = []
            labels = []
            for index in range(len(inputs)):
                parts.append(
                    f"[{index}:v:0]scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,setpts=PTS-STARTPTS[v{index}]"
                )
                labels.append(f"[v{index}]")
                if audio:
                    parts.append(f"[{index}:a:0]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{index}]")
                    labels.append(f"[a{index}]")
            parts.append("".join(labels) + f"concat=n={len(inputs)}:v=1:a={int(audio)}[v]" + ("[a]" if audio else ""))
            args += ["-filter_complex", ";".join(parts), "-map", "[v]"]
            if audio:
                args += ["-map", "[a]"]
        elif operation == "mp3":
            if not audio:
                raise MediaError("audio_required", "This video has no audio track.", 422)
            args += ["-map", "0:a:0", "-vn", "-c:a", "libmp3lame", "-q:a", "3"]
        elif operation == "video-to-gif":
            args += [
                "-filter_complex",
                f"fps={options.fps},scale={options.width}:-1:flags=lanczos,split[x][y];[x]palettegen[p];[y][p]paletteuse",
                "-an",
            ]
        else:
            if operation == "speed":
                video_filter += f",setpts=PTS/{options.speed}"
                if audio and options.preserve_audio:
                    args += ["-af", f"atempo={options.speed}"]
                else:
                    args += ["-an"]
            if operation == "remove-audio":
                args += ["-an"]
            args += ["-map", "0:v:0"]
            if not copy_video:
                args += ["-vf", video_filter]
            if audio and operation not in {"remove-audio", "speed"}:
                args += ["-map", "0:a:0"]
            elif audio and operation == "speed" and options.preserve_audio:
                args += ["-map", "0:a:0"]
        if operation == "trimmer":
            args += ["-ss", str(options.start), "-t", str((options.end or metadata[0]["duration"]) - options.start)]
        if operation == "video-to-gif":
            args += ["-ss", str(options.start), "-t", str((options.end or metadata[0]["duration"]) - options.start)]
        if copy_video:
            args += ["-c:v", "copy"]
            if extension in {"mp4", "mov"}:
                args += ["-movflags", "+faststart"]
        elif extension not in {"gif", "mp3"}:
            args += [
                "-c:v",
                "libvpx-vp9" if extension == "webm" else "libx264",
                "-crf",
                str(options.quality),
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "libopus" if extension == "webm" else "aac",
            ]
            if extension in {"mp4", "mov"}:
                args += ["-preset", "veryfast", "-movflags", "+faststart"]
        args += ["-map_metadata", "-1", "-map_chapters", "-1", str(output)]
        execute(args, directory, cancelled, settings.download_timeout_seconds)
        if cancelled.is_set():
            raise MediaError("cancelled", "Processing was cancelled.", 409)
        if not output.is_file() or not 0 < output.stat().st_size <= settings.max_file_bytes:
            raise MediaError("invalid_output", "No valid output was produced.", 422)
        measured = inspect(output)
        if operation == "remove-audio" and any(s["codec_type"] == "audio" for s in measured["streams"]):
            raise MediaError("invalid_output", "The output did not match the requested operation.", 422)
        os.chmod(output, 0o600)
        diagnostic(directory, "output_validation", success=True, bytes=output.stat().st_size)
        return {
            "path": str(output),
            "filename": output.name,
            "extension": extension,
            "filesize": output.stat().st_size,
            "metadata": measured,
        }
    except BaseException:
        shutil.rmtree(directory, ignore_errors=True)
        raise


def process_files(operation: str, inputs: list[Path], options: Options, directory: Path, cancelled):
    if operation in ESSENTIAL:
        return process_essential(operation, inputs, options, directory, cancelled)
    from .extended import process_extended

    return process_extended(operation, inputs, options, directory, cancelled)
