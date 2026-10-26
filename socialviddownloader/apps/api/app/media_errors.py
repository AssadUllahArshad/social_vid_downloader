def platform_name(value):
    return {
        "youtube": "YouTube",
        "facebook": "Facebook",
        "instagram": "Instagram",
        "tiktok": "TikTok",
        "snapchat": "Snapchat",
        "whatsapp": "WhatsApp",
    }.get(value.lower(), value.title())


class MediaError(Exception):
    def __init__(self, code, message, status=422):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


def provider_error(exc, platform):
    text = str(exc).lower()
    if any(s in text for s in ["not a bot", "confirm you’re not", "confirm you're not", "automated requests", "bot detection"]):
        return MediaError("platform_unavailable", f"{platform_name(platform)} is temporarily limiting public video access. Please try again later.", 502)
    if "403" in text or "401" in text:
        return MediaError(
            "platform_access_restricted", f"{platform_name(platform)} could not provide access to this video. Please try another public link later.", 502
        )
    if any(s in text for s in ["login", "sign in", "cookies", "private", "authentication"]):
        return MediaError(
            "authentication_required",
            f"{platform_name(platform)} requires account access for this video. Private or login-required content is not supported.",
        )
    if any(s in text for s in ["cannot parse data", "unable to extract universal data", "unable to extract webpage"]):
        return MediaError(
            "extractor_changed", f"{platform_name(platform)} video information could not be read. Please try again later.", 502
        )
    if any(s in text for s in ["دستیاب نہیں", "not available", "unavailable", "removed", "not found", "404", "does not exist"]):
        return MediaError("video_unavailable", f"This {platform_name(platform)} video is unavailable, removed, or restricted.")
    if any(s in text for s in ["429", "too many", "rate limit"]):
        return MediaError("platform_rate_limited", f"{platform_name(platform)} is limiting requests. Please try again later.", 429)
    if "restricted network" in text or "blocked destination" in text:
        return MediaError("unsafe_destination", "The source requested a blocked destination.", 400)
    if "size limit" in text:
        return MediaError("file_too_large", "This video exceeds the permitted file size.", 413)
    if "timed out" in text or "timeout" in text:
        return MediaError("processing_timeout", "Video processing took too long. Try a shorter video.", 504)
    return MediaError(
        "platform_unavailable",
        f"{platform_name(platform)} could not provide this video. The platform may have changed or restricted public access.",
        502,
    )
