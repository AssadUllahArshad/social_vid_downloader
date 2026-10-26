"""Source audio inventory and session-bound mux plans, shared by every provider."""

import hashlib
import re

from yt_dlp.utils import ISO639Utils

from .media_errors import MediaError

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ar": "Arabic",
    "es": "Spanish",
    "fr": "French",
    "pt": "Portuguese",
    "id": "Indonesian",
    "bn": "Bengali",
    "ur": "Urdu",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "tr": "Turkish",
    "it": "Italian",
    "ru": "Russian",
    "zh": "Chinese",
    "nl": "Dutch",
    "pl": "Polish",
    "ta": "Tamil",
    "te": "Telugu",
    "vi": "Vietnamese",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "mr": "Marathi",
    "th": "Thai",
}
LANGUAGE_ALIASES = {"fre": "fr", "ger": "de", "chi": "zh", "dut": "nl", "in": "id", "iw": "he"}
AUDIO_EXTENSIONS = {"m4a", "mp4", "webm", "ogg", "opus"}


def language_code(value):
    """Normalize an actual source code. Unknown/invalid metadata stays unknown."""
    if not isinstance(value, str):
        return None
    value = value.strip().replace("_", "-").lower()
    value = re.sub(r"-desc$", "", value)
    if not re.fullmatch(r"[a-z]{2,3}(?:-[a-z0-9]{2,8})*", value) or value in {"und", "unk", "zxx", "mul"}:
        return None
    parts = value.split("-")
    parts[0] = LANGUAGE_ALIASES.get(parts[0], ISO639Utils.long2short(parts[0]) or parts[0])
    return "-".join(parts)


def mux_language(code):
    if not code:
        return "und"
    base = code.split("-")[0]
    return (ISO639Utils.short2long(base) or "und") if len(base) == 2 else base


def codec_family(codec):
    value = str(codec or "").lower()
    for family, prefixes in {
        "aac": ("aac", "mp4a"),
        "h264": ("h264", "avc"),
        "hevc": ("hevc", "h265", "hev", "hvc"),
        "mpeg4": ("mpeg4", "mp4v"),
        "av1": ("av01", "av1"),
        "vp9": ("vp09", "vp9"),
        "vp8": ("vp8",),
        "opus": ("opus",),
        "vorbis": ("vorbis",),
        "mp3": ("mp3",),
        "alac": ("alac",),
        "ac3": ("ac3", "ac-3"),
        "eac3": ("eac3", "ec-3"),
        "flac": ("flac",),
    }.items():
        if value.startswith(prefixes):
            return family
    return value


def output_container(video, audios):
    """Conservative stream-copy choices; never silently transcode an audio track."""
    vcodec = codec_family(video.get("vcodec"))
    codecs = {codec_family(a.get("acodec")) for a in audios}
    if vcodec in {"h264", "hevc", "av1", "mpeg4"} and codecs <= {"aac", "mp3", "alac", "ac3", "eac3"}:
        return "mp4"
    if vcodec in {"vp8", "vp9", "av1"} and codecs <= {"opus", "vorbis"}:
        return "webm"
    if vcodec in {"h264", "hevc", "av1", "vp8", "vp9", "mpeg4"} and codecs <= {
        "aac",
        "opus",
        "vorbis",
        "mp3",
        "alac",
        "ac3",
        "eac3",
        "flac",
    }:
        return "mkv"
    raise MediaError(
        "unsupported_container", "These video and audio tracks cannot be combined safely. Choose another quality or audio track.", 400
    )


def audio_catalog(formats, platform=None):
    groups = {}
    known_audio = any(
        language_code(fmt.get("language"))
        or any(language_code(stream.get("language") or stream.get("tags", {}).get("language")) for stream in fmt.get("audio_streams", []))
        for fmt in formats
    )
    for fmt in formats:
        if fmt.get("acodec") in {None, "none"}:
            continue
        # FFprobe may expose multiple selectable streams inside a combined source.
        streams = fmt.get("audio_streams") or [{}]
        if (
            known_audio
            and not fmt.get("audio_streams")
            and not language_code(fmt.get("language"))
            and fmt.get("vcodec") not in {None, "none"}
            and not fmt.get("audio_track_id")
        ):
            continue  # Untagged progressive variants cannot prove an additional language.
        for index, stream in enumerate(streams):
            tags = stream.get("tags", {})
            disposition = stream.get("disposition", {})
            # Format-level metadata describes its first audio stream, not every embedded stream.
            format_metadata = fmt if index == 0 else {}
            note = str(stream.get("title") or tags.get("title") or format_metadata.get("format_note") or "")
            raw_language = stream.get("language") or tags.get("language") or format_metadata.get("language")
            code = language_code(raw_language)
            original = stream.get("is_original") is True or format_metadata.get("is_original") is True or bool(disposition.get("original"))
            default = stream.get("is_default") is True or format_metadata.get("is_default") is True or bool(disposition.get("default"))
            descriptive = (
                bool(disposition.get("visual_impaired"))
                or stream.get("is_descriptive") is True
                or format_metadata.get("is_descriptive") is True
            )
            dubbed = bool(disposition.get("dub")) or stream.get("is_dubbed") is True or format_metadata.get("is_dubbed") is True
            if platform == "youtube":
                original = original or format_metadata.get("language_preference") == 10
                default = default or format_metadata.get("language_preference") == 5
                descriptive = descriptive or format_metadata.get("language_preference") == -10
            original = original or bool(re.search(r"\boriginal\b", note, re.I))
            default = default or bool(re.search(r"\bdefault\b", note, re.I))
            descriptive = (
                descriptive or bool(re.search(r"\bdescriptive\b|audio description", note, re.I)) or str(raw_language).endswith("-desc")
            )
            dubbed = dubbed or bool(re.search(r"\bdubbed\b", note, re.I))
            role = "descriptive" if descriptive else "dubbed" if dubbed else "main"
            # Missing language metadata does not mean each codec/bitrate is another language.
            identity = code or str(
                stream.get("id") or fmt.get("audio_track_id") or (f"embedded-{index}" if len(streams) > 1 else "unknown")
            )
            key = (identity, role)
            if key not in groups:
                groups[key] = {
                    "id": hashlib.sha256(("source-audio:" + ":".join(key)).encode()).hexdigest()[:20],
                    "language_code": code,
                    "language_name": LANGUAGE_NAMES.get((code or "").split("-")[0], "Unknown"),
                    "is_default": False,
                    "is_original": False,
                    "is_descriptive": descriptive,
                    "is_dubbed": dubbed,
                    "origin": "source",
                    "sources": [],
                }
            group = groups[key]
            group["is_default"] |= default
            group["is_original"] |= original
            source = {
                **fmt,
                "audio_stream_index": index,
                "acodec": stream.get("codec") or stream.get("codec_name") or format_metadata.get("acodec"),
            }
            bitrate = stream.get("bitrate") or stream.get("bit_rate")
            if not bitrate and isinstance(format_metadata.get("abr"), (int, float)):
                bitrate = round(format_metadata["abr"] * 1000)
            source["audio_bitrate"] = int(bitrate) if str(bitrate).isdigit() and int(bitrate) > 0 else None
            group["sources"].append(source)
    result = list(groups.values())
    for track in result:
        track["label"] = track_label(track, len(result) == 1)
    return result


def track_label(track, single_track=False):
    name = track["language_name"]
    if name == "Unknown":
        name = "Original" if track["is_original"] or single_track else "Default" if track["is_default"] else "Unknown"
    code = track["language_code"]
    if code and "-" in code and name not in {"Original", "Default"}:
        region = {"zh-hans": "Simplified", "zh-hant": "Traditional"}.get(code, code)
        name += f" ({region})"
    elif name == "Unknown" and code:
        name += f" ({code})"
    qualifiers = []
    if track["is_original"] and name != "Original":
        qualifiers.append("Original")
    if track["is_default"] and name != "Default":
        qualifiers.append("Default")
    if track["is_descriptive"]:
        qualifiers.append("Audio description")
    if track["is_dubbed"]:
        qualifiers.append("Dubbed")
    return name + (" · " + ", ".join(qualifiers) if qualifiers else "")


def audio_options(video, catalog, merge_available=True):
    options = {}
    for group in catalog:
        candidates = []
        for source in group["sources"]:
            same = source.get("url") == video.get("url") and source.get("format_id") == video.get("format_id")
            if not merge_available and (not same or len(video.get("audio_streams") or [{}]) > 1):
                continue
            try:
                container = output_container(video, [source]) if merge_available else video["ext"]
            except MediaError:
                continue
            # Some providers expose alternate audio only inside combined video files.
            # Fetch the smallest such video instead of pulling an HD copy for its audio.
            candidates.append(
                (
                    container == "mp4",
                    same,
                    source.get("vcodec") == "none",
                    -(source.get("height") or 0),
                    source.get("audio_bitrate") or 0,
                    source,
                )
            )
        if not candidates:
            continue
        source = max(candidates, key=lambda row: row[:-1])[-1]
        public = {k: v for k, v in group.items() if k != "sources"}
        public.update(codec=source["acodec"], bitrate=source["audio_bitrate"])
        options[group["id"]] = {
            "track": public,
            "source": source,
            "container": output_container(video, [source]) if merge_available else video["ext"],
        }
    return options


def default_audio_id(options):
    return (
        next((key for key, value in options.items() if value["track"]["is_default"]), None)
        or next((key for key, value in options.items() if value["track"]["is_original"]), None)
        or next(iter(options), None)
    )


def distinct_audio(tracks):
    codes = [t["language_code"].split("-")[0] for t in tracks if t["language_code"]]
    return len(codes) == len(set(codes))


def has_dual_audio(selection):
    options = list(selection.get("audio_options", {}).values())
    if not selection.get("merge_available", True):
        return False
    for i, first in enumerate(options):
        for second in options[i + 1 :]:
            if distinct_audio([first["track"], second["track"]]):
                try:
                    output_container(selection["video"], [first["source"], second["source"]])
                    return True
                except MediaError:
                    pass
    return False


def public_audio(selections):
    tracks = {}
    for selection in selections.values():
        for key, option in selection.get("audio_options", {}).items():
            tracks.setdefault(key, option["track"])
    ordered = sorted(tracks.values(), key=lambda track: (not track["is_default"], not track["is_original"]))
    return {"audio_tracks": ordered, "supports_dual_audio": any(has_dual_audio(s) for s in selections.values())}


def download_plan(record, format_id, audio_mode="single", audio_track_ids=None):
    selection = record["selections"].get(format_id)
    if not selection:
        raise MediaError("quality_unavailable", "The requested quality is not available.", 400)
    options = selection.get("audio_options", {})
    ids = audio_track_ids if audio_track_ids is not None else ([selection["format"].get("default_audio_track_id")] if options else [])
    if audio_mode not in {"single", "dual", "multi"} or (audio_mode == "single" and len(ids) > 1):
        raise MediaError("invalid_audio_selection", "Choose one audio track for Single Audio.", 400)
    if audio_mode in {"dual", "multi"} and not selection.get("merge_available", True):
        raise MediaError("dual_audio_not_supported", "Multiple audio tracks cannot be prepared right now. Use Single Audio.", 400)
    if audio_mode in {"dual", "multi"} and not has_dual_audio(selection):
        raise MediaError("dual_audio_not_supported", "This video does not expose compatible alternate audio tracks. Use Single Audio.", 400)
    if audio_mode == "dual" and len(ids) != 2:
        raise MediaError("second_audio_track_unavailable", "Choose an available secondary audio track.", 400)
    if audio_mode == "multi" and not 2 <= len(ids) <= 8:
        raise MediaError("invalid_audio_selection", "Choose between two and eight available audio tracks.", 400)
    if len(ids) != len(set(ids)):
        raise MediaError("duplicate_audio_track", "Choose different audio tracks for each selection.", 400)
    if options and not ids:
        raise MediaError("audio_track_unavailable", "Choose an available audio track.", 400)
    for index, identifier in enumerate(ids):
        if identifier not in options:
            code = "second_audio_track_unavailable" if index == 1 else "audio_track_unavailable"
            raise MediaError(code, "The selected audio track is unavailable. Analyze the video again.", 400)
    chosen = [options[key] for key in ids]
    if not distinct_audio([o["track"] for o in chosen]):
        raise MediaError("duplicate_audio_language", "Choose different audio languages for a multilingual download.", 400)
    if not options:
        # Existing short-lived sessions and silent videos still use their proven path.
        return {**selection, "audio_mode": "single", "selected_audio": [], "audio_maps": None}
    video = selection["video"]
    inputs = [video]
    mappings = []
    for option in chosen:
        source = option["source"]
        index = next(
            (
                i
                for i, item in enumerate(inputs)
                if item.get("url") == source.get("url") and item.get("format_id") == source.get("format_id")
            ),
            None,
        )
        if index is None:
            index = len(inputs)
            inputs.append(source)
        mappings.append((index, source["audio_stream_index"]))
    extension = output_container(video, [o["source"] for o in chosen])
    fmt = {**selection["format"], "extension": extension, "hasAudio": bool(chosen), "requiresMerge": len(inputs) > 1}
    return {
        **selection,
        "format": fmt,
        "tracks": inputs,
        "selected_audio": [
            {
                **o["track"],
                "source_is_default": o["track"]["is_default"],
                "is_default": index == 0,
                "label": track_label({**o["track"], "is_default": index == 0}, len(chosen) == 1),
            }
            for index, o in enumerate(chosen)
        ],
        "audio_mode": audio_mode,
        "audio_maps": mappings,
        "passthrough": len(inputs) == 1
        and mappings == [(0, 0)]
        and len(video.get("audio_streams") or [{}]) == 1
        and extension == video["ext"],
    }
