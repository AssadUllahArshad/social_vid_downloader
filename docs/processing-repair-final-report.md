# Processing and sitemap repair — final verification

Verified 2026-10-13T18:28:04.022566+00:00. **READY FOR MANUAL DEPLOYMENT.** No external deployment or new SEO articles.

## Server and sitemap reconciliation

All final browser and HTTP verification used `http://127.0.0.1:3000`, standalone production Webpack build `-F7VjDt9_-5BXzoBfsT-K` (web PID 62839), with the isolated API on port 8001 (PID 62840). API functional tests used development SQLite explicitly; this does not claim PostgreSQL/Redis integration testing. Bulk tests used a test-only write limit of 1000/minute. Production defaults, read limits, concurrency, storage, file, CPU and timeout protections remain unchanged.

The failing server was PID 61279, default Turbopack development. Its JSON transform changed floating-point semantic-review values (for example 0.09090909090909091 became 0.09090909090909093). All 525 source approval digests were valid, but 108 compiled payloads failed their unchanged approval check. Dependency pruning then removed another 275 articles. That accounts for all **383 missing indexable URLs**: 349 general, 18 YouTube, 4 WhatsApp, 5 TikTok, 3 Snapchat, 1 Facebook and 3 Instagram. Another 31 noindex collection routes were pruned as a consequence. No content was deleted or manufactured.

Development and production package commands now explicitly select Webpack. Playwright release runs use `PLAYWRIGHT_EXTERNAL_SERVER=1` to prevent implicit dev-server startup/reuse. The exact missing URL list, digest evidence and final server identity are in [sitemap-route-mismatch.json](sitemap-route-mismatch.json).

Final HTTP inventory: **1,097 public 200 pages; 1,020 indexable; 77 noindex; 1,020 unique sitemap URLs**. All 383 missing indexable articles are restored. Zero public URLs removed. Zero canonical, metadata uniqueness, schema, sitemap eligibility, missing sitemap, link, orphan or robots errors. All 506 multilingual pages checked; 456 eligible translated pages, zero hreflang errors. All 1,602 nonpublic candidate routes remain 404. The 448 unfinished SEO candidates remain untouched and nonpublic.

## Actual tool output

| Tool | URL | Desktop | Mobile |
|---|---|---|---|
| Video Converter | /video-converter/ | PASS | PASS |
| Video Compressor | /video-compressor/ | PASS | PASS |
| Video Trimmer | /trim-video/ | PASS | PASS |
| Video Splitter | /split-video/ | PASS | PASS |
| Video Merger | /merge-videos/ | PASS | PASS |
| Video to GIF | /video-to-gif/ | PASS | PASS |
| GIF to Video | /gif-to-video/ | PASS | PASS |
| Thumbnail Extractor | /video-thumbnail-extractor/ | PASS | PASS |
| Thumbnail Grid | /thumbnail-grid-generator/ | PASS | PASS |
| MP3 Audio Extractor | /video-to-mp3/ | PASS | PASS |
| Remove Audio | /remove-audio-from-video/ | PASS | PASS |
| Images to Video | /images-to-video/ | PASS | PASS |
| Image Watermark | /add-image-watermark/ | PASS | PASS |
| Text Watermark | /add-text-watermark/ | PASS | PASS |
| Burn Subtitles | /burn-subtitles-into-video/ | PASS | PASS |
| Extract Subtitles | /extract-video-subtitles/ | PASS | PASS |
| Video Information | /video-metadata-viewer/ | PASS | PASS |
| Video Filters | /video-filters/ | PASS | PASS |
| Video Stabilizer | /stabilize-video/ | PASS | PASS |
| Trim Silence | /remove-silence-from-video/ | PASS | PASS |
| Storyboard Creator | /video-storyboard-generator/ | PASS | PASS |
| Change Video Speed | /change-video-speed/ | PASS | PASS |

These are **44 actual upload → settings → processing → download workflows**, using an authorized 1080×1920 real-footage excerpt (3,777,843 bytes, about eight seconds), plus derived images/GIFs and authorized subtitle fixtures where appropriate. Media outputs were inspected with FFprobe and decoded with FFmpeg; split archives were unpacked and every segment probed, metadata JSON parsed and subtitle cues checked. The original 59,431,977-byte, 126.293-second Trailer3.mp4 additionally passed Remove Audio on desktop/mobile against this same final server. Earlier verified full-length compression results (26,670,779-byte outputs, about 109–110 seconds) are preserved; they were not unnecessarily repeated. These checks do not assert every format or full-length setting fits the bounded processing budget.

Two real cancellation workflows revoked file delivery. All 26 translated invalid-upload error checks passed. API tests verified CPU/output limits, corrupt inputs, admission, real expiry and stale cleanup. Original provider/download regressions from the saved repair run remain valid; downloader providers were not changed.

## 429/503 investigation and verifier corrections

The historical verifier reused the entire trailer and default settings for every operation, omitted necessary auxiliary inputs, tried to probe ZIP/JSON as video, retained media and exited successfully despite failures. It is replaced by the operation-specific browser workflow and fails when any required project/output is unverified. The original failures are preserved in [processing-load-failure-evidence.json](processing-load-failure-evidence.json).

The earlier API log contains 16 responses with 503 and two with 429. Retained media was roughly 765 MiB; storage plus conservative reservations exceeded the 1 GiB budget. Historical response bodies were discarded, so individual old 503 categories cannot be proven retrospectively. The two rapid final upload retries hit the write-rate guard. At resume, no API was running, producing a separately confirmed frontend `service_unavailable` 503. The old full-length/default splitter request hit the processing-time budget; shorter operation-specific real-footage splits passed without raising that limit.

The final server logged **zero 429s**. One additional overlapping job request at 18:23:05 UTC was explicitly logged as `storage_busy`, while the mobile speed workflow was active. The reservation check safely rejected that request; all 44 named workflows still passed. Expected invalid-upload 422s and cancelled-delivery 410s remain tested. New logs record safe error categories without submitted URLs, credentials or capability identifiers.

The results exporter initially read only the first project suite, incorrectly flagging mobile despite Playwright's **44 passed / zero failed** result. It now aggregates all suites; three focused regressions verify separate projects, missing projects and failed/skipped results. The named execution log and Playwright zero-failure status were used to correct the saved matrix without rerunning completed media work. `video-tools-verification.log.exit` preserves the original exporter exit 1; it is not a media failure or a claimed successful process exit. Future runs retain raw JSON results as well.

## Final checks

- Browser: **98 passed** (44 tool, 24 SEO/multilingual/proxy-security, 28 cancellation/error, 2 original-trailer).
- API: **238 unique checks passed across full and focused runs**. Initial full run had two fixture failures; explicit Redis configuration now lets those production tests exercise the intended wildcard guard. Corrected affected suite: 36 passed; new storage tests: 2 passed. One third-party deprecation warning remains informational.
- Publication: **26 passed**; exporter regressions: **3 passed**.
- TypeScript, ESLint, Ruff and one production Webpack build: **PASS**.
- Full HTTP SEO, multilingual/hreflang and draft-isolation audits: **zero errors**.

Evidence: [processing-repair-verification.json](processing-repair-verification.json), [video-tools-execution-state-run.json](video-tools-execution-state-run.json), current audit JSON files and `/private/tmp/svd-reconciliation/` logs. Checkpoint saved in [processing-repair-checkpoint.json](processing-repair-checkpoint.json). No known unresolved locally fixable critical blocker remains. Follow [manual-deployment.md](manual-deployment.md) for manual host setup and smoke checks.
