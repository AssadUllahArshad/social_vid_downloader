# Snapchat provider

Spotlight is enabled as **BETA** through the existing provider interface and normalized engine. Stories remain **UNSUPPORTED**. No WhatsApp implementation was started.

## Accepted links and flow

- Exact `snapchat.com` / `www.snapchat.com` submitted hosts only.
- `/spotlight/{id}` identifies a single public Spotlight clip.
- `/t/{token}` is recognized as a shared link. It is supported only when guarded redirects resolve to a valid public Spotlight URL. Non-Spotlight, account, login, expired and unsupported share targets fail truthfully. The redirect work runs inside the 90-second extraction process.
- `/stories/{creator}` and `/stories/{creator}/{id}` are recognized for an unsupported response, not extraction. Profiles, add-friend links, account pages and arbitrary subdomains are rejected.

The provider uses yt-dlp's [public Spotlight extractor](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/snapchat.py), which reads official share-page data identifying the requested clip. It does not call private account APIs. Unknown codecs/dimensions are measured through the common local probe. Formats, sessions, thumbnail proxy, preparation, file checks and serving use the same schema and services as existing providers; no Snapchat-specific API structure exists.

Outbound destinations are limited to Snapchat and its `sc-cdn.net` media/thumbnail CDN. Every DNS answer, redirect and connection uses the existing public-address checks and pinned transport. Account credentials, session-cookie uploads, login bypass and private Story access are not implemented.

## Live evidence

On October 7, 2026, this official extractor sample produced a real MP4:

`https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYYWtidGhudGZpAX1TKn0JAX1TKnXJAAAAAA`

FFprobe confirmed 480×880 video with audio; final size was **583,698 bytes**. The actual mobile frontend also analyzed it, fetched its source thumbnail, prepared the file, previewed it at 480×880 and saved it. Long example-URL wrapping was corrected after this test; both Snapchat and TikTok pages now measure 390px document width at a 390px viewport.

A second official extractor sample ending `AZEaIYnrAAAAAQ` was unavailable/removed/restricted. A successful sample does not imply all Spotlight links work. Short `/t/` resolution has controlled tests; no separate live short-link success is claimed.

## Story investigation

Snap officially supports [embedding public Stories](https://newsroom.snap.com/how-to-embed-snapchat-content?lang=en-GB) and [public share links](https://help.snapchat.com/hc/en-gb/articles/44902813459732-How-do-I-share-content-from-Snapchat). These facts do not establish a reliable downloader for every Story. Research fetched the real public `https://www.snapchat.com/@nasa` page: it exposed Spotlight and saved-highlight metadata, but no individual active public Story share link was present in the retrieved document. No Story file was created or claimed verified. The installed upstream extractor supports Spotlight, not Story extraction.

The public Snapchat Story downloader route and tool entry have been removed. Story detection remains for a clear unsupported API response and internal capability reporting. Profile lookup, highlight scraping, multi-Snap assembly and account-only content are outside this implementation. Do not infer that public Stories are impossible generally; this phase did not verify a supported download path.

No watermark removal, anonymous private viewing or universal 4K claims are made. Source pixels and any watermark are retained.
