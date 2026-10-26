# Phase 1 scope and limits

Implemented: monorepo, responsive frontend, unique tool route inventory, platform hubs, draft legal/trust content, blog and guide framework, TypeScript/Tailwind design system, FastAPI routes, structured errors, provider adapters, SQLAlchemy model inventory, migrations and idempotent seeds, Redis rate limits, request-size limits, domain validation and DNS-address checks, Docker configuration, CI and local checks.

The admin route is a truthful unavailable shell, not an authenticated CMS. Extraction, media normalization, quality selection, FFmpeg jobs, signed download URLs, cache, CMS/authentication, CSV keyword import, SEO audit dashboards, sitemap shards, localization, analytics, and deployment belong to subsequent phases. No tool is represented as functional without its actual provider.

Network egress protections must be completed before real media extraction is enabled. The DNS helper does not prevent DNS rebinding by itself. No current endpoint makes an outbound media request.

Frontend verification: production build and TypeScript pass; ESLint passes with no warnings; 2 content inventory tests and 8 Playwright checks pass across desktop and mobile. Screenshots inspected at 1440px and 390px. The production-only npm audit has zero findings. Full npm audit reports five high-severity development-tool findings inherited from ESLint's glob/braces chain; braces 3.0.3 is the latest available release and has no patched version in the registry. Recheck this chain before CI accepts untrusted lint inputs.

Backend verification: 28 pytest cases pass. Disposable SQLite migration upgrade/downgrade, Alembic schema drift check, and idempotent seeds pass (13 SEO pages, 6 platforms, 12 tools, 12 primary keyword mappings, all draft/noindex). The migration compiles to PostgreSQL SQL in offline mode. Actual PostgreSQL/Redis services and Docker images remain unverified because neither those services nor Docker are installed here. Optional Python linting is separately available through requirements-lint.txt; its large package download was deferred. Python syntax compilation passes.

Live verification: API /health returns 200; /ready returns the expected 503 without PostgreSQL/Redis. The browser receives the API’s actual 503 through the bounded runtime proxy. A redirect conflict between frontend trailing slashes and FastAPI was fixed and covered by unmocked proxy regression tests.
