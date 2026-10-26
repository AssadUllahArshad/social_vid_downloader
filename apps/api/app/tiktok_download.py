"""TikTok native download keeps fresh extractor cookies, headers and signed URLs together."""

import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path

from .config import settings
from .media_errors import MediaError


def native_download(record, format_id, directory, plan=None):
    selected = plan or record["selections"][format_id]
    selectors = [str(track.get("format_id", "")) for track in selected["tracks"]]
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]{1,200}", selector) for selector in selectors):
        raise MediaError("quality_unavailable", "This TikTok format cannot be selected safely. Analyze the link again.", 400)
    payload = {
        "source": record["source"],
        "selector": "+".join(selectors),
        "directory": str(directory),
        "height": selected["format"]["height"],
        "hasAudio": selected["format"]["hasAudio"],
    }
    if plan is not None:
        payload["inputs"] = [
            {
                "format_id": str(track.get("format_id", "")),
                "extension": track["ext"],
                "height": track.get("height"),
                "language": track.get("language"),
                "audio_streams": track.get("audio_streams"),
            }
            for track in selected["tracks"]
        ]
        payload["selector"] = selectors[0]
    process = subprocess.Popen(
        [sys.executable, "-m", "app.tiktok_worker"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        stdout, _ = process.communicate(json.dumps(payload).encode(), timeout=settings.download_timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise MediaError("processing_timeout", "TikTok download preparation took too long.", 504) from exc
    if process.returncode or len(stdout) > 65536:
        raise MediaError("processing_failed", "TikTok could not prepare a supported file.", 502)
    result = json.loads(stdout)
    if not result["success"]:
        failure = result["error"]
        raise MediaError(failure["code"], failure["message"], failure["status"])
    if plan is not None:
        paths = [Path(value) for value in result["paths"]]
        if len(paths) != len(plan["tracks"]):
            raise MediaError("invalid_media", "TikTok did not provide the selected tracks.", 502)
        for path, track in zip(paths, plan["tracks"]):
            if path.parent != directory or path.is_symlink() or not path.is_file() or path.suffix != "." + track["ext"]:
                raise MediaError("invalid_media", "TikTok did not provide valid selected media.", 502)
        return paths
    path = Path(result["path"])
    if path.suffix != "." + selected["format"]["extension"]:
        raise MediaError("format_changed", "The TikTok file format changed. Please submit the link again.", 410)
    if path.parent != directory or path.is_symlink() or not path.is_file():
        raise MediaError("invalid_media", "TikTok did not provide a valid file.", 502)
    return path
