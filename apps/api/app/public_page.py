"""Fallback for video data explicitly embedded in the submitted PUBLIC page.

Only JSON objects identifying the requested video are considered. No JS is
executed, login flows are not followed, and every format is measured locally.
"""

import json
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlsplit

from .media_errors import MediaError
from .probe import fill_missing_formats
from .transport import SafeTransport

VIDEO_FIELDS = {
    "playable_url",
    "playable_url_quality_hd",
    "browser_native_hd_url",
    "browser_native_sd_url",
    "progressive_url",
    "video_url",
    "contentUrl",
}


class PublicPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.scripts = []
        self.buffer = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            self.meta[attrs.get("property", attrs.get("name", ""))] = attrs.get("content", "")
        if tag == "script" and attrs.get("type") in {"application/json", "application/ld+json"}:
            self.buffer = []

    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.buffer is not None:
            try:
                self.scripts.append(json.loads("".join(self.buffer)))
            except ValueError:
                pass
            self.buffer = None


def identity(url):
    parsed = urlsplit(url)
    return parse_qs(parsed.query).get("v", [parsed.path.rstrip("/").split("/")[-1]])[0]


def nodes(data, target=None):
    stack = [data]
    count = 0
    while stack and count < 50000:
        current = stack.pop()
        count += 1
        if isinstance(current, dict):
            if (
                target
                and current is not data
                and current.get("__typename") in {"Video", "GraphVideo", "XDTGraphVideo"}
                and not any(str(current.get(key, "")) == target for key in ["id", "shortcode", "code"])
            ):
                continue
            if target and any(current.get(key) and str(current[key]) != target for key in ["shortcode", "video_id"]):
                continue
            yield current
            stack.extend(v for v in current.values() if isinstance(v, (dict, list)))
        elif isinstance(current, list):
            stack.extend(v for v in current if isinstance(v, (dict, list)))


def public_video_info(url, platform):
    from yt_dlp.utils.networking import std_headers

    body, headers, status, final = SafeTransport(platform).open(url, headers=dict(std_headers))
    try:
        if status != 200 or "html" not in headers.get("Content-Type", ""):
            raise MediaError("public_metadata_unavailable", "The public page did not provide video data.")
        if any(part in urlsplit(final).path for part in ["/login", "/accounts/", "/consent"]):
            raise MediaError("authentication_required", "This video requires an account or consent confirmation and cannot be processed.")
        page = PublicPage()
        page.feed(body.read().decode("utf-8", "replace"))
    finally:
        body.close()
    target = identity(final)
    candidates = []
    creator = None
    for script in page.scripts:
        for node in nodes(script):
            if not any(str(node.get(key, "")) == target for key in ["id", "video_id", "shortcode", "code"]):
                continue
            owner = node.get("owner") or node.get("user")
            if isinstance(owner, dict):
                creator = owner.get("username") or owner.get("name") or owner.get("full_name") or creator
            for item in nodes(node, target=target):
                for key in VIDEO_FIELDS:
                    value = item.get(key)
                    if isinstance(value, str) and value.startswith(("https://", "http://")):
                        candidates.append(value)
                for video in item.get("video_versions", []) if isinstance(item.get("video_versions"), list) else []:
                    if isinstance(video, dict) and isinstance(video.get("url"), str):
                        candidates.append(video["url"])
    # Do not fall back to unrelated videos, recommendations, or a URL guessed from a title.
    candidates = list(dict.fromkeys(candidates))[:8]
    if not candidates:
        raise MediaError("public_metadata_unavailable", "No media belonging to the requested video was provided publicly.")
    info = {
        "title": page.meta.get("og:title") or "Untitled video",
        "thumbnail": page.meta.get("og:image"),
        "uploader": creator,
        "formats": [
            {"format_id": f"public-{index}", "url": candidate, "ext": "mp4", "protocol": "https", "http_headers": dict(std_headers)}
            for index, candidate in enumerate(candidates)
        ],
    }
    fill_missing_formats(info, platform)
    info["formats"] = [f for f in info["formats"] if f.get("height") and f.get("vcodec")]
    if not info["formats"]:
        raise MediaError("public_metadata_unavailable", "Public media formats could not be verified.")
    return info
