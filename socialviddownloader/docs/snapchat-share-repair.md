# Snapchat Spotlight share-link repair — 14 October 2026

**Verified:** the supplied public short link now produces a real downloadable video. Spotlight remains **Beta**. No Stories, profile downloads, private access, credentials or authentication bypass were enabled.

## Cause and change

`https://snapchat.com/t/2mjmfV1D` publicly resolves to `https://www.snapchat.com/@teranirmaan/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZ2RpcmF6YW9nAaB-ty4LAaB-trvXAAAAAw`. The frontend accepted the link and the guarded transport followed its redirects successfully. Backend classification then rejected the creator-qualified path before metadata extraction. A second defect in the installed upstream extractor's ID pattern truncated hyphenated identifiers.

Validation now recognizes both `/spotlight/ID` and `/@creator/spotlight/ID` on the existing exact entry hosts, with or without `www`. The Snapchat-specific extractor subclass preserves full URL-safe IDs and reuses the upstream exact-ID metadata selection; it never substitutes a recommendation-feed clip. `/t/` is only classified as Spotlight after its destination is validated. Story/profile recognition exists solely to return accurate unsupported errors without extraction.

The same pinned transport still validates domains and every resolved IP/redirect. Allowlisted domains, bounded subprocesses, request budgets, file limits and cookies policy are unchanged. No package files or other providers were patched. Seven distinct error messages cover wrong content, Stories, profiles, restricted access, unavailable content, temporary source failure and recognized Spotlight with inaccessible media. All are localized in the existing 13 languages without changing approved page dictionaries, URLs or publication digests.

## Real URL verification

| URL | Result | Verified bytes | Duration (s) |
|---|---|---:|---:|
| `https://snapchat.com/t/2mjmfV1D` | PASS | 794,705 | 4.733333 |
| `https://www.snapchat.com/t/2mjmfV1D` | PASS | 794,705 | 4.733333 |
| `https://snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZ2RpcmF6YW9nAaB-ty4LAaB-trvXAAAAAw` | PASS | 794,705 | 4.733333 |
| `https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYYWtidGhudGZpAX1TKn0JAX1TKnXJAAAAAA` | PASS | 583,698 | 4.641995 |

The supplied clip is “Welcome to America 🇺🇸  guys 👀” by `teranirmaan`: H.264 video at 540×960 with AAC audio. Source filesize was unknown during extraction and remained unknown in the quality selector; actual downloaded size was verified afterward. Thumbnail requests and source-reported formats passed. No resolutions or sizes were fabricated.

The supplied short URL additionally passed actual **desktop and mobile** browser submission, quality selection, preparation, preview and file saving. Both downloaded files were **794,705 bytes**, FFprobe-verified and fully decoded with FFmpeg. This is **six verified file deliveries across two distinct source clips**, not six unique videos. Screenshots: [desktop](snapchat-share-verification/desktop.png), [mobile](snapchat-share-verification/mobile.png).

A second genuine short URL, `https://snapchat.com/t/WhWPtAb9`, found on [Snapchat's public tag page](https://www.snapchat.com/tag/https), returned **HTTP 404**. It was reported as `snapchat_unavailable`; no download was claimed. Story/profile redirects, private/restricted cases, temporary failures and missing exact-ID metadata were verified with controlled fixtures, not represented as successful live downloads or live private-content access.

## Regression and security results

- **43 Snapchat API checks passed**, including creator-qualified paths, full hyphenated IDs, unsupported classification, failed extraction and malicious redirect rejection.
- **52 existing security/provider API checks passed**; private/mixed DNS and SSRF protections remain intact.
- **120 processing/format/audio checks passed**, including real output tests for all 22 unchanged processing operations.
- **58 focused browser regressions passed**, including seven error categories in all 13 languages on desktop/mobile, other downloader workflows, retained Beta status, Story route exclusion and the full existing SEO browser suite.
- **2 live Spotlight browser workflows passed**, with genuine downloaded files.
- **29 publication checks passed**. TypeScript, ESLint, Ruff and one production Webpack build passed.
- Existing sitemap count: **1,020**, matching the approved indexable inventory. No SEO content, styling, provider status or security protections were removed.

Local final server: `http://127.0.0.1:3000`; production build `5Ebdy2Pcw9etr2mX4Qy45`; isolated local API at port 8001. No external deployment. [Machine-readable verification](snapchat-share-repair.json) preserves individual samples and results.

## Files changed

- `apps/api/app/security.py`
- `apps/api/app/providers/snapchat.py`
- `apps/api/app/extractor.py`
- `apps/api/tests/test_snapchat.py`
- `apps/web/src/components/downloader.tsx`
- `apps/web/src/locales/snapchat-errors.json`
- `apps/web/e2e/snapchat-share.spec.ts`

Also added this report, its JSON evidence and the two verification screenshots. No changes to processing-engine code, other provider implementations or existing translation publication records.

## Limits

Spotlight remains Beta: success depends on Snapchat exposing the requested public media. Deleted/expired links, Stories, profiles and login-required content do not become downloadable. No claim is made that every Snapchat share link is Spotlight or that every public clip will always remain accessible.
