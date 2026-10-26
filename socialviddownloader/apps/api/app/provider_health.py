"""Internal sanitized observations. Public capabilities contain availability only."""

from datetime import datetime, timezone

CONTENT_TYPES = {
    "youtube": ["video", "shorts"],
    "facebook": ["video", "reels"],
    "instagram": ["video", "reels"],
    "tiktok": ["video"],
    "snapchat": ["spotlight"],
    "whatsapp": [],
}
STATES = {
    "youtube": {"video": "AVAILABLE", "shorts": "AVAILABLE"},
    "facebook": {"video": "AVAILABLE", "reels": "AVAILABLE"},
    "instagram": {"video": "AVAILABLE", "reels": "AVAILABLE", "story": "UNSUPPORTED"},
    "tiktok": {"video": "BETA"},
    "snapchat": {"spotlight": "BETA", "story": "UNSUPPORTED", "shared": "BETA"},
    "whatsapp": {"status": "UNSUPPORTED"},
}


def baseline(provider):
    known = provider in {"youtube", "facebook", "instagram"}
    return {
        "provider": provider,
        "supportedContentTypes": CONTENT_TYPES[provider],
        "status": "operational"
        if known
        else "degraded"
        if provider == "tiktok"
        else "experimental"
        if provider == "snapchat"
        else "unavailable",
        "extraction": "operational"
        if known
        else "degraded"
        if provider == "tiktok"
        else "experimental"
        if provider == "snapchat"
        else "unavailable",
        "download": "operational"
        if known
        else "degraded"
        if provider == "tiktok"
        else "experimental"
        if provider == "snapchat"
        else "unavailable",
        "contentTypes": STATES[provider],
        "supports_multiple_audio_tracks": None,
        "supports_language_metadata": None,
        "supports_dual_audio_mux": None,
        "lastTestStatus": "PASS" if known else "FAIL" if provider == "tiktok" else "NOT_TESTED",
        "lastFailureCategory": "platform_access_restricted" if provider == "tiktok" else None,
        "lastSuccessfulLiveTest": "2026-10-07" if known else None,
        "evidence": "Accepted Phase 2 live verification"
        if known
        else "Phase 2 provider limitation"
        if provider == "tiktok"
        else "No successful live test recorded",
    }


async def observe(store, provider, stage, success, category=None):
    # Called only after actual upstream extraction or final FFprobe-verified file generation.
    record = await store.get("provider-health:" + provider) or baseline(provider)
    now = datetime.now(timezone.utc).isoformat()
    record.update(lastTestStatus="PASS" if success else "FAIL", lastTestAt=now)
    if not success:
        record.update(lastFailureCategory=category, lastFailureAt=now)
    record[stage] = "operational" if success else "degraded"
    if stage == "download" and success:
        record["lastSuccessfulLiveTest"] = now
        record["evidence"] = "API created and FFprobe verified an actual file"
    record["status"] = "operational" if record["extraction"] == record["download"] == "operational" else "degraded"
    if provider == "snapchat":
        record["status"] = "experimental"
    elif provider == "tiktok":
        record["status"] = "degraded"  # One successful source does not establish broad reliability.
    await store.set("provider-health:" + provider, record, 30 * 86400)


async def observe_audio(store, provider, metadata=None, result=None):
    """Track source-specific evidence, never assume provider-wide language support."""
    record = await store.get("provider-health:" + provider) or baseline(provider)
    if metadata is not None and "audio_tracks" in metadata:
        tracks = metadata["audio_tracks"]
        record["supports_multiple_audio_tracks"] = len(tracks) > 1
        record["supports_language_metadata"] = any(track.get("language_code") for track in tracks)
    if result is not None and len(result.get("audio_tracks", [])) > 1:
        record["supports_dual_audio_mux"] = True  # Reached only after final FFprobe checks.
    await store.set("provider-health:" + provider, record, 30 * 86400)
