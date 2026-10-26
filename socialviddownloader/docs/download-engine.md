# Shared downloader engine

All eight integrated tool pages call the same backend. Platform adapters declare capabilities and delegate extraction to the common yt-dlp engine. No page owns extraction code. Snapchat Spotlight is beta; Instagram/Snapchat Stories and WhatsApp return truthful unsupported responses.

1. `POST /api/v1/extract` accepts `url`, optional `platform` and `contentType`. Exact submitted hosts and supported paths are validated. A bounded isolated yt-dlp process extracts one non-live, unprotected video. Facebook/Instagram can fall back to public embedded JSON that explicitly identifies the submitted video. That fallback measures media locally rather than inferring dimensions/codecs.
2. A short-lived session returns title, creator, duration if known, a same-origin thumbnail proxy, and normalized formats. Unknown sizes stay null; sums of input tracks are estimates. Signed media URLs and extractor selectors remain server-side. Only actual direct HTTP MP4/WebM formats are offered. Manifest-only formats are unsupported in this phase.
3. `POST /api/v1/download` accepts the session and an opaque format ID. It returns a queued job, never a fabricated download success. TikTok uses a bounded native yt-dlp download with fresh extraction context; other providers download bounded tracks and merges compatible audio/video with local FFmpeg stream copy when needed.
4. `GET /api/v1/jobs/{id}` reports processing/ready/error. A ready result requires a real file. FFprobe verifies video dimensions and required audio; final size comes from disk.
5. `GET /api/v1/files/{id}` serves the attachment, or `?inline=1` for native video preview, including byte ranges. `GET /api/v1/thumbnail/{session}` proxies a bounded real source image.

The Next route is an explicit operation whitelist and streaming same-origin proxy. Each tool passes its expected platform/type for validation. Source thumbnail precedes generation; native video preview becomes available once a file has been prepared. Quality labels report actual source pixel height, including irregular portrait heights; dimensions remain available in the API. No nonexistent 4K or fabricated sizes are added.

## Limits and security

Defaults: 90-second extraction, 180-second generation, 30-minute source duration, 200 MiB total input/final file limit, two concurrent jobs, 1 GiB temporary storage, 120-second metadata cache, 10-minute sessions/files, 8 KiB request bodies. Configure through environment variables. Oversized, empty, malformed and HTML-instead-of-video responses fail and clean their partial directories.

Every extractor, probe, thumbnail and media HTTP request uses the same domain allowlist and pinned-IP transport. All DNS answers must be public; redirects are revalidated; TLS uses the original hostname. No environment proxies or unrestricted yt-dlp handlers remain. FFmpeg/FFprobe accept only local file/pipe inputs and supported containers. Extraction is isolated with process/CPU/file limits and process-group cancellation.

No password, user cookie, netrc or authentication inputs are accepted. Fresh anonymous cookies set by public upstream pages can be used inside extraction; user browser cookies are never collected. Tokens are bearer access to ephemeral results: keep them private. Logs omit submitted URLs and signed URLs. Redis state expires automatically; the explicit local SQLite store removes expired records during operations. File sweeping runs every 30 seconds with a conservative generation grace period. Files may remain on disk briefly after access expires.

Use one API instance with local media storage, or mount a shared filesystem across API replicas. Job metadata in Redis alone does not share files. Worker/download concurrency is globally leased through Redis; extraction/thumbnail concurrency is bounded per process. Interrupted jobs can expire rather than automatically resume. There is no durable background queue or restart recovery yet.

Rate limits use HMAC client identities. The Next proxy does not forward untrusted incoming identity headers, so proxied requests share its identity by default. Production needs an ingress that supplies a trustworthy client identity and an explicitly configured forwarding/trust policy before per-user rate limits can be relied upon; do not blindly trust arbitrary `X-Forwarded-For`. `TRUSTED_PROXY_IPS` applies to direct API ingress. Restrict API exposure.

API errors retain meaningful categories: login/access restriction, unavailable media, extractor changes, rate limiting, unsafe destinations, size/time limits and expired sessions/files. Platform blockers are surfaced; no bypass of private or protected content is implemented.

Phase 3 provider behavior and evidence are documented in [provider system](provider-system.md) and [live matrix](phase-3-status.md).
