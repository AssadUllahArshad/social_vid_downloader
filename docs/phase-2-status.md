# Phase 2 verification

Historical evidence: Phase 2 was accepted with its known TikTok limitation. [Phase 3 verification](phase-3-status.md) supersedes the current provider status below.

The shared core downloader and all seven requested tool integrations are implemented. **Phase 2 is not fully verified complete:** TikTok did not produce a downloadable file in the live tests. Instagram Stories remain disabled; Snapchat and WhatsApp were not started.

## Actual public-link tests

Tested locally on October 7, 2026, without user passwords or browser cookies. yt-dlp 2026.8.19 was confirmed as the latest published stable release on PyPI during verification. Successful files were inspected with FFprobe; sizes below come from the final file on disk, not estimates. Source availability may change.

| Tool | Public sample | Observed result |
| --- | --- | --- |
| YouTube Video | https://www.youtube.com/watch?v=jNQXAC9IVRw | Downloaded 144p MP4, 506,017 bytes; separate video/audio merged. Also passed the full mobile browser → Next proxy → API → quality selection → preview → file-save workflow. Native preview measured 192×144. |
| YouTube Shorts | https://www.youtube.com/shorts/BGQWPY4IigY | Downloaded 144p merged MP4, 303,602 bytes. |
| Facebook Video | https://www.facebook.com/watch/?v=647537299265662 | Downloaded 224×400 MP4, 4,469,831 bytes, through the bounded isolated worker and actual generator. Two measured formats were offered (720×1280 and 224×400). Initial worker timeouts were resolved by measuring readable MP4 headers before fetching the entire probe range. Native yt-dlp could not parse the page; the public-data path succeeded. |
| Facebook Reels | https://www.facebook.com/reel/1195289147628387 | Downloaded 362×640 MP4, 352,915 bytes, through the isolated extraction worker and real generator. Public page data fallback used. Also passed the real Next proxy/API pipeline with a JPEG thumbnail (43,336 bytes). |
| Instagram Video | https://www.instagram.com/p/aye83DjauH/ | Downloaded 640×640 MP4, 1,017,460 bytes. Also passed the real Next proxy/API session → job → file pipeline, with actual JPEG thumbnail (59,900 bytes). |
| Instagram Reels | https://www.instagram.com/reel/Chunk8-jurw/ | Downloaded 480×854 MP4, 918,120 bytes, through isolated extraction and real generation. Public page data fallback used. |
| TikTok Video | https://www.tiktok.com/@scout2015/video/6718335390845095173 | Metadata intermittently extracted, but actual media fetch returned HTTP 403. Other attempts could not extract page rehydration data. No successful file. |
| TikTok alternate | https://www.tiktok.com/@moxypatch/video/7206382937372134662 | Failed because yt-dlp could not parse page rehydration data; public fallback did not yield verified media. Another sample, `@hankgreen1/video/7047596209028074758`, failed similarly. |
| Instagram Story investigation | https://www.instagram.com/stories/fruits_zipper/3570766765028588805/ | No publicly processable media established; upstream requests entered a blocked cross-platform flow. Remains disabled. |

The initially tried Facebook Reel ID ending `8380` was incorrect; the verified official extractor sample ends `8387`. One temporary manual harness also initially unpacked the generator's dictionary as a tuple; those harness errors were corrected and the affected Instagram tests rerun. Neither error was a downloader success claim.

The public fallback does not log in or bypass authentication. Instagram Story extraction can require authentication in the [upstream extractor](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/instagram.py). This implementation has no verified public Story or authorized API integration, so it is intentionally unavailable.

## Controlled checks

- 70 API tests passed: all seven platform/content types through the shared API contract with actual generated video bytes, FFmpeg merge verification, exact final filesize, range serving, malformed-media rejection, expiry and validation, DNS/private-address/redirect controls, request limits, fallback ownership/login/measurement rules, lease ownership, partial-header previews and true 4K dimensions.
- 12 Playwright tests passed across desktop/mobile: real generated media fixtures, quality selection, prepare/poll/save/preview, stale response handling, platform routes, actual API error forwarding and bounded proxy requests.
- Two frontend inventory tests, ESLint, Ruff and Next production build passed.
- Live mobile YouTube test also saved a real MP4 and verified native video dimensions without horizontal overflow.

Controlled tests mock platform metadata/network access using genuine local media fixtures. They prove pipeline behavior but do not establish live platform availability. Docker/PostgreSQL production deployment was not exercised on this machine; Docker is unavailable.

See [engine limits and remaining production concerns](download-engine.md). Before declaring the requested phase fully complete, establish a successful TikTok download on the intended deployment network and address any remaining upstream incompatibility. No fake success response substitutes for those checks.
