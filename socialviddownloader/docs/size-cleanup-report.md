# Safe project cleanup — 15 October 2026

**SAFE CLEANUP COMPLETE. Main website source modified: NO.**

Original user estimate: **3.68 GB**. Measured baseline: **3.677 GB** allocated.
Current project: **1.333 GB**. Recovered: **2.343 GB (63.74%)**.
Sizes use the same `du` allocated-block measurement before/after; decimal GB. Inventory was saved before deletion.

Removed: inactive `.next-dev`, old Next compiler caches, old test output, repository Python/test/lint caches, TypeScript incremental cache; replaced the inactive production build with the single successful fresh build. Removed the new HTTP audit route cache only after verification servers stopped. Temporary clean-install environments were also removed; those are not counted as project space recovered.

Preserved: installed node_modules and both Python environments, source/configuration/security, dependency manifests/lockfiles, 1,020 approved URLs, 22 video tools, 13 languages, all editorial records/SEO history, public assets, real secrets, current release, historical evidence, frozen Android source and all four media fixtures. No files moved to backup. Optional future review: `source.mov` (uncertain user-media provenance) and `.venv-phase1` (older environment); both are retained, not cleanup blockers.

Git status: no `.git` exists. No Git reset/clean was used. **466 protected file hashes match before/after**, including original content, application source, manifests and deployment configuration. The snapshot is in `size-cleanup-protected-hashes.json`.

## Verification

- TypeScript, ESLint, Ruff: PASS.
- Publication/SEO tests: 29 PASS; packaging tests: 4 PASS.
- One production Webpack build: PASS, from the extracted release after a clean npm install.
- Python production requirements: clean install PASS; disposable SQLite migration/readiness PASS. Existing databases were untouched.
- HTTP audit: 1,097 public 200 pages, 1,020 indexable, 1,020 sitemap URLs; zero canonical, metadata, schema, link, orphan, robots or sitemap errors.
- Multilingual audit: 506 pages, zero hreflang errors; 13 languages retained.
- Basic smoke: 14 PASS. Desktop/mobile navigation/language smoke: 8 PASS.
- FFmpeg/FFprobe available; API advertises all 22 runtime operations. **No full processing regression suite or new external provider download run is claimed.**
- Clean install/build was local macOS (Node 25.2.0/Python 3.12), not Docker/Linux deployment verification. Documented Node 22 Docker host checks remain manual deployment steps.

## Deployment archive

`releases/socialviddownloader-launch-2026-10-14.tar.gz` — **9,799,371 bytes**. Existing clean archive reused; no duplicate release was generated. All 433 archive files validated; application/content/configuration remain identical. Dependencies, caches, credentials, databases, generated media, test output and Android prototype are excluded. Required production source, lockfiles, requirements, migrations, assets and manuals remain included.

SHA-256: `e621c89664c1dccbfe030b335d778e16f5e86ce5a9ff69b678252f19af1504f5`.

Largest retained directories (allocated):

| Directory | MB |
|---|---:|
| `node_modules` | 542.7 |
| `apps/web/.next` | 431.4 |
| `apps/api/.venv` | 124.0 |
| `docs` | 72.8 |
| `apps/web/test-media` | 64.1 |
| `apps/api/.venv-phase1` | 63.6 |
| `content` | 22.0 |
| `releases` | 10.3 |

Detailed inventory: `size-cleanup-inventory.json`; results: `size-cleanup-report.json`. Original verification reports were not overwritten. No deployment, provider, tool, style, translation or content changes were made.
