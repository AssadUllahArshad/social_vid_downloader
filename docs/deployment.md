# Production deployment

This is deployment preparation, not a claim that a live deployment exists. Canonical frontend: `https://socialviddownloader.com`. Keep the current downloader, repository-backed publication system and saved draft inventory. Content generation is `PAUSED_FOR_LAUNCH`.

## Requirements and configuration

Use Node 22, Python 3.12, FFmpeg/FFprobe and system fonts (Debian/Ubuntu: `fonts-dejavu-core fonts-noto-core`), PostgreSQL 17, Redis 7, an HTTPS ingress, private service networking and sufficient temporary disk. Start with one API process, two bounded jobs, at least 2 CPU cores and 4 GB total host memory, then measure actual load. These are initial capacity planning values, not throughput guarantees. Do not start several API workers with independent temporary disks: shared Redis job state must point to the same private media volume.

Copy `.env.example` to a private environment file outside public assets. Set `ENVIRONMENT=production`, `STATE_BACKEND=redis`, a real PostgreSQL connection, private Redis, and a random `IP_HASH_SECRET` of at least 32 characters. Production rejects development database credentials, SQLite state and unsafe secret defaults. Generate secrets with a password manager or `openssl rand -hex 32`; do not paste them into logs or version control. An unset `ADMIN_PROVIDER_TOKEN` disables internal diagnostics; if used, it must be random and at least 32 characters. The browser `/admin/` and `/admin/content/` shells are disabled in production because CMS authentication does not exist.

`NEXT_PUBLIC_SITE_URL` must be correct before the web build. `API_INTERNAL_URL` is server-only and must point to the private API. Analytics/Sentry variables remain reserved and inactive; no trackers are loaded. Do not promise that setting an ID enables an integration.

## Limits and storage

Defaults: 200 MiB aggregate input/final media budget, 1,800-second source duration, 90-second extraction, 180-second preparation, two concurrent jobs, 1 GiB temporary-media capacity, 600-second sessions/files, 120-second metadata cache. Download admission reserves up to twice the file budget per active slot for inputs plus merged output. Storage can become busy before the full disk budget is reached; this is intentional. Allow filesystem overhead and use a dedicated volume/quota plus disk alerts. Expired media is swept every 30 seconds after the file TTL plus processing grace. Invalid output and failed media generation remove their directories immediately. Completed files are retained during the short download/preview window, not deleted after the first delivery. A restart resumes sweeping orphaned job directories.

Configure positive limit environment variables from `.env.example`; do not raise concurrency without matching CPU, memory and disk. Extraction slots are process-local while download slots are Redis-backed. Multi-worker global extraction capacity therefore scales with worker count; use one process initially and ingress limits.

## Build and migrate

1. Take a verified database backup and retain the previous application/content release.
2. Install locked JS and Python dependencies: `npm ci`, then `pip install -r apps/api/requirements.txt` in an isolated Python environment.
3. From `apps/api`, run `alembic upgrade head` only. Seeding is a separate optional initialization step, never part of normal production migrations. Seed is idempotent and preserves existing editorial records; it deliberately retires unsupported legacy Snapchat Story records. Never reset the database. Published web articles are rendered from the repository's reviewed content files, not automatically from relational seed drafts.
4. Run `npm run lint`, `npm test`, API tests, TypeScript and `npm run build --workspace apps/web -- --webpack`. Verify exact release evidence in `final-launch-report.md`.
5. Container deployment uses `apps/web/Dockerfile` and `apps/api/Dockerfile`, both non-root. API includes FFmpeg and Node for yt-dlp extraction. Build/run images on a Docker-enabled host; Docker is unavailable in the current development environment.
6. `docker-compose.yml` is a local/staging setup. It now accepts runtime production settings and limits, but it is not a hardened production orchestrator. Explicitly set all production credentials; replace local defaults, restrict networks, apply CPU/memory/disk limits, configure restart policy and monitoring. Inspect `docker compose config` without publishing its secret values.

## Start and private services

API: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers --no-access-log` under a supervisor. No development reload or debug. Next standalone: the Docker image runs `node apps/web/server.js`; its standalone output includes static/public assets. For a native standalone installation, copy `.next/static` and `public` into the corresponding standalone application paths before starting its `server.js`. Configure supervisor restart, graceful shutdown and bounded process resources.

Verify private `/health` for liveness and `/ready` for Redis, FFmpeg and the migrated `seo_pages` table. Local SQLite readiness is development evidence only. PostgreSQL/Redis outages must not silently fall back to a local store. Keep ports 5432, 6379 and 8000 private. Public API traffic goes through Next's allowlisted `/api/v1/` and `/api/processing/` proxies; CORS wildcard access is not required.

## HTTPS ingress and client identity

Example ingress fragment after installing certificates (replace paths with real certificate paths):

```nginx
server {
  listen 80;
  server_name socialviddownloader.com www.socialviddownloader.com;
  return 301 https://socialviddownloader.com$request_uri;
}
server {
  listen 443 ssl;
  server_name socialviddownloader.com;
  ssl_certificate /etc/ssl/socialvid/fullchain.pem;
  ssl_certificate_key /etc/ssl/socialvid/key.pem;
  client_max_body_size 8k;
  location ^~ /api/processing/ {
    client_max_body_size 200m;
    proxy_pass http://127.0.0.1:3000;
    proxy_set_header Host socialviddownloader.com;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For "";
    proxy_request_buffering off;
    proxy_buffering off;
    proxy_read_timeout 650s;
    access_log off;
  }
  location / {
    proxy_pass http://127.0.0.1:3000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For "";
    proxy_read_timeout 650s;
    proxy_buffering off;
  }
}
```

Configure a separate HTTPS www server with one redirect to apex. Restrict direct frontend access to this ingress, then set `TRUSTED_CLIENT_IP_HEADER=x-real-ip`. Set API `TRUSTED_PROXY_IPS` to the exact frontend socket peers, not arbitrary public networks. If Cloudflare is in front, restore the real client address only after validating its maintained ingress IP ranges. Do not trust arbitrary forwarded headers. Check distinct client rate buckets from the final deployment. Enable `ENABLE_HSTS=1` before the final build only after TLS works. Public pages receive CSP, frame restrictions, nosniff, referrer and permissions headers; CSP permits inline framework/JSON-LD scripts but no third-party trackers by default.

## Logging, monitoring and launch

Disable raw Uvicorn access logs. Application logs contain outcomes and processing durations rather than source links, cookies or tokens. Configure edge/supervisor logs to omit query strings, IP addresses and token-bearing URL paths; rotate and retain diagnostic logs for a documented short period (initial recommendation seven days). Alert on readiness failures, sustained provider failures, disk usage and job saturation. Provider details remain behind a bearer-protected internal endpoint; never publish raw logs.

Review `backups.md`, `rollback.md`, `domain-launch.md`, `cloudflare-production.md`, `search-console-launch.md` and `launch-checklist.md`. Configure the real contact mailboxes, backups and monitoring before accepting traffic. Run `AUDIT_ORIGIN=https://socialviddownloader.com node scripts/audit-publication.mjs` after deployment and verify draft isolation. Re-test public providers from the deployment network: local bot challenges do not prove global availability or success at a different host.

## Current manual handoff

Use [manual-deployment.md](manual-deployment.md) for the ordered procedure and [environment.md](environment.md) for all settings. Production Compose uses both docker-compose.yml and docker-compose.production.yml. Migrations never seed automatically. Production browser admin remains disabled; provider diagnostics require the optional private token. The current local readiness result is in manual-deployment-readiness-report.md; earlier live-domain reports are historical and do not impose an external DNS/TLS prerequisite on code readiness.
