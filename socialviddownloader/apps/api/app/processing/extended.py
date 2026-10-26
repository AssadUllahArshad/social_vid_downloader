from __future__ import annotations

import json
import os
import re
import shutil
import time
import zipfile
from fractions import Fraction
from pathlib import Path

from ..config import settings
from ..media_errors import MediaError
from .engine import FORMATS, OPERATIONS, Options, diagnostic, execute, inspect


def process_extended(operation: str, inputs: list[Path], options: Options, directory: Path, cancelled):
    if operation not in OPERATIONS:
        raise MediaError("operation_unavailable", "This operation is not available.", 501)
    expected = 2 if operation in {"image-watermark", "burn-subtitles"} else None if operation == "images" else 1
    if not inputs or len(inputs) > 8 or (expected and len(inputs) != expected):
        raise MediaError("invalid_inputs", "Choose the required files in their displayed order.", 400)
    if any(not path.is_file() or path.is_symlink() for path in inputs):
        raise MediaError("file_expired", "An input expired. Upload it again.", 410)
    if sum(path.stat().st_size for path in inputs) > settings.max_file_bytes:
        raise MediaError("file_too_large", "The combined inputs exceed the job size limit.", 413)
    metadata = [inspect(path) for path in inputs]
    duration = metadata[0]["duration"]
    video = next((stream for stream in metadata[0]["streams"] if stream["codec_type"] == "video"), None)
    if not video:
        raise MediaError("video_required", "Choose a video or supported image input.", 422)
    image_codecs = {"png", "mjpeg", "gif"}
    if operation == "images" and (options.width % 2 or options.height % 2):
        raise MediaError("invalid_dimensions", "Choose even output dimensions for a video.", 400)
    if operation == "images" and any(not any(s["codec_name"] in {"png", "mjpeg"} for s in item["streams"]) for item in metadata):
        raise MediaError("image_required", "Choose PNG or JPEG images.", 422)
    if operation == "gif-to-video" and video["codec_name"] != "gif":
        raise MediaError("gif_required", "Choose an animated GIF.", 422)
    if operation not in {"images", "gif-to-video"} and (duration <= 0 or video["codec_name"] in image_codecs):
        raise MediaError("video_required", "Choose a video with a known duration.", 422)
    if operation == "image-watermark" and not any(s["codec_name"] in {"png", "mjpeg"} for s in metadata[1]["streams"]):
        raise MediaError("image_required", "Choose a PNG or JPEG watermark after the video.", 422)
    if operation == "burn-subtitles" and not any(s["codec_type"] == "subtitle" for s in metadata[1]["streams"]):
        raise MediaError("subtitle_required", "Choose a valid SRT subtitle file after the video.", 422)
    if options.start >= duration and operation not in {"images", "gif-to-video"}:
        raise MediaError("invalid_range", "Choose a timestamp within the video.", 400)
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    deadline = time.monotonic() + settings.download_timeout_seconds

    def run(args):
        if time.monotonic() >= deadline:
            raise MediaError("processing_timeout", "Processing took too long.", 504)
        execute(args, directory, cancelled, deadline - time.monotonic())

    def source(path):
        return ["-protocol_whitelist", "file,pipe", "-format_whitelist", FORMATS, "-i", str(path.resolve())]

    encode = [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        str(options.quality),
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        "-map_metadata",
        "-1",
    ]
    extension = (
        "png"
        if operation in {"thumbnail", "thumbnail-grid", "storyboard"}
        else "json"
        if operation == "information"
        else "srt"
        if operation == "extract-subtitles"
        else "zip"
        if operation == "splitter"
        else "mp4"
    )
    output = directory / f"output.{extension}"
    measured = None
    try:
        if operation == "information":
            output.write_text(json.dumps({"inputBytes": inputs[0].stat().st_size, **metadata[0]}, indent=2))
            json.loads(output.read_text())
            measured = metadata[0]
        elif operation == "splitter":
            count = int((duration + options.segment_seconds - 0.000001) // options.segment_seconds)
            # A sub-frame remainder is not an independently encodable video.
            # Keep that tail in the preceding segment instead of producing an
            # empty final file (for example 8.008 s split into 1 s intervals).
            try:
                frame_seconds = 1 / float(Fraction(video.get("avg_frame_rate") or "0/1"))
            except (ValueError, ZeroDivisionError):
                frame_seconds = 0
            if count > 1 and 0 < duration - (count - 1) * options.segment_seconds < frame_seconds:
                count -= 1
            if count < 1 or count > 32:
                raise MediaError("segment_limit", "Choose a segment duration that produces no more than 32 segments.", 400)
            parts = []
            for index in range(count):
                file = directory / f"segment-{index + 1:02d}.mp4"
                run(
                    source(inputs[0])
                    + [
                        "-ss",
                        str(index * options.segment_seconds),
                        "-t",
                        str(duration - index * options.segment_seconds if index == count - 1 else options.segment_seconds),
                        *encode,
                        str(file),
                    ]
                )
                inspect(file)
                parts.append(file)
                if sum(p.stat().st_size for p in parts) > settings.max_file_bytes:
                    raise MediaError("file_too_large", "Combined segments exceed the output limit.", 413)
            with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
                for part in parts:
                    archive.write(part, part.name)
            for part in parts:
                part.unlink()
            measured = {"segments": count}
        elif operation == "extract-subtitles":
            if not any(s["codec_type"] == "subtitle" for s in metadata[0]["streams"]):
                raise MediaError("subtitles_unavailable", "This video contains no embedded subtitles.", 422)
            run(source(inputs[0]) + ["-map", f"0:s:{options.subtitle_track}", "-c:s", "srt", str(output)])
            content = output.read_text(encoding="utf-8")
            if not re.search(r"\d\d:\d\d:\d\d,\d{3}\s+-->\s+\d\d:\d\d:\d\d,\d{3}", content):
                raise MediaError("invalid_output", "No valid text subtitle output was produced.", 422)
            measured = {"subtitleFormat": "srt"}
        elif operation in {"thumbnail", "thumbnail-grid", "storyboard"}:
            if operation == "thumbnail":
                run(source(inputs[0]) + ["-ss", str(options.start), "-frames:v", "1", "-vf", f"scale={options.width}:-1", str(output)])
            else:
                rows = (options.frames + options.columns - 1) // options.columns
                scaled_height = int(options.width * video["height"] / max(1, video["width"]))
                if options.width * options.columns > 4096 or rows * scaled_height > 4096:
                    raise MediaError("grid_too_large", "Reduce frame count, columns or thumbnail width.", 400)
                run(
                    source(inputs[0])
                    + [
                        "-vf",
                        f"fps={options.frames / duration},scale={options.width}:-1,tile={options.columns}x{rows}:nb_frames={options.frames}",
                        "-frames:v",
                        "1",
                        str(output),
                    ]
                )
            measured = inspect(output)
        elif operation == "images":
            args = []
            parts = []
            labels = []
            for index, path in enumerate(inputs):
                args += ["-loop", "1", *source(path)]
                parts.append(
                    f"[{index}:v]scale={options.width}:{options.height}:force_original_aspect_ratio=decrease,pad={options.width}:{options.height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25,trim=duration={options.image_seconds},setpts=PTS-STARTPTS[v{index}]"
                )
                labels.append(f"[v{index}]")
            parts.append("".join(labels) + f"concat=n={len(inputs)}:v=1:a=0[v]")
            run(
                args
                + [
                    "-filter_complex",
                    ";".join(parts),
                    "-map",
                    "[v]",
                    "-an",
                    "-t",
                    str(len(inputs) * options.image_seconds),
                    *encode,
                    str(output),
                ]
            )
            measured = inspect(output)
        elif operation == "trim-silence":
            if not any(s["codec_type"] == "audio" for s in metadata[0]["streams"]):
                raise MediaError("audio_required", "Silence trimming requires an audio track.", 422)
            # Detection log is local/private and deleted with the job. No raw
            # filter expression or path comes from the user.
            detect = directory / "detected.log"
            # execute writes only bounded FFmpeg diagnostics; info level enables
            # silencedetect events. Keep the shared child/resource boundary.
            from .engine import execute as execute_shared

            execute_shared(
                source(inputs[0])
                + [
                    "-loglevel",
                    "info",
                    "-af",
                    f"silencedetect=noise={options.silence_db}dB:d={options.silence_seconds}",
                    "-f",
                    "null",
                    "-",
                ],
                directory,
                cancelled,
                max(0.1, deadline - time.monotonic()),
                diagnostic_output=detect,
            )
            text = detect.read_text(errors="replace")
            events = [(kind, float(value)) for kind, value in re.findall(r"silence_(start|end):\s*([0-9.]+)", text)]
            silent = []
            start = None
            for kind, value in events:
                if kind == "start":
                    start = value
                elif start is not None:
                    silent.append((start, min(value, duration)))
                    start = None
            if start is not None:
                silent.append((start, duration))
            retained = []
            cursor = 0.0
            for start, end in silent:
                if start - cursor > 0.02:
                    retained.append((cursor, start))
                cursor = end
            if duration - cursor > 0.02:
                retained.append((cursor, duration))
            if not retained or len(retained) > 32:
                raise MediaError("silence_scope", "No audible portions remain, or more than 32 edits are required.", 422)
            pieces = []
            labels = []
            for index, (start, end) in enumerate(retained):
                pieces += [
                    f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{index}]",
                    f"[0:a:0]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{index}]",
                ]
                labels += [f"[v{index}][a{index}]"]
            pieces.append("".join(labels) + f"concat=n={len(retained)}:v=1:a=1[v][a]")
            run(source(inputs[0]) + ["-filter_complex", ";".join(pieces), "-map", "[v]", "-map", "[a]", *encode, str(output)])
            detect.unlink(missing_ok=True)
            measured = inspect(output)
        else:
            args = source(inputs[0])
            filter_string = "scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1"
            if operation == "gif-to-video":
                args += ["-an"]
            elif operation == "filters":
                filter_string += f",eq=brightness={options.brightness}:contrast={options.contrast},unsharp=5:5:{options.sharpen}:5:5:0"
            elif operation == "stabilizer":
                filter_string += ",deshake=rx=16:ry=16"
            elif operation == "text-watermark":
                if not options.text.strip() or "\x00" in options.text:
                    raise MediaError("invalid_text", "Enter nonempty watermark text without control characters.", 400)
                (directory / "watermark.txt").write_text(options.text, encoding="utf-8")
                filter_string += f",drawtext=textfile=watermark.txt:expansion=none:fontcolor=white:fontsize={options.font_size}:x=10:y=10"
            elif operation == "burn-subtitles":
                shutil.copyfile(inputs[1], directory / "subtitles.srt")
                filter_string += ",subtitles=filename=subtitles.srt"
            elif operation == "image-watermark":
                args += source(inputs[1])
                args += [
                    "-filter_complex",
                    f"[1:v]scale={min(options.width, video['width'])}:-1[mark];[0:v][mark]overlay=10:10:format=auto,scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p[v]",
                    "-map",
                    "[v]",
                    "-map",
                    "0:a?",
                ]
            if operation != "image-watermark":
                args += ["-vf", filter_string]
            run(args + encode + [str(output)])
            measured = inspect(output)
        if cancelled.is_set():
            raise MediaError("cancelled", "Processing was cancelled.", 409)
        if not output.is_file() or not 0 < output.stat().st_size <= settings.max_file_bytes:
            raise MediaError("invalid_output", "No valid output within the size limit was produced.", 422)
        for file in directory.iterdir():
            if file != output:
                file.unlink()
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
