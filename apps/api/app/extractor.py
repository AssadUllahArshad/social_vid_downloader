import shutil
import time

from yt_dlp import YoutubeDL
from yt_dlp.networking.common import RequestHandler, Response
from yt_dlp.networking.exceptions import HTTPError, TransportError

from .audio import public_audio
from .config import settings
from .formats import normalize
from .media_errors import MediaError, provider_error
from .probe import fill_missing_formats
from .public_page import public_video_info
from .transport import SafeTransport


class QuietLogger:
    def debug(self, message):
        pass

    def warning(self, message):
        pass

    def error(self, message):
        pass


class GuardedRH(RequestHandler):
    _SUPPORTED_URL_SCHEMES = ("http", "https")
    _SUPPORTED_PROXY_SCHEMES = ()

    def __init__(self, platform, deadline, **kwargs):
        super().__init__(**kwargs)
        self.transport = SafeTransport(platform)
        self.deadline = deadline

    def _check_extensions(self, extensions):
        super()._check_extensions(extensions)
        for name in ["cookiejar", "timeout", "legacy_ssl", "keep_header_casing"]:
            extensions.pop(name, None)

    def _send(self, request):
        if time.monotonic() > self.deadline:
            raise TransportError("processing timeout")
        try:
            body, headers, status, url = self.transport.open(
                request.url,
                method=request.method,
                headers=self._get_headers(request),
                data=request.data,
                cookiejar=self._get_cookiejar(request),
            )
            response = Response(body, url, headers, status=status)
            if status >= 400:
                raise HTTPError(response)
            return response
        except MediaError as exc:
            raise TransportError(exc.message) from exc
        except OSError as exc:
            raise TransportError(str(exc)) from exc


def extract_metadata(url, platform):
    if platform == "snapchat":
        from .providers.snapchat import resolve_public_spotlight

        url = resolve_public_spotlight(url)
    deadline = time.monotonic() + settings.extract_timeout_seconds
    options = {
        "quiet": True,
        "no_warnings": True,
        "logger": QuietLogger(),
        "noplaylist": True,
        "skip_download": True,
        "socket_timeout": 20,
        "retries": 1,
        "extractor_retries": 1,
        "cachedir": False,
        "proxy": "",
        "usenetrc": False,
        "allow_unplayable_formats": False,
        "js_runtimes": {"node": {"path": shutil.which("node")}} if shutil.which("node") else {},
        "remote_components": [],
        "check_formats": False,
    }
    try:
        info = None
        extraction_strategy = "native"
        if platform in {"facebook", "instagram"} and "/stories/" not in url:
            try:
                info = public_video_info(url, platform)
                extraction_strategy = "public_page"
            except Exception:
                pass
        if info is None:
            try:
                with YoutubeDL(options) as ydl:
                    director = ydl._request_director
                    director.close()
                    director.add_handler(GuardedRH(platform, deadline, logger=QuietLogger(), proxies={}, cookiejar=ydl.cookiejar))
                    if platform == "snapchat":
                        from .providers.snapchat import PublicSpotlightIE

                        ydl.add_info_extractor(PublicSpotlightIE(ydl))
                        info = ydl.extract_info(url, download=False, ie_key=PublicSpotlightIE.ie_key())
                    else:
                        info = ydl.extract_info(url, download=False)
            except Exception as original:
                if platform not in {"facebook", "instagram"} or "/stories/" in url:
                    raise
                try:
                    info = public_video_info(url, platform)
                    extraction_strategy = "public_page"
                except Exception:
                    raise original
        if not info or info.get("_type") in {"playlist", "multi_video"}:
            raise MediaError("collection_unsupported", "Use a link to one video, not a collection or carousel.")
        if info.get("duration") and info["duration"] > settings.max_duration_seconds:
            raise MediaError("video_too_long", "This video exceeds the duration limit.", 413)
        if not info.get("formats") and info.get("url"):
            info["formats"] = [{**info, "format_id": str(info.get("format_id") or "source"), "protocol": "https"}]
        fill_missing_formats(info, platform)
        if info.get("duration") and info["duration"] > settings.max_duration_seconds:
            raise MediaError("video_too_long", "This video exceeds the duration limit.", 413)
        formats, selections = normalize(info, settings.max_file_bytes, bool(shutil.which(settings.ffmpeg_path)), platform)
        metadata = {
            "platform": platform,
            "title": info.get("title") or "Untitled video",
            "creator": info.get("uploader") or info.get("channel"),
            "duration": info.get("duration"),
            "thumbnailSource": info.get("thumbnail"),
            "formats": formats,
            **public_audio(selections),
        }
        return {
            "metadata": metadata,
            "selections": selections,
            "source": url,
            "platform": platform,
            "downloadStrategy": "yt_dlp" if platform == "tiktok" and extraction_strategy == "native" else "direct",
        }
    except MediaError:
        raise
    except Exception as exc:
        if platform == "snapchat":
            import re

            failure = provider_error(exc, platform)
            categories = {
                "authentication_required": "snapchat_restricted", "platform_access_restricted": "snapchat_restricted",
                "video_unavailable": "snapchat_unavailable", "extractor_changed": "snapchat_extraction_failed",
                "platform_unavailable": "snapchat_extraction_failed", "platform_rate_limited": "snapchat_temporary",
                "processing_timeout": "snapchat_temporary",
            }
            failure.code = categories.get(failure.code, failure.code)
            if re.search(r"http (?:error )?(?:429|5\d\d)\b|unable to download webpage|connection (?:refused|reset)", str(exc), re.I):
                failure = MediaError("snapchat_temporary", "Snapchat is temporarily unavailable. Please try again later.", 502)
            raise failure from exc
        raise provider_error(exc, platform) from exc
