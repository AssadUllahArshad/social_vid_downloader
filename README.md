# SocialVidDownloader

Current hosting plan: [Oracle $0 launch checklist](docs/oracle-zero-cost-launch.md).
Local deployment changes are prepared; cloud build, media tests, backup restoration
and public launch remain pending. No hosting account or paid resource was created.

Next.js / FastAPI downloader with one normalized backend for YouTube Video/Shorts, Facebook Video/Reels, Instagram Video/Reels, and TikTok. Extraction and file generation are implemented; upstream availability varies. Snapchat Spotlight is now available in beta, alongside the hardened TikTok downloader. Instagram/Snapchat Stories and WhatsApp remain disabled. See [live verification](docs/phase-3-status.md) for observed successes and failures.

22 bounded upload-based video tools now share the processing API and a 13-language frontend. See [current tool release verification](docs/video-tools-final-report.md) and [manual deployment](docs/manual-deployment.md). Saved SEO candidates are tracked separately; deferred articles are not published.

## Development

Requires Node 22+, Python 3.12+, FFmpeg and FFprobe on PATH. PostgreSQL/Redis are the default services.

```sh
cp .env.example .env
npm install
python3.12 -m venv apps/api/.venv
apps/api/.venv/bin/pip install -r apps/api/requirements-dev.txt
docker compose up -d postgres redis
cd apps/api
.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
cd ../..
npm run dev:all
```

Open http://127.0.0.1:3000. API http://127.0.0.1:8000, development docs `/docs`. Replace `IP_HASH_SECRET` with a random secret.

Without Docker, explicitly use the development-only SQLite state store:

```sh
cd apps/api
STATE_BACKEND=sqlite .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run `npm run dev` separately. This mode runs the downloader without PostgreSQL/Redis; CMS database operations still need PostgreSQL. SQLite state is rejected outside development. Redis errors never silently switch storage backends.

## Verification

```sh
npm run build
npm run lint
npm test
apps/api/.venv/bin/pytest apps/api/tests
apps/api/.venv/bin/ruff check apps/api
npx playwright install chromium
npm run test:e2e
```

Media tests require FFmpeg/FFprobe and generate genuine local video fixtures. They validate extraction contracts, all eight integrated tool types, real merges/files/ranges, stale UI responses, and hostile outbound destinations. Controlled fixtures do not establish live upstream availability.

`docker compose up --build` includes FFmpeg, FFprobe, Node, bundled yt-dlp JavaScript components, migrations (without automatic seeding). This is a development deployment. Before production, configure TLS, secret management, resource limits, trusted ingress, storage, monitoring, and PostgreSQL migration checks. Container builds were not verified on this machine because Docker is unavailable.

See [engine and API](docs/download-engine.md), [architecture](docs/architecture.md), and [Phase 1 evidence](docs/phase-1-status.md). Tool pages retain independent UX/SEO content and use the same downloader component and API. CMS authentication/editing and public search indexing remain later phases.

## Manual production handoff

Content expansion is PAUSED_FOR_LAUNCH. Start with [manual deployment](docs/manual-deployment.md), [environment](docs/environment.md) and [local readiness report](docs/manual-deployment-readiness-report.md). Production admin web UI is disabled; optional diagnostics use an operator-generated bearer token. Basic smoke: `node scripts/smoke-production.mjs https://socialviddownloader.com`; authorized provider smoke: `python3 scripts/smoke-providers.py --help`. No external service or DNS configuration is performed automatically.

## Multilingual launch

The core product now supports 13 languages with static locale URLs, translated shared controls and RTL layouts. English URLs are preserved. See [multilingual system](docs/multilingual-system.md) and [current multilingual readiness report](docs/multilingual-launch-report.md). Run `node scripts/audit-translations.mjs` against a local production server, or set AUDIT_ORIGIN for your manually deployed release, to verify all localized canonicals and reciprocal alternates. Existing candidate expansion remains paused.

### Local frontend modes

Use `npm run dev` for port 3000 while editing. Development artifacts live in `apps/web/.next-dev`, separately from production `.next` output. Do not run a production build over the directory used by an active `next start` or standalone server: it can retain old HTML references after hashed CSS/JS files are replaced. Stop that server before rebuilding, or serve a complete immutable release copy containing its matching `public` and `.next/static` assets. After a release switch, reload already-open tabs to obtain the matching assets.
