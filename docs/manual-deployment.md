# Manual deployment — frozen launch release, 14 October 2026

**Prepared for manual deployment. No external deployment has been performed.** Current gated inventory: **1,097 public pages, 1,020 indexable/sitemap URLs, 22 enabled video utilities, 13 languages**. [Launch freeze](launch-freeze.json) records exact approved paths. Reuse [processing verification](processing-repair-final-report.md) and the later [Snapchat verification](snapchat-share-repair.md). Older reports are historical.

All feature work, SEO authoring and WhatsApp research are frozen. Preserve unfinished candidates. WhatsApp Status URL downloading remains **unsupported**: no login, QR pairing, status retrieval or companion-app promotion. The partial Android project stays locally preserved but is excluded from the deployment archive. Deploy matching application/content/lockfiles together; use the existing **Webpack** build command. Do not reset/reseed the database or switch to Turbopack.

## 1. Prepare the host and transfer the source package

Use a maintained Linux host, an unprivileged deployment account, Docker Engine/Compose v2, host Nginx, Certbot, OpenSSL, Python 3 and Node 22 (for smoke commands). Install FFmpeg/FFprobe on the operator machine if running the optional provider smoke; the API image already installs them and fonts. Budget memory beyond the API's 2 GiB and web's 1 GiB limits for PostgreSQL, Redis and image builds. Keep SSH, 80 and 443 as the only required public ports. Application/database/cache bindings stay loopback.

The prepared `releases/socialviddownloader-launch-2026-10-14.tar.gz` is a **source deployment package**, not an already-built Docker image. It includes dependency manifests and lockfiles; Docker installs dependencies on the host. Local test media, test screenshots, caches, secrets and the unfinished Android prototype are excluded; textual verification reports and saved editorial decisions are retained. Transfer its `.sha256` file alongside it. On Linux:

```sh
sha256sum -c socialviddownloader-launch-2026-10-14.tar.gz.sha256
tar -xzf socialviddownloader-launch-2026-10-14.tar.gz
cd socialviddownloader
python3 - <<'PY'
import hashlib,json,pathlib
for name,digest in json.load(open('RELEASE-SHA256.json')).items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest()==digest, name
print('Release file hashes verified')
PY
```

Keep previous releases and images. Repackage only intentional launch fixes with `python3 scripts/package-release.py /PRIVATE/NEW-release.tar.gz`; never upload local `.env`, caches or media.

## 2. Configure production secrets and exact ingress trust

```sh
umask 077
cp deploy/production.env.example .env
chmod 600 .env
openssl rand -hex 32
openssl rand -hex 32
```

Put the two independent generated values into `POSTGRES_PASSWORD` and `IP_HASH_SECRET` using a private editor; do not paste them into logs. The example enables the existing 22 tools and retains production abuse/resource limits. Optional admin diagnostics stay disabled. See [environment variables](environment.md).

Use the supplied **host Nginx → loopback web → private API** topology. Check `ip route` and `docker network inspect` for conflicts with `172.30.90.0/24`. If occupied, choose an unused private /24 and change both `deploy/compose.ingress.yml` and `.env`'s `TRUSTED_PROXY_IPS` to the web container's exact new IP. Do not use a wildcard or entire subnet as a trusted peer. Nginx overwrites `X-Real-IP`; do not expose port 3000 publicly. Avoid untrusted containers on this network.

Define this shell helper **in each deployment terminal**, and use it for every command:

```sh
dc() { docker compose --project-name socialviddownloader -f docker-compose.yml -f docker-compose.production.yml -f deploy/compose.ingress.yml "$@"; }
dc config --quiet
```

Local preparation validated YAML structure/merge, exact peer trust, private ports and application production settings with in-memory dummy values. Docker/Compose is not installed locally; the `dc config --quiet`, image build and startup above/below are host checks. The production override rejects blank required secrets. Compose builds the PostgreSQL connection from the hex password and sets private API/Redis URLs. It does not forward arbitrary `.env` values. No test-only rate limit of 1000 belongs in production.

## 3. Build images, start PostgreSQL/Redis, migrate, start applications

```sh
dc build
dc up -d --wait postgres redis
dc exec -T postgres pg_isready -U socialvid -d socialvid
dc exec -T redis redis-cli ping
dc run --rm migrate
dc up -d api web
dc ps
dc logs --tail=100 api web
curl --fail --show-error http://127.0.0.1:8000/health
curl --fail --show-error http://127.0.0.1:8000/ready
dc exec -T api ffmpeg -version
dc exec -T api ffprobe -version
```

Wait for dependencies to be healthy before migrating; stop on any failure. Migration runs `alembic upgrade head`, never seeds. Normal API startup may run the idempotent migration service again. PostgreSQL data uses `postgres-data`; private expiring media uses `media-data`. **Never run `down -v` on production.** Redis state is ephemeral; restarting it invalidates sessions/jobs. Run one API process; no separate queue worker exists. Verify image capabilities before opening traffic.

## 4. Configure DNS and HTTPS manually

Point apex and www DNS at the actual host; add AAAA only if IPv6 is configured and served. Obtain a certificate **before installing the supplied TLS configuration**. For a new host without an existing web service, let Certbot use port 80 (stop Nginx if necessary):

```sh
sudo certbot certonly --standalone -d socialviddownloader.com -d www.socialviddownloader.com
```

For a host already serving other sites, use your existing ACME webroot/plugin instead of interrupting them. Copy `deploy/nginx/socialviddownloader.conf.example` into the host's enabled Nginx configuration. Replace both certificate placeholders with the actual files under `/etc/letsencrypt/live/socialviddownloader.com/`. Resolve conflicting default virtual hosts; retain unknown-host rejection. Preserve the separate **200 MiB streaming upload location**, timeouts and overwritten identity headers.

```sh
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

Configure certificate renewal with the chosen ACME method. Standalone renewal needs port 80 free: either configure safe Nginx stop/start renewal hooks or switch to a webroot/Nginx authenticator, then run `sudo certbot renew --dry-run`. Enable `ENABLE_HSTS=1` in `.env` only after HTTPS and renewal work; rebuild/recreate **web only** with `dc build web` and `dc up -d --no-deps web`. This is the intentional deployment-time HSTS build, not a repeated audit.

If using Cloudflare, apply [Cloudflare instructions](cloudflare.md), Full (strict), no API caching and exact trusted edge networks. Do not copy unverified proxy headers into client identity.

## 5. Run essential live smoke checks

From the deployment checkout on the host (Node 22; private API loopback available):

```sh
node scripts/smoke-production.mjs https://socialviddownloader.com
node scripts/smoke-sitemap.mjs https://socialviddownloader.com
curl --fail --show-error https://socialviddownloader.com/api/processing/capabilities/
curl -I http://socialviddownloader.com/
curl -I https://www.socialviddownloader.com/
curl -I https://socialviddownloader.com/
curl -I https://socialviddownloader.com/snapchat-story-downloader/
```

Expect basic smoke PASS, **1,020 exact canonical sitemap URLs with zero missing/extra/duplicates**, HTTPS apex redirects, security headers and Story 404. Capabilities must list the intended enabled operations; do not infer working uploads just from health. The sitemap command checks shard contents, not every page. Reuse the completed full audit unless the deployed release differs or a smoke fails. If needed, run `AUDIT_ORIGIN=https://socialviddownloader.com node scripts/audit-publication.mjs` once against the matching checkout.

In desktop and mobile browsers, verify homepage, one article, one downloader, one processing page and Arabic/Urdu layout/language selection. Check self-canonical, reciprocal hreflang and that WhatsApp remains unsupported/noindex. With an authorized local MP4, upload through **Remove Audio**, preview, download and inspect the actual output:

```sh
ffprobe -v error -show_format -show_streams -of json /path/to/downloaded-output.mp4
```

Confirm video exists and audio is absent. Also try a realistic roughly 50–60 MB clip within the displayed limits, cancel a separate active job, and verify its file is inaccessible. After the configured TTL, old download links must expire and private files must be swept (allow the processing grace period); saved local copies remain yours. Do not clear media manually or raise production limits to make tests pass. Confirm independent visitors do not share the same rate bucket.

Optional live downloader smoke, **one authorized URL per invocation** to avoid artificial load:

```sh
python3 scripts/smoke-providers.py --origin https://socialviddownloader.com --snapchat 'YOUR_AUTHORIZED_PUBLIC_SPOTLIGHT_URL'
```

Repeat with `--youtube`, `--facebook`, `--instagram`, `--tiktok` as applicable. These commands verify actual downloaded files with FFprobe. Do not retain raw sample URLs in public logs; Beta/degraded status stays unchanged.

## 6. Backups, rollback and launch

Before traffic, create a restricted backup directory outside the release and take a custom-format database dump:

```sh
umask 077
mkdir -p ../private-backups
backup_file="../private-backups/socialvid-$(date -u +%Y%m%dT%H%M%SZ).dump"
dc exec -T postgres pg_dump -U socialvid -d socialvid --format=custom > "$backup_file"
test -s "$backup_file"
```

Stop if dump fails. Encrypt with your approved backup system before off-host transfer, schedule daily jobs with monitoring, retain 7 daily/4 weekly, and rehearse `pg_restore` into an **isolated** database. Never restore a test over production. Back up the matching source archive/content and encrypted secrets separately; exclude temporary media and ephemeral Redis sessions. See [backups](backups.md) and [rollback](rollback.md). Preserve the same Compose project/volumes across releases. No destructive downgrade or reseeding during rollback.

Complete [launch checklist](launch-checklist.md), then manually verify the Search Console Domain property with Google's TXT record and submit `https://socialviddownloader.com/sitemap.xml`. Inspect homepage/key tools/articles, monitor indexing and field performance. Do not submit drafts, noindex WhatsApp pages or unsupported Story routes. Google verification and submission remain your actions.
