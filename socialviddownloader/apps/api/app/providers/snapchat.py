"""Public Spotlight only. Stories remain unavailable until a genuine path is verified."""

from urllib.parse import urlsplit

from yt_dlp.extractor.snapchat import SnapchatSpotlightIE

from ..media_errors import MediaError
from ..security import validate_media_url
from ..transport import SafeTransport
from .base import Capabilities, Provider


class SnapchatProvider(Provider):
    def __init__(self):
        super().__init__("snapchat", enabled=True)
        self.capabilities = Capabilities(supportsPublicUrl=True, supportsSpotlight=True, enabled=True)

    def extract(self, url):
        _, _, kind = validate_media_url(url, "snapchat")
        if kind == "profile":
            raise MediaError("snapchat_profile", "This is a Snapchat profile, not an individual Spotlight video.", 501)
        if kind not in {"spotlight", "shared"}:
            raise MediaError(
                "content_unsupported",
                "Only public Spotlight links are supported. Snapchat Stories and account content are unavailable.",
                501,
            )
        record = super().extract(url)
        record["metadata"]["contentType"] = "spotlight"
        return record


def resolve_public_spotlight(url):
    """Runs inside the bounded extraction process, including share redirects."""
    from ..security import InvalidUrl

    url, _, kind = validate_media_url(url, "snapchat")
    if kind == "shared":
        try:
            body, _, status, final = SafeTransport("snapchat").open(url)
        except (OSError, TimeoutError) as exc:
            raise MediaError("snapchat_temporary", "Snapchat could not be reached. Please try again later.", 502) from exc
        body.close()
        if status in {401, 403}:
            raise MediaError("snapchat_restricted", "Snapchat restricts access to this content. Login-required content is not supported.", 422)
        if status == 429 or status >= 500:
            raise MediaError("snapchat_temporary", "Snapchat is temporarily limiting access. Please try again later.", 502)
        if status != 200:
            raise MediaError("snapchat_unavailable", "This Snapchat share link is unavailable or expired.", 422)
        if urlsplit(final).path.rstrip("/") in {"/accounts/login", "/accounts", "/login"}:
            raise MediaError("snapchat_restricted", "Snapchat requires account access for this content. It cannot be downloaded here.", 422)
        try:
            url, _, kind = validate_media_url(final, "snapchat")
        except InvalidUrl as exc:
            raise MediaError(
                "snapchat_not_spotlight", "This Snapchat share link does not point to an individual public Spotlight video.", 501
            ) from exc
    if kind == "profile":
        raise MediaError("snapchat_profile", "This is a Snapchat profile, not an individual Spotlight video.", 501)
    if kind == "story":
        raise MediaError("content_unsupported", "Snapchat Story downloading is not supported. Use a public Spotlight link.", 501)
    if kind != "spotlight":
        raise MediaError(
            "snapchat_not_spotlight", "This Snapchat link does not identify an individual public Spotlight video.", 501
        )
    return url


class PublicSpotlightIE(SnapchatSpotlightIE):
    """Compatibility for creator-qualified URLs and complete URL-safe IDs.

    Reuse upstream's exact story-ID metadata selection, never a recommended
    feed entry. All webpage/media requests still use the pinned GuardedRH.
    """

    _VALID_URL = r"https?://(?:www\.)?snapchat\.com/(?:@[A-Za-z0-9_.-]+/)?spotlight/(?P<id>[A-Za-z0-9_-]+)(?:[/?#]|$)"

    def _search_nextjs_data(self, *args, **kwargs):
        data = super()._search_nextjs_data(*args, **kwargs)
        if data.get("props", {}).get("pageProps", {}).get("restricted"):
            raise MediaError("snapchat_restricted", "Snapchat restricts access to this content. Login-required content is not supported.", 422)
        return data

    def _real_extract(self, url):
        info = super()._real_extract(url)
        if not info.get("url"):
            raise MediaError(
                "snapchat_extraction_failed", "This Spotlight link is recognized, but Snapchat did not expose playable public media.", 502
            )
        return info


provider = SnapchatProvider()
