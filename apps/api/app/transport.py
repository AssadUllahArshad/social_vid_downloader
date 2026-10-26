"""Pinned outbound transport: validate hostname and EVERY DNS address/redirect.

No system proxies, arbitrary URLs, browser cookies, or fallback networking.
"""

import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit
from urllib.request import Request

from .media_errors import MediaError

DOMAINS = {
    "snapchat": ("snapchat.com", "sc-cdn.net"),
    "youtube": ("youtube.com", "youtu.be", "youtube-nocookie.com", "googlevideo.com", "ytimg.com", "ggpht.com"),
    "facebook": ("facebook.com", "fb.watch", "fbcdn.net", "fbsbx.com"),
    "instagram": ("instagram.com", "cdninstagram.com", "fbcdn.net"),
    "tiktok": (
        "tiktok.com",
        "tiktokcdn.com",
        "tiktokcdn-us.com",
        "tiktokv.com",
        "tiktokv.us",
        "byteoversea.com",
        "ibytedtos.com",
        "ibyteimg.com",
        "muscdn.com",
        "musical.ly",
    ),
}


def destination(url, platform, resolver=None):
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    try:
        allowed = parsed.scheme in {"http", "https"} and not parsed.username and not parsed.password and parsed.port in {None, 80, 443}
    except ValueError:
        allowed = False
    if (
        not allowed
        or "\\" in url
        or "%" in parsed.netloc
        or not any(host == suffix or host.endswith("." + suffix) for suffix in DOMAINS.get(platform, ()))
    ):
        raise MediaError("unsafe_destination", "Source requested a blocked destination.", 400)
    records = (resolver or socket.getaddrinfo)(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    addresses = sorted({record[4][0] for record in records})
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise MediaError("unsafe_destination", "Source resolves to a restricted network address.", 400)
    return parsed, addresses


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, addresses, port, timeout):
        super().__init__(host, port=port, timeout=timeout, context=ssl.create_default_context())
        self.addresses = addresses

    def connect(self):
        last = None
        for address in self.addresses[:2]:
            try:
                sock = socket.create_connection((address, self.port), self.timeout)
                self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
                return
            except OSError as exc:
                last = exc
        raise last


class PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host, addresses, port, timeout):
        super().__init__(host, port=port, timeout=timeout)
        self.addresses = addresses

    def connect(self):
        last = None
        for address in self.addresses[:2]:
            try:
                self.sock = socket.create_connection((address, self.port), self.timeout)
                return
            except OSError as exc:
                last = exc
        raise last


class BoundedResponse:
    def __init__(self, raw, connection, max_bytes):
        self.raw, self.connection, self.max_bytes, self.count = raw, connection, max_bytes, 0
        self._closed = False

    @property
    def closed(self):
        return self._closed

    def readable(self):
        return True

    def read(self, amount=-1):
        amount = -1 if amount is None else amount
        remaining = self.max_bytes - self.count
        data = self.raw.read(min(amount, remaining + 1) if amount >= 0 else remaining + 1)
        self.count += len(data)
        if self.count > self.max_bytes:
            self.close()
            raise MediaError("file_too_large", "The source video exceeds the file size limit.", 413)
        if not data:
            self.close()
        return data

    def close(self):
        self._closed = True
        self.raw.close()
        self.connection.close()


class SafeTransport:
    def __init__(self, platform, max_bytes=32 * 1024 * 1024, timeout=20):
        self.platform, self.max_bytes, self.timeout = platform, max_bytes, timeout

    def open(self, url, method="GET", headers=None, data=None, cookiejar=None):
        headers = dict(headers or {})
        for key in list(headers):
            if key.lower() in {"host", "cookie", "authorization", "proxy-authorization", "connection", "accept-encoding"}:
                del headers[key]
        headers["Accept-Encoding"] = "identity"
        for hop in range(6):
            parsed, addresses = destination(url, self.platform)
            connection_class = PinnedHTTPS if parsed.scheme == "https" else PinnedHTTP
            connection = connection_class(
                parsed.hostname, addresses, parsed.port or (443 if parsed.scheme == "https" else 80), self.timeout
            )
            target = parsed.path or "/"
            if parsed.query:
                target += "?" + parsed.query
            outgoing = dict(headers)
            request = Request(url, data=data, headers=outgoing, method=method)
            if cookiejar is not None:
                cookiejar.add_cookie_header(request)
                outgoing = dict(request.header_items())
            connection.request(method, target, body=data, headers=outgoing)
            response = connection.getresponse()
            if cookiejar is not None:
                cookiejar.extract_cookies(response, request)
            if response.status in {301, 302, 303, 307, 308}:
                location = response.getheader("Location")
                response.close()
                connection.close()
                if not location or hop == 5:
                    raise MediaError("redirect_failed", "This video link could not be followed. Please try a direct public video link.")
                url = urljoin(url, location)
                if response.status == 303 or response.status in {301, 302} and method == "POST":
                    method, data = "GET", None
                continue
            length = response.getheader("Content-Length")
            if length and int(length) > self.max_bytes:
                response.close()
                connection.close()
                raise MediaError("file_too_large", "The source video exceeds the file size limit.", 413)
            return BoundedResponse(response, connection, self.max_bytes), response.headers, response.status, url
        raise MediaError("redirect_failed", "This video link could not be followed. Please try a direct public video link.")
