# Indexability repair and publication audit

## Final inventory

All 24 current public content routes were reviewed. The former blanket Phase 1 noindex rule is replaced by an explicit reviewed publication inventory. Homepage: indexable before and after. Every other route previously declared `noindex, follow` in page-level or dynamic metadata; CMS status did not control rendering.

| URL | Type | Previous status / cause | Should index? | Final status / action |
|---|---|---|---|---|
| `/` | home | Indexable; default robots permission | YES | Index, follow — Completed public tool directory. |
| `/youtube-video-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/youtube-shorts-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/instagram-video-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/instagram-reels-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/instagram-story-downloader/` | tool | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Unsupported downloading; limitation page remains noindex. |
| `/facebook-video-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/facebook-reels-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/tiktok-video-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/snapchat-spotlight-downloader/` | tool | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Enabled public-link tool with source-dependent access. |
| `/whatsapp-status-downloader/` | tool | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Unsupported downloading; limitation page remains noindex. |
| `/youtube/` | hub | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Useful supported-tool selection and platform-specific access guidance. |
| `/facebook/` | hub | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Useful supported-tool selection and platform-specific access guidance. |
| `/instagram/` | hub | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Useful supported-tool selection and platform-specific access guidance. |
| `/tiktok/` | hub | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Useful supported-tool selection and platform-specific access guidance. |
| `/snapchat-downloader/` | hub | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Useful supported-tool selection and platform-specific access guidance. |
| `/whatsapp/` | hub | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — No supported public tool; limited access guidance only. |
| `/about/` | trust | Noindex; explicit Phase 1 page metadata | YES | Index, follow — Completed factual service explanation. |
| `/guides/` | guides | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Empty landing page; no published guides. |
| `/blog/` | blog | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Empty landing page; no published articles. |
| `/contact/` | trust | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Operator and support contacts are placeholders. |
| `/copyright/` | trust | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Launch contact and takedown process are unfinished. |
| `/privacy-policy/` | trust | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Production retention and operator details need review. |
| `/terms/` | trust | Noindex; explicit Phase 1 page metadata | NO | Noindex, follow — Brief draft terms require operator and editorial review. |

## Architecture and safeguards

`content/pages/publication.json` is the reviewed inventory of existing canonical public routes, with titles, descriptions, indexability and editorial reasons. `pageMetadata()` and the sitemap consume the same inventory. Unknown slugs still return 404; the inventory does not create routes by itself. Publication is an explicit reviewed decision, not inferred from tool availability alone. Tools retain source-dependent access restrictions and beta labels. Hub copy is platform-specific; supported hubs now explain link selection and limitations. About explains actual service behavior and links to the supported hubs.

The root layout supplies the metadata base and site-wide defaults; reviewed page metadata supplies unique descriptions/titles, canonical paths and explicit robots directives. No environment-based indexing switch, middleware noindex rule, or X-Robots-Tag header was found. Trailing slashes remain canonical. The `/snapchat/` redirect remains excluded; all Snapchat Story keyword routes remain absent. Only indexable reviewed routes enter the sitemap. No placeholder dates or fake publication timestamps are added.

Robots permits public content and render assets. It excludes admin, API, internal, search, temporary, preview and framework-error paths. No CSS/JS blocking rule is present. Noindex content remains crawlable so robots metadata can be seen.

## Content sources and CMS boundary

- Static TSX: homepage, About, Contact, Copyright, Privacy, Terms, Guides and Blog landings (8 pages).
- JSON-driven dynamic route: 10 tools from `content/pages/tools.json`, plus six platform hubs; Snapchat hub uses `/snapchat-downloader/` rather than the redirect alias.
- PostgreSQL currently supplies zero frontend page routes. `SEOPage`, `BlogPost`, FAQ, tool and keyword models exist, but there is no public CMS page reader or published-content routing endpoint.
- The 12 seed definitions are draft database records (homepage plus 11 JSON entries, including the Snapchat hub); they do not create extra routes and their draft flag does not hide the separately authored frontend routes. Do not mark these duplicates published merely to match frontend metadata.
- Future large editorial inventory should use PostgreSQL as its content source with a shared published-page resolver used by rendering, metadata, canonicals and sitemap. Only published, reviewed, indexable canonical records should resolve to SEO pages; drafts/previews require separate access and noindex. Existing curated routes need an explicit ownership/migration mapping to prevent duplicate CMS pages. Unique intent/slug/canonical constraints already exist in the schema.
- CMS publication/routing is not currently implemented or represented as operational. No mass content or new CMS-generated routes were created during this repair. That integration remains a prerequisite to the 5,000-page expansion.

## Database diagnosis

The configured fallback is PostgreSQL on localhost:5432, database `socialvid`, using psycopg. Neither a root `.env` nor an explicit process `DATABASE_URL` is configured. The local PostgreSQL connection is unavailable. `docker-compose.yml` defines PostgreSQL 17 with a persistent volume, Redis, and a migration service running Alembic and the seed. Docker and PostgreSQL executables are absent from this environment; no installed PostgreSQL Homebrew formula was found. Safe startup is therefore unavailable without installing/provisioning a service. No existing database was reset or altered.

Migrations exist (`0001_initial.py`). A disposable temporary SQLite database successfully ran `alembic upgrade head`, the seed twice, and `alembic check`. It held 12 draft/nonindex SEO records and 11 tool records, with no schema drift. This validates migration/seed logic locally, not PostgreSQL-specific execution or the state of a production database. The downloader’s development SQLite job state is separate from this CMS database and is not a substitute for it.

## Validation

Fresh localhost HTTP audit: 24 public pages; 15 indexable; 9 noindex; 15 sitemap URLs. Zero canonical errors, conflicting X-Robots-Tag headers, broken public URLs, missing indexable URLs, invalid/noindex sitemap entries, or duplicate sitemap URLs. All 24 titles, descriptions and H1 values are unique. Full rendered evidence is saved in `docs/indexability-audit.json`.

API: 166 passed. Browser: 32 passed (desktop and mobile, including all existing downloader/audio regressions and the full SEO inventory). Content inventory: 4 passed. TypeScript and ESLint pass. Production build passes with `next build --webpack`: Turbopack failed in this environment while its CSS worker attempted to bind a local port, including on the elevated retry. This is recorded separately from application validation.

Remaining infrastructure limitation: the actual PostgreSQL migration/seed state cannot be verified until a database service is provisioned. No claim is made that CMS publication/routing or the future 5,000-page system is operational. No downloader engine code changed, and no next feature phase was started.
