# Production environment

For the documented Docker production topology, copy `deploy/production.env.example` to a private `.env` at the repository root and include `deploy/compose.ingress.yml` with both base and production Compose files. `.env.example` remains a development example; native deployments must explicitly configure production values. Never commit it. Native commands must export its variables into the process; Python's relative env-file lookup alone is not a deployment strategy. Docker Compose reads `.env` for interpolation, and only explicitly listed values enter containers.

## SITE

`NEXT_PUBLIC_SITE_URL=https://socialviddownloader.com` is the canonical, non-www build-time origin. `API_INTERNAL_URL` is the private API origin (`http://api:8000` in Compose, `http://127.0.0.1:8000` native). `ENABLE_HSTS=1` is a build-time option only after HTTPS works. Next standalone uses `PORT=3000`, `HOSTNAME=0.0.0.0`, `NODE_ENV=production`.

## API / DATABASE / REDIS

Set `ENVIRONMENT=production`, `STATE_BACKEND=redis`, `DATABASE_URL=postgresql+psycopg://socialvid:ENCODED_PASSWORD@postgres:5432/socialvid`, `POSTGRES_PASSWORD` to a generated password and `REDIS_URL=redis://redis:6379/0`. Compose constructs DATABASE_URL from POSTGRES_PASSWORD: use a long random hexadecimal password to avoid URL escaping. Native deployments may use local hosts instead. SQLite and development database credentials are rejected in production. Redis must be private, not publicly exposed; failure returns a friendly 503, never silently switches to SQLite.

`LOCAL_STATE_PATH` is development-only. SQLAlchemy uses bounded default pooling with pre-ping; start one API process, then measure before changing process count. Alembic migrations are separate from seed data. Frontend published content comes from the reviewed JSON registry, not CMS database records.

## SECURITY

`IP_HASH_SECRET`: independent random secret of at least 32 characters. `ALLOWED_HOSTS`: comma-separated exact API hostnames, no scheme/port (default domain, loopback and internal `api`). Remove unused hosts; add a separate API hostname only if needed. `CORS_ORIGINS`: exact HTTPS origins, default `https://socialviddownloader.com`; add www only if actually serving it. Wildcards are rejected in production. Nginx must reject unrecognized frontend Host headers.

`TRUSTED_CLIENT_IP_HEADER`: leave empty for a directly exposed frontend; set `X-Real-IP` only when a private ingress overwrites it. `TRUSTED_PROXY_IPS`: exact peers permitted to provide API X-Forwarded-For. The base Compose network uses dynamic addresses. The launch overlay `deploy/compose.ingress.yml` fixes the web peer at `172.30.90.10`, matched by the production environment example. Check subnet conflicts and change both together if needed; without that overlay, leave trusted forwarding disabled or configure another exact trusted peer. Never trust the entire Internet. Until configured, clients may share a rate-limit bucket.

## DOWNLOAD LIMITS

All are configurable: `RATE_LIMIT_PER_MINUTE=20`; `MAX_FILE_BYTES=209715200`; `MAX_STORAGE_BYTES=1073741824`; `MAX_DURATION_SECONDS=1800`; `MAX_CONCURRENT_JOBS=2`; `EXTRACT_TIMEOUT_SECONDS=90`; `DOWNLOAD_TIMEOUT_SECONDS=180`; `SESSION_TTL_SECONDS=600`; `FILE_TTL_SECONDS=600`; `METADATA_CACHE_TTL_SECONDS=120`. Processing reserves twice the maximum file budget per active job. Change budgets consistently with available disk/CPU. `MEDIA_ROOT` must be an owned private writable directory; `FFMPEG_PATH=ffmpeg`, `FFPROBE_PATH=ffprobe` must resolve to installed binaries. Cleanup adds a processing grace period.

## ADMIN

`ADMIN_PROVIDER_TOKEN` is optional, empty disables internal read-only diagnostics. Initialize with `python3 scripts/initialize-provider-admin.py --output /PRIVATE/NEW/provider-admin.env`; transfer the token into secret storage and delete the transport file securely. Existing files are never overwritten. No password account is needed for this release: the production admin web shell is intentionally unavailable (404). The preexisting users table does not implement a CMS login. Token authorization is constant-time, rate-limited and read-only. No browser session/cookie or CSRF mutation exists. Do not expose a supposed CMS login or claim password/session features. Rotate tokens to revoke access.

## CONTACT

Configured operator: Hammad Hassan. Support: support@socialviddownloader.com. Copyright: copyright@socialviddownloader.com. These supplied real details live in `apps/web/src/lib/operator.ts`; changing them requires a reviewed build. No mailbox password is required by the app.

## ANALYTICS / MONITORING

`NEXT_PUBLIC_GA_ID`, `NEXT_PUBLIC_CLARITY_ID`, `SENTRY_DSN` are optional reserved values; this release deliberately loads no tracking SDK. Setting them does not activate analytics. Use private health/readiness and host log monitoring without a paid service. Never send source URLs, tokens or credentials into telemetry.

## Stale media maintenance

The API sweeps automatically every 30 seconds. Optional offline cleanup from the repository root: `PYTHONPATH=apps/api apps/api/.venv/bin/python scripts/cleanup-media.py` with the same exported configuration as the API. It removes only expired 32-hex job directories, adds processing grace and leaves symlinks/active jobs intact. Do not run broad `rm` commands against MEDIA_ROOT.

## Multilingual release

The launch includes static locale pages and the shared translated downloader UI. Verify locale switching, Arabic/Urdu direction, self-canonicals, reciprocal hreflang and the localized sitemap after deployment. English URLs remain unchanged. See [multilingual-system.md](multilingual-system.md) and [multilingual-launch-report.md](multilingual-launch-report.md). Do not resume candidate discovery or content expansion.

## Verified upload processing

`PROCESSING_ENABLED=1` enables the 22 verified operations; set it to 0 for maintenance or to disable uploads. Runtime filter/encoder inspection removes unavailable operations from capabilities and rejects their submission. Docker installs FFmpeg and DejaVu/Noto fonts for text/subtitles. Font glyph support still depends on the host's installed fonts.

`PROCESSING_MAX_UPLOAD_BYTES=209715200` is the web proxy cap (never above 200 MiB); backend MAX_FILE_BYTES may be lower. The capabilities response exposes the smaller usable limit. One job accepts at most eight inputs and their combined size must fit MAX_FILE_BYTES. Dedicated upload streaming avoids buffering media in the Next proxy. Settings requests remain limited to 8 KiB.

Existing Redis, MEDIA_ROOT/_processing, duration, concurrency, timeout and file TTL budgets are reused. Downloaders and processors share job slots and account for active upload reservations. FFmpeg runs with one filter thread, CPU/output/file-descriptor limits and a Linux 1 GiB address-space budget. Jobs run in the API process, not a new durable queue service. Cancellation kills the process group and deletes work files; shutdown signals running jobs; expired records/files are inaccessible and swept. Failed uploads and outputs are removed. No arbitrary paths or remote URLs are accepted.

Use the Nginx processing location in deploy/nginx/socialviddownloader.conf.example: 200 MiB request cap, request/response buffering off, overwritten trusted identity and API access logs off. Keep API/database/cache ports private. Use the current execution state and release report for remaining deferred editorial records.

Processing repair (13 October 2026): FFmpeg decoder threads are bounded per input and encoder threads per output; filter threads remain bounded. H.264 encoding uses `veryfast` within the existing CRF and size limits. Remove Audio copies compatible H.264/HEVC into MP4/MOV or VP8/VP9/AV1 into WebM, retaining encoded video instead of spending the CPU budget re-encoding it. Other codec/container combinations still encode. CPU, wall-clock, output-size, descriptor and Linux address-space limits remain enforced. Structured processing events log hashed correlation IDs, phase, exit code and safe error categories; capability tokens, source names, commands and raw FFmpeg diagnostics are not logged publicly. A timeout or resource rejection is not a successful download.
