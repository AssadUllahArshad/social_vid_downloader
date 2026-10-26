import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from .audio import codec_family, download_plan, language_code, mux_language, track_label
from .config import settings
from .media_errors import MediaError, platform_name, provider_error
from .probe import inspect_file
from .transport import SafeTransport


def safe_filename(title, quality, extension, audio_tracks=None, audio_mode="single"):
    title = re.sub(r"[^a-zA-Z0-9_-]+", "-", title).strip("-_")[:80] or "video"
    labels = []
    for track in audio_tracks or []:
        label = (
            track["language_name"]
            if track["language_name"] != "Unknown"
            else "original"
            if track["is_original"]
            else "default"
            if track["is_default"]
            else "unknown"
        )
        label = re.sub(r"[^a-z0-9-]+", "-", label.lower()).strip("-")[:18]
        labels.append(label)
    suffix = "-" + "-".join(labels) if labels else ""
    if audio_mode in {"dual", "multi"}:
        suffix += "-dual-audio" if audio_mode == "dual" else "-multi-audio"
    # Leave room for up to eight tracks without exceeding common filename limits.
    return f"{title[: max(20, 190 - len(suffix))]}-{quality}p{suffix}-socialviddownloader.{extension}"


def verify_audio(measured, selection):
    expected = selection.get("selected_audio", [])
    if selection.get("audio_maps") is None:
        return  # Backward-compatible sessions still have the original audio presence check.
    videos = [s for s in measured["streams"] if s.get("codec_type") == "video"]
    audios = [s for s in measured["streams"] if s.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != len(expected):
        raise MediaError(
            "audio_mux_failed", "The prepared file does not contain the selected audio tracks. Please try another selection.", 502
        )
    for index, (stream, track) in enumerate(zip(audios, expected)):
        wanted = mux_language(track["language_code"])
        if track["language_code"] and stream.get("tags", {}).get("language") != wanted:
            raise MediaError("audio_mux_failed", "The selected audio language could not be preserved. Please try another selection.", 502)
        if codec_family(stream.get("codec_name")) != codec_family(track["codec"]):
            raise MediaError("audio_mux_failed", "The selected audio format changed. Please analyze the video again.", 502)
        if len(expected) > 1 and bool(stream.get("disposition", {}).get("default")) != (index == 0):
            raise MediaError("audio_mux_failed", "The primary audio track could not be preserved. Please try again.", 502)


def generate_file(record, format_id, directory, audio_mode="single", audio_track_ids=None):
    selection = download_plan(record, format_id, audio_mode, audio_track_ids)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    deadline = time.monotonic() + settings.download_timeout_seconds
    total = 0
    tracks = []
    try:
        native = record.get("downloadStrategy") == "yt_dlp" and record["platform"] == "tiktok"
        if native:
            from .tiktok_download import native_download

            tracks.extend(native_download(record, format_id, directory, selection))
        for index, track in enumerate([] if native else selection["tracks"]):
            target = directory / f"track-{index}.{track['ext']}"
            remaining = max(1, deadline - time.monotonic())
            transport = SafeTransport(record["platform"], max_bytes=settings.max_file_bytes, timeout=min(20, remaining))
            body, _, status, _ = transport.open(track["url"], headers=track.get("http_headers"))
            if status >= 400:
                body.close()
                if status in {401, 403}:
                    raise MediaError(
                        "platform_access_restricted",
                        f"{platform_name(record['platform'])} could not provide access to this video. Please try another public link later.",
                        502,
                    )
                if status == 429:
                    raise MediaError("platform_rate_limited", "The source is limiting media requests. Please try later.", 429)
                raise MediaError("source_expired", "The source link expired or became unavailable. Analyze the video again.", 410)
            try:
                with target.open("wb") as output:
                    while True:
                        if time.monotonic() > deadline:
                            raise MediaError("processing_timeout", "Download preparation took too long.", 504)
                        chunk = body.read(256 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > settings.max_file_bytes:
                            raise MediaError("file_too_large", "This video exceeds the file size limit.", 413)
                        output.write(chunk)
            finally:
                body.close()
            if target.stat().st_size == 0:
                raise MediaError("empty_file", "The source returned an empty file.", 502)
            tracks.append(target)
        fmt = selection["format"]
        chosen = selection["selected_audio"]
        filename = safe_filename(record["metadata"]["title"], fmt["height"], fmt["extension"], chosen, selection["audio_mode"])
        result = directory / filename
        # Ordinary combined videos remain a file move, unless language metadata needs writing.
        passthrough = selection.get("passthrough") and not any(
            t["language_code"] or t["is_original"] or t["is_descriptive"] or t["is_dubbed"] for t in chosen
        )
        if len(tracks) == 1 and (selection["audio_maps"] is None or passthrough):
            tracks[0].rename(result)
        else:
            ffmpeg = shutil.which(settings.ffmpeg_path)
            if not ffmpeg:
                raise MediaError("merge_unavailable", "Audio and video cannot be combined right now. Please try again later.", 503)
            inputs_measured = {}
            for track, (input_index, audio_index) in zip(chosen, selection["audio_maps"] or []):
                if input_index not in inputs_measured:
                    inputs_measured[input_index] = inspect_file(
                        tracks[input_index], require_video=False, timeout=max(1, min(12, deadline - time.monotonic()))
                    )
                input_audio = [s for s in inputs_measured[input_index]["streams"] if s.get("codec_type") == "audio"]
                if audio_index >= len(input_audio):
                    raise MediaError("audio_track_unavailable", "The source audio tracks changed. Please analyze the video again.", 410)
                stream = input_audio[audio_index]
                actual_language = language_code(stream.get("tags", {}).get("language"))
                expected_language = track["language_code"]
                if (
                    actual_language
                    and expected_language
                    and actual_language.split("-")[0] != expected_language.split("-")[0]
                    or codec_family(stream.get("codec_name")) != codec_family(track["codec"])
                ):
                    raise MediaError("audio_track_unavailable", "The selected source audio changed. Please analyze the video again.", 410)
            command = [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
            for track in tracks:
                command += ["-protocol_whitelist", "file,pipe", "-format_whitelist", "mov,matroska,webm,ogg", "-i", str(track)]
            command += ["-map", "0:v:0"]
            mappings = selection["audio_maps"] if selection["audio_maps"] is not None else [(1, 0)]
            for input_index, stream_index in mappings:
                command += ["-map", f"{input_index}:a:{stream_index}"]
            command += ["-c", "copy"]
            for index, track in enumerate(chosen):
                flags = (["default"] if index == 0 else []) + (["original"] if track["is_original"] else [])
                flags += (["visual_impaired"] if track["is_descriptive"] else []) + (["dub"] if track["is_dubbed"] else [])
                command += [
                    f"-metadata:s:a:{index}",
                    f"language={mux_language(track['language_code']) or 'und'}",
                    f"-metadata:s:a:{index}",
                    f"title={track['label']}",
                    f"-metadata:s:a:{index}",
                    f"handler_name={track['label']}",
                    f"-disposition:a:{index}",
                    "+".join(flags) or "0",
                ]
            if fmt["extension"] == "mp4":
                command += ["-movflags", "+faststart"]
            command += [str(result)]
            try:
                subprocess.run(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=max(1, deadline - time.monotonic()),
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise MediaError(
                    "audio_mux_failed" if chosen else "merge_failed",
                    "The video and selected audio could not be combined. Try another available selection.",
                    502,
                ) from exc
            for track in tracks:
                track.unlink()
        size = result.stat().st_size
        if not size or size > settings.max_file_bytes:
            raise MediaError("file_too_large", "The prepared video exceeds the file size limit.", 413)
        measured = inspect_file(result)
        duration = float(measured.get("format", {}).get("duration") or 0)
        if duration > settings.max_duration_seconds:
            raise MediaError("video_too_long", "This video exceeds the duration limit.", 413)
        video = next(s for s in measured["streams"] if s.get("codec_type") == "video")
        if (
            video.get("height") != fmt["height"]
            or (fmt.get("width") and video.get("width") != fmt["width"])
            or fmt["hasAudio"]
            and not any(s.get("codec_type") == "audio" for s in measured["streams"])
        ):
            raise MediaError("format_changed", "The source format changed. Analyze this link again.", 410)
        verify_audio(measured, selection)
        output_audio = []
        for track, stream in zip(chosen, [s for s in measured["streams"] if s.get("codec_type") == "audio"]):
            output_track = {**track, "is_default": bool(stream.get("disposition", {}).get("default"))}
            output_track["label"] = track_label(output_track, len(chosen) == 1)
            output_audio.append(output_track)
        os.chmod(result, 0o600)
        return {
            "path": str(result),
            "filename": filename,
            "filesize": size,
            "extension": fmt["extension"],
            "audio_mode": selection["audio_mode"],
            "audio_tracks": output_audio,
        }
    except Exception as exc:
        shutil.rmtree(directory, ignore_errors=True)
        if isinstance(exc, MediaError):
            raise
        raise provider_error(exc, record["platform"]) from exc
