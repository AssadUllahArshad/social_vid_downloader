import hashlib

from .audio import AUDIO_EXTENSIONS, audio_catalog, audio_options, default_audio_id, has_dual_audio
from .media_errors import MediaError


def normalize(info, max_bytes, merge_available=True, platform=None):
    if info.get("is_live") or info.get("live_status") == "is_live":
        raise MediaError("live_unsupported", "Live streams are not supported. Wait until the broadcast has finished.")
    raw = info.get("formats") or ([info] if info.get("url") else [])
    safe = [
        f
        for f in raw
        if f.get("url")
        and not f.get("has_drm")
        and f.get("protocol", "https") in {"http", "https"}
        and f.get("ext") in AUDIO_EXTENSIONS
        and not (f.get("filesize") and f["filesize"] > max_bytes)
    ]
    catalog = audio_catalog(safe, platform)
    choices = {}
    for f in safe:
        height = f.get("height")
        if not isinstance(height, (int, float)) or height <= 0 or f.get("vcodec") in {None, "none"}:
            continue
        if f.get("ext") not in {"mp4", "webm"}:
            continue
        options = audio_options(f, catalog, merge_available)
        default = default_audio_id(options)
        option = options.get(default)
        has_audio = bool(option)
        audio_source = option["source"] if option else None
        merged = audio_source and (audio_source.get("url"), audio_source.get("format_id")) != (f.get("url"), f.get("format_id"))
        if not options and (f.get("acodec") != "none" or catalog):
            continue  # Unknown or incompatible audio must never be advertised as silent media.
        exact = f.get("filesize")
        estimate = f.get("filesize_approx")
        if merged:
            video_size = exact or estimate
            audio_size = audio_source.get("filesize") or audio_source.get("filesize_approx")
            estimate = video_size + audio_size if video_size and audio_size else None
            exact = None
        if (
            option
            and not merged
            and (
                option["container"] != f["ext"]
                or len(f.get("audio_streams") or [{}]) > 1
                or option["track"]["language_code"]
                or option["track"]["is_original"]
                or option["track"]["is_descriptive"]
                or option["track"]["is_dubbed"]
            )
        ):
            estimate = exact or estimate
            exact = None
        selector = str(f.get("format_id", ""))
        if merged:
            selector += "+" + str(audio_source.get("format_id", ""))
        if not selector:
            continue
        token = hashlib.sha256(selector.encode()).hexdigest()[:20]
        extension = option["container"] if option else f["ext"]
        quality = f"{int(height)}p"
        width = f.get("width")
        if isinstance(width, (int, float)) and width >= height * 16 / 9:
            quality += {720: " HD", 1080: " Full HD", 1440: " QHD", 2160: " 4K"}.get(int(height), "")
        public = {
            "id": token,
            "quality": quality,
            "height": int(height),
            "width": f.get("width"),
            "extension": extension,
            "filesize": exact,
            "estimatedFilesize": estimate if not exact else None,
            "hasAudio": has_audio,
            "hasVideo": True,
            "requiresMerge": bool(merged),
            "videoCodec": f.get("vcodec"),
            "audioCodec": audio_source.get("acodec") if audio_source else "none",
            "audio_track_ids": list(options),
            "default_audio_track_id": default,
            "audio_containers": {key: option["container"] for key, option in options.items()},
        }
        selection = {
            "format": public,
            "video": f,
            "tracks": [f] + ([audio_source] if merged else []),
            "audio_options": options,
            "merge_available": merge_available,
        }
        public["supports_dual_audio"] = has_dual_audio(selection)
        rank = (extension == "mp4", str(f.get("vcodec", "")).startswith(("avc", "h264")), has_audio, f.get("tbr") or 0)
        key = int(height)
        if key not in choices or rank > choices[key][0]:
            choices[key] = (rank, public, selection)
    if not choices:
        raise MediaError(
            "no_supported_formats", "No supported download formats are available for this video. Please try another public video."
        )
    ordered = [choices[k] for k in sorted(choices, reverse=True)]
    return [c[1] for c in ordered], {c[1]["id"]: c[2] for c in ordered}
