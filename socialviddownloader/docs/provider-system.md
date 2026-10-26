# Provider system

All providers share capability and normalized extraction interfaces. Independent tool pages call one API. YouTube Video/Shorts, Facebook Video/Reels and Instagram Video/Reels remain available. TikTok and Snapchat Spotlight are beta. Instagram/Snapchat Stories and WhatsApp are unsupported.

| Provider | Content | Public tool state | Download strategy |
| --- | --- | --- | --- |
| YouTube | Video, Shorts | AVAILABLE | Guarded direct tracks, common FFmpeg merge |
| Facebook | Video, Reels | AVAILABLE | Verified public-page/native metadata, common guarded download |
| Instagram | Video, Reels | AVAILABLE | Verified public-page/native metadata, common guarded download |
| TikTok | Video | BETA | Fresh native yt-dlp extraction/download in one guarded session |
| Snapchat | Spotlight | BETA | Public share-page yt-dlp extraction, common guarded download |
| Snapchat | Stories (internal capability only) | No public tool | Unsupported API response; no verified download path enabled |
| Instagram | Stories | UNSUPPORTED | No verified download path enabled |
| WhatsApp | Status | UNSUPPORTED | Not started |

`GET /api/v1/capabilities` provides only safe content-type states: AVAILABLE, BETA, TEMPORARILY_UNAVAILABLE and UNSUPPORTED. Beta controls are usable with a subtle notice; unsupported and temporary-unavailable controls are disabled. Snapchat Story is not a public tool or landing page; its unsupported capability is retained internally. Static reviewed defaults make pages usable without waiting for capability fetch; explicit API states update the form. Private extraction context is never serialized to the browser.

Extraction retains its isolated process budget; Snapchat share resolution runs inside that process. Network protections cover all metadata, probes, thumbnails, native TikTok and direct media requests. FFprobe validates actual generated files before success. No password/cookie uploads, DRM bypass or private-account access exist.

## Internal provider administration

`/admin/` contains a development-only read-only provider status panel; production returns 404. Configure a long random `ADMIN_PROVIDER_TOKEN` **only on the API**, then use it in authorized private diagnostics requests (or the development masked panel). The frontend proxy forwards the bearer token to `/internal/provider-status`. It never stores the token in local/session storage or publishes it in frontend environment variables. Compose forwards the optional setting. An unset token disables the internal endpoint (404); an invalid token returns 401. This does not implement CMS editing or full administrator accounts, which remain later work.

The authenticated response shows provider, supported content types, overall status, extraction/download observations, last test result, last failure category and last successful verified file timestamp. It contains no raw logs, source/CDN URLs, tokens or passwords. Current API extraction/file results update observations with 30-day state retention. Last failure is retained across later success. Cached analyses do not count as new live tests. Overall Snapchat remains experimental and TikTok degraded even after a successful sample; stage results record actual latest outcomes. Existing-provider baselines explicitly cite accepted Phase 2 evidence; they are not fabricated current monitoring checks.

Public pages/capabilities omit technical health categories and timestamps. The panel is a protected diagnostic surface, not a continuous external monitoring service. Do not expose the API publicly without the deployment safeguards in [engine documentation](download-engine.md).

See [Snapchat](snapchat-provider.md), [TikTok](tiktok-provider.md), and [Phase 3 live verification](phase-3-status.md).

## Deployment smoke tests

Basic routes and private dependencies: `node scripts/smoke-production.mjs https://socialviddownloader.com`. Optional live tests: `python3 scripts/smoke-providers.py --help`; supply your authorized public URLs. Results print PASS/FAIL and error category; temporary client media is removed and server media expires normally. No test depends on passwords or cookies. YouTube remains intermittent; TikTok may safely reject changed source formats; Spotlight stays Beta. The production diagnostics credential can be initialized with scripts/initialize-provider-admin.py; no CMS password/session login exists in this release.
