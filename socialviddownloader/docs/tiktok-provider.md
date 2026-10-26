# TikTok provider hardening

TikTok remains **BETA / degraded** for reliability, but Phase 3 obtained genuine downloads from the tested public URL. Existing YouTube, Facebook and Instagram paths retain their direct guarded download/merge strategy.

## Findings

Phase 2 sometimes extracted metadata but then received HTTP 403 from the selected CDN URL. A CDN response alone did not identify whether the cause was context, URL expiry, regional policy or platform blocking. [Upstream reports](https://github.com/yt-dlp/yt-dlp/issues/13771) describe similar differences between extracted direct URLs and native downloads; they are corroborating reports, not proof of this local cause.

A controlled real-media test identified a concrete local defect: the replacement guarded request handler did not share yt-dlp's own cookie jar. Cookies assigned directly by the extractor could therefore be absent from transport requests. The handler now receives `ydl.cookiejar`. Only fresh server-created anonymous cookies are involved; user passwords, browser cookies and cookie files are never collected.

## Download strategy

1. Native TikTok extraction returns the existing normalized quality list. Public format IDs are opaque hashes; raw selectors, headers and signed CDN URLs stay server-side.
2. The server's selected format invokes a bounded yt-dlp subprocess. It re-extracts the original validated public URL and downloads in **that same session**, using the fresh extractor HTTP context and cookie jar. It does not blindly replay the earlier cached CDN URL.
3. The fresh selector must exist, be unprotected, use direct HTTP/S, and agree with the known selected resolution. Unknown fresh dimensions defer to final FFprobe checks. Format changes produce a truthful error.
4. The native HTTP downloader uses the same pinned transport for every request/redirect, preserves Referer/User-Agent and signed query parameters, and applies deadline/progress/disk limits. Manifest formats, external downloaders, user authentication and merged native selections are rejected. TikTok's currently observed formats are combined video/audio; shared local merging for other providers is unchanged.
5. The common generator checks the actual output container, video height/width, required audio, duration and size before publishing a ready job. Timeout kills the whole subprocess group; failure removes partial files.

HTTP 401/403 normalize to `platform_access_restricted`; malformed pages, unavailable clips, expired sessions and time/size limits remain separate categories. There are no proxy rotations, fingerprint-bypass chains or retries without bounds.

The generic public-page fallback has **not** been verified for TikTok, so TikTok does not invoke it in this phase. Facebook/Instagram retain their already verified public-page strategy. A future secondary TikTok parser requires independent real-file verification before enabling it.

## Live result

`https://www.tiktok.com/@scout2015/video/6718335390845095173`

The hardened pipeline created a **2,953,029-byte MP4**, verified at **576×1024** with audio. The real mobile frontend/API also selected that format, prepared it, previewed its actual dimensions and saved it. This demonstrates working native context for the sample, not universal TikTok reliability. Other URLs/networks can still return 403 or changed page data; Beta status remains appropriate.

Tests use genuine local media and mocked upstream requests to confirm native yt-dlp download execution, header/cookie/signature preservation, private context isolation, valid selectors, no manifest delegation, specific 403 errors and absence of an unverified fallback chain. CI does not depend on TikTok availability.
