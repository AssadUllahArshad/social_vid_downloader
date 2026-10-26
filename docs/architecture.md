# Architecture

`apps/web`: Next.js App Router, TypeScript, React, Tailwind CSS, server-rendered pages. The shared downloader component handles analysis, source formats, preparation, preview and file saving. A bounded same-origin server proxy keeps the API origin out of the browser. No API secrets are bundled.

`apps/api`: FastAPI with provider registry, strict URL allowlist, Redis-backed rate limiting, structured errors, SQLAlchemy models and Alembic migrations. The Phase 2 engine fetches media through a pinned, allowlisted transport; see [engine details](download-engine.md). PostgreSQL holds the future editorial inventory. Redis keys contain HMAC-derived peer identities with a 60-second TTL, not raw IPs. Proxy headers are disabled in the container entrypoint; behind a trusted ingress, configure exact trusted proxy addresses and prevent direct API access before enabling forwarded client identities.

`content/pages/tools.json`: initial reviewed route inventory and database seed input. Frontend metadata and page routes use this inventory; CMS database edits do not affect the web app yet. Package directories reserve shared contracts, SEO policy, configuration, and UI extraction when reuse warrants it.

Publication defaults to draft/noindex. Migration includes 10 entity tables. Seed writes homepage, platforms, tools, SEO pages, clusters, and primary keyword mappings without overwriting editorial changes. User/admin secrets are never seeded. Real author setup is required for article publication.

Production uses repository-backed reviewed publication records (268 indexable pages at the current freeze), not database-generated CMS publication. The production admin web shell is disabled; optional read-only provider diagnostics use a private token. Jobs run within the API with bounded concurrency and Redis leases, not a separate durable queue worker. Interrupted jobs expire rather than resume. Content generation is PAUSED_FOR_LAUNCH. CMS login/editing, durable queue recovery and localization are outside this release. See manual-deployment-readiness-report.md for current verification and warnings.

Stack references used for setup: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation) and [FastAPI container deployment](https://fastapi.tiangolo.com/deployment/docker/).

## Multilingual release

English lives in the `(english)` static route group. Explicit locale directories have independent static root layouts with correct HTML lang/dir and share the localized core renderer and the existing downloader. No request-header locale detection is used. The selected UI dictionary flows through a client context; the selector uses only the small route/language catalog. Translation records and digest/completeness gates are separate from English editorial publication. See multilingual-system.md and multilingual-launch-report.md for current counts and evidence. Content expansion stays paused.
