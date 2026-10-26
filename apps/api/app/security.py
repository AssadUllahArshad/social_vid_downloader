import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

from .media_errors import platform_name

HOSTS = {
    "youtube.com": "youtube",
    "www.youtube.com": "youtube",
    "m.youtube.com": "youtube",
    "youtu.be": "youtube",
    "instagram.com": "instagram",
    "www.instagram.com": "instagram",
    "facebook.com": "facebook",
    "www.facebook.com": "facebook",
    "m.facebook.com": "facebook",
    "fb.watch": "facebook",
    "tiktok.com": "tiktok",
    "www.tiktok.com": "tiktok",
    "vm.tiktok.com": "tiktok",
    "vt.tiktok.com": "tiktok",
    "snapchat.com": "snapchat",
    "www.snapchat.com": "snapchat",
}


class InvalidUrl(ValueError):
    pass


def validate_url(value: str) -> tuple[str, str]:
    if len(value) > 2048 or any(ord(c) < 33 for c in value):
        raise InvalidUrl("Use a complete video link without whitespace.")
    try:
        url = urlsplit(value)
        host = (url.hostname or "").lower()
        if url.scheme not in {"https", "http"} or url.username or url.password or url.port not in {None, 80, 443}:
            raise InvalidUrl("Only public HTTP or HTTPS links are accepted.")
        if host not in HOSTS:
            raise InvalidUrl("This website is not supported. Choose a listed platform.")
        if "\\" in value or "%" in url.netloc:
            raise InvalidUrl("This link has an invalid host.")
        return urlunsplit((url.scheme, host, url.path or "/", url.query, "")), HOSTS[host]
    except ValueError as exc:
        if isinstance(exc, InvalidUrl):
            raise
        raise InvalidUrl("Enter a valid public video URL.") from exc


def public_destination(url: str, resolver=socket.getaddrinfo) -> tuple[str, ...]:
    """Validate every address before future outbound requests; never fetch here."""
    normalized, _ = validate_url(url)
    host = urlsplit(normalized).hostname
    records = resolver(host, 443, type=socket.SOCK_STREAM)
    addresses = tuple(sorted({record[4][0] for record in records}))
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise InvalidUrl("This link resolves to a restricted network address.")
    return addresses


def validate_media_url(value: str, expected_platform=None, expected_type=None):
    import re
    from urllib.parse import parse_qs

    normalized, platform = validate_url(value)
    url = urlsplit(normalized)
    path = url.path
    host = url.hostname
    kind = "video"
    if platform == "youtube":
        if host == "youtu.be":
            valid = bool(re.fullmatch(r"/[A-Za-z0-9_-]{11}/?", path))
        elif re.fullmatch(r"/shorts/[A-Za-z0-9_-]{11}/?", path):
            valid, kind = True, "shorts"
        else:
            valid = path.rstrip("/") == "/watch" and bool(re.fullmatch(r"[A-Za-z0-9_-]{11}", parse_qs(url.query).get("v", [""])[0]))
    elif platform == "instagram":
        match = re.fullmatch(r"/(p|reel|reels|stories)/([^/]+)(?:/([0-9]+))?/?", path)
        valid = bool(match)
        if match:
            kind = "story" if match[1] == "stories" else "reels" if match[1] in {"reel", "reels"} else "video"
    elif platform == "facebook":
        valid = bool(host == "fb.watch" and re.fullmatch(r"/[A-Za-z0-9_-]+/?", path))
        if re.fullmatch(r"/reel/[0-9]+/?", path):
            valid, kind = True, "reels"
        valid = (
            valid
            or bool(re.search(r"/videos/(?:[^/]+/)?[0-9]+/?$", path))
            or (path.rstrip("/") in {"/watch", "/video.php", "/story.php"} and any(parse_qs(url.query).get(k) for k in ["v", "story_fbid"]))
            or bool(re.fullmatch(r"/share/(v|r)/[A-Za-z0-9]+/?", path))
        )
    elif platform == "tiktok":
        valid = bool(
            re.fullmatch(r"/@[^/]+/video/[0-9]+/?", path)
            or host in {"vm.tiktok.com", "vt.tiktok.com"}
            and re.fullmatch(r"/[A-Za-z0-9]+/?", path)
            or re.fullmatch(r"/t/[A-Za-z0-9]+/?", path)
        )
    elif platform == "snapchat":
        valid = False
        for pattern, content in [
            (r"/(?:@[A-Za-z0-9_.-]+/)?spotlight/[A-Za-z0-9_-]+/?", "spotlight"),
            (r"/t/[A-Za-z0-9_-]+/?", "shared"),
            (r"/stories/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_-]+)?/?", "story"),
            (r"/@[A-Za-z0-9_.-]+/story/[A-Za-z0-9_-]+/?", "story"),
            (r"/(?:add/|@)[A-Za-z0-9_.-]+/?", "profile"),
        ]:
            if re.fullmatch(pattern, path):
                valid, kind = True, content
                break
    else:
        valid = True
    if not valid:
        raise InvalidUrl(f"Use an individual {platform_name(platform)} video link, not a profile, feed, or playlist.")
    if expected_platform and expected_platform != platform:
        raise InvalidUrl(f"Use a {platform_name(expected_platform)} link with this tool.")
    if (
        expected_type
        and expected_type != kind
        and host not in {"youtu.be", "fb.watch", "vm.tiktok.com", "vt.tiktok.com"}
        and "/share/" not in path
        and kind != "shared"
        and not (platform == "snapchat" and kind in {"story", "profile"})
    ):
        raise InvalidUrl("This link is for a different content type. Please choose the matching tool.")
    return normalized, platform, kind
