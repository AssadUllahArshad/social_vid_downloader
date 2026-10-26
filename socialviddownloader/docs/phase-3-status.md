# Phase 3 completion and live verification

Historical accepted milestone. The subsequent [public Story cleanup](snapchat-story-cleanup.md) removed the Story page and hub links; the Spotlight and TikTok evidence below is unchanged.

Phase 3 is complete within the accepted scope: public Snapchat Spotlight, Snapchat hub/unsupported Story behavior, TikTok native download/context hardening, protected provider observations, and regressions. Instagram/Snapchat Stories remain unsupported. WhatsApp and large-scale SEO expansion were not started.

## Implemented

- Public Spotlight adapter through the existing provider interface, strict official submitted hosts and supported paths, bounded share resolution, and the common normalized metadata/format/session/file pipeline.
- `/snapchat-downloader/` hub with clear Spotlight Beta and Story Unsupported links; legacy `/snapchat/` redirects to the hub.
- TikTok fresh native extraction and HTTP download in one guarded yt-dlp session. Shared anonymous cookie jar wiring was corrected; explicit selectors, headers, Referer and signatures stay private. The unverified TikTok public-parser fallback is disabled.
- AVAILABLE / BETA / TEMPORARILY_UNAVAILABLE / UNSUPPORTED tool states. Beta is usable, unsupported/temporarily unavailable is disabled. No unsupported watermark, private-access or 4K claims.
- Read-only token-protected administrator provider status with safe observations and timestamps; no raw logs/secrets in the response. No public technical-health endpoint.
- Final width as well as height checks, existing actual-size/audio/duration checks, and mobile wrapping for long example URLs.

## Live matrix

Public URLs tested locally on October 7, 2026, without user account credentials or browser-cookie uploads. Every PASS below created a real downloadable MP4, was inspected with FFprobe, and had its exact final size verified from disk. Tests selected a returned source format; listed dimensions are measurements, not advertised capabilities.

| Tool | Result | Verified dimensions | Final bytes | Public URL |
| --- | --- | --- | --- | --- |
| YouTube Video | PASS | 192×144 | 506,017 | https://www.youtube.com/watch?v=jNQXAC9IVRw |
| YouTube Shorts | PASS | 82×144 | 303,602 | https://www.youtube.com/shorts/BGQWPY4IigY |
| Facebook Video | PASS | 224×400 | 4,469,831 | https://www.facebook.com/watch/?v=647537299265662 |
| Facebook Reels | PASS | 362×640 | 352,915 | https://www.facebook.com/reel/1195289147628387 |
| Instagram Video | PASS | 640×640 | 1,017,460 | https://www.instagram.com/p/aye83DjauH/ |
| Instagram Reels | PASS | 480×854 | 918,120 | https://www.instagram.com/reel/Chunk8-jurw/ |
| TikTok Video | PASS | 576×1024 | 2,953,029 | https://www.tiktok.com/@scout2015/video/6718335390845095173 |
| Snapchat Story | UNSUPPORTED | — | — | Public NASA profile researched; no individual active Story share URL was found or verified |
| Snapchat Spotlight | PASS | 480×880 | 583,698 | https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYYWtidGhudGZpAX1TKn0JAX1TKnXJAAAAAA |

TikTok and Snapchat Spotlight additionally passed real mobile browser → Next proxy → API → thumbnail → format selection → preparation → native preview → file save. The browser measured TikTok at 576×1024 and Spotlight at 480×880. Both pages were checked at a 390px viewport after fixing long-URL wrapping and measured 390px document width.

Facebook Video initially failed its isolated analysis deadline. An independent retest of the same URL succeeded without weakening the budget. This transient failure is recorded rather than hidden. The selected public Facebook Reel and Instagram formats were video-only and were correctly offered without audio; no audio was fabricated.

A second Snapchat Spotlight sample ending `AZEaIYnrAAAAAQ` failed as unavailable/removed/restricted. Spotlight Beta does not promise every link works. `/t/` share-resolution behavior is tested with fixtures; no separate live short-link result is asserted.

Story research used the real official `https://www.snapchat.com/@nasa` public page, which exposed Spotlight/saved-highlight metadata but no individual active Story share link in the retrieved document. No Story download succeeded or is claimed. The Story UI remains disabled and the API returns unsupported; public Story downloading generally is not claimed impossible. See [Story investigation](snapchat-provider.md).

## Validation

- **97 API tests passed**, including all existing provider regressions, actual local media files/merges/ranges, Snapchat detection/parsing/normalization/preparation, private/auth rejection, native TikTok HTTP execution and context preservation, selector validation, specific 403 handling, private-context isolation, bounded/no-unverified fallback behavior, admin authorization and retained failure history.
- **18 browser tests passed** across desktop/mobile, covering downloader controls/files, Snapchat hub/Beta/unsupported states, temporary unavailability, protected administration, API errors and responsive layout.
- Two inventory tests passed. Ruff, ESLint, TypeScript in the production build and the Next production build passed.
- Real live files were inspected again independently with FFprobe and filesystem-size checks; CI remains independent of platform uptime.

One Starlette/AnyIO deprecation warning remains in test dependencies. Docker/container and production PostgreSQL deployment checks were not run because Docker is unavailable on this machine.

## Remaining limits

TikTok remains **BETA/degraded** for reliability even though the selected sample now succeeds. Stage observations distinguish actual success from overall provider maturity. HTTP 403, extractor changes, rate limits, unavailable content and slow upstream pages can still occur. Snapchat Spotlight is **BETA/experimental**; Stories remain unsupported. No password/session-cookie collection, private-content bypass, watermark-removal promise or fabricated source qualities exists.

Provider administration requires `ADMIN_PROVIDER_TOKEN` on the API; it is disabled when unconfigured. It is a read-only diagnostic panel, not full CMS authentication. Production ingress identity, durable job recovery and deployment concerns remain as documented in [engine limits](download-engine.md).

See [Snapchat strategy](snapchat-provider.md), [TikTok findings](tiktok-provider.md), and [capability matrix](provider-system.md).
