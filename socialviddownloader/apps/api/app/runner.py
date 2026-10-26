import json
import os
import signal
import subprocess
import sys

from .config import settings
from .media_errors import MediaError


def isolated_extract(url, platform):
    process = subprocess.Popen(
        [sys.executable, "-m", "app.extract_worker"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        stdout, _ = process.communicate(json.dumps({"url": url, "platform": platform}).encode(), timeout=settings.extract_timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        raise MediaError("processing_timeout", "Analysis took too long. The platform may be unavailable.", 504) from exc
    if process.returncode or len(stdout) > 2 * 1024 * 1024:
        raise MediaError("extraction_failed", "The video could not be analyzed safely.", 502)
    try:
        result = json.loads(stdout)
    except ValueError as exc:
        raise MediaError("extraction_failed", "Video information could not be read. Please try another public link.", 502) from exc
    if not result["success"]:
        failure = result["error"]
        raise MediaError(failure["code"], failure["message"], failure["status"])
    return result["record"]
