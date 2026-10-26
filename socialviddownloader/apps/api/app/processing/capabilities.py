"""Actual runtime filter/encoder support, cached until the API restarts."""

import shutil
import subprocess
from functools import lru_cache

from ..config import settings
from .engine import OPERATIONS


@lru_cache(maxsize=1)
def supported_operations():
    if not shutil.which(settings.ffprobe_path):
        return set()
    executable = shutil.which(settings.ffmpeg_path)
    if not executable:
        return {"information"}
    try:
        filters = subprocess.run([executable, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=10, check=True).stdout
        encoders = subprocess.run([executable, "-hide_banner", "-encoders"], capture_output=True, text=True, timeout=10, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return {"information"}
    filter_names = {line.split()[1] for line in filters.splitlines() if len(line.split()) > 2}
    encoder_names = {line.split()[1] for line in encoders.splitlines() if len(line.split()) > 2}
    required = {
        "stabilizer": {"deshake"},
        "text-watermark": {"drawtext"},
        "burn-subtitles": {"subtitles"},
        "video-to-gif": {"palettegen", "paletteuse"},
        "trim-silence": {"silencedetect", "trim", "atrim", "concat"},
        "thumbnail-grid": {"tile"},
        "storyboard": {"tile"},
        "filters": {"eq", "unsharp"},
        "images": {"concat"},
        "image-watermark": {"overlay"},
        "speed": {"atempo", "setpts"},
    }
    available = {op for op in OPERATIONS if required.get(op, set()).issubset(filter_names)}
    if "libx264" not in encoder_names:
        available -= OPERATIONS - {"mp3", "information", "extract-subtitles", "thumbnail", "thumbnail-grid", "storyboard", "video-to-gif"}
    if "libmp3lame" not in encoder_names:
        available.discard("mp3")
    return available
