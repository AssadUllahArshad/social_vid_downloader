# Oracle $0 launch: operator checklist

Prepared 23 October 2026. No cloud resources or DNS changes have been made.

**Signup update:** the owner has a debit card, not a credit card. Oracle's
[signup instructions](https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-Sign_Up_for_Free_Oracle_Cloud_Promotion.htm)
explicitly allow major-network debit cards that do not require a PIN for this
transaction, even though the form says Credit Card. Acceptance is bank/card
dependent; do not assume signup will work. If unsuitable, this Oracle plan is
conditional, not an actionable hosting commitment. No dependable no-card $0
cloud replacement for this complete media-processing stack has been verified.
Render Free is a demo option only (sleep, ephemeral files, 30-day PostgreSQL).
Running on an existing Linux machine is another option, but electricity,
connectivity, public access and uptime must be accounted for; it is not a
guaranteed zero-cost production substitute.

## Read this first

Use one Oracle Always Free A1 VM for the entire application, with Cloudflare
**DNS only** and free Let's Encrypt HTTPS. Expected hosting bill: $0 within the
account's free allowances. Availability and continued free service are not
guaranteed. Existing domain renewal, internet access and card verification holds
are outside that hosting estimate. Do not buy a VPS or upgrade an account if A1
is unavailable: wait, try an eligible availability domain, or revisit the plan.

## 1. Account and cost boundary (owner action)

- Create your own Oracle account with accurate identity/billing details and MFA.
  Card verification may be required. Never send card details or passwords here.
- Choose the home region carefully; confirm A1 eligibility/capacity before relying
  on it. No region's capacity was checked in an authenticated account.
- Stay on the free account. Do not opt into Pay As You Go or rely on trial credit.
- Select `VM.Standard.A1.Flex`, at most **2 OCPU / 12 GB** total across A1 VMs,
  and an Always Free Ubuntu 24.04 ARM64 image. Start with a 50 GB boot disk.
- Review the complete order estimate and the Console's Always Free labels,
  including storage performance, public IP and networking. Stop on any cost or
  ambiguity. This document cannot certify your account's final bill.
- Keep combined boot/block volumes within 200 GB and outbound within 10 TB/month.
  No paid load balancer, NAT gateway, managed database, marketplace image,
  extra disk, paid monitoring or paid Cloudflare plan is needed.
- Configure available quota controls and cost/usage notifications. Alerts are
  not hard spending caps. Track transfer and volume use yourself as well.
- Oracle may reclaim idle instances; do not manufacture traffic to evade this.
  Keep encrypted backups outside Oracle and a recovery copy of the release.

Official sources checked for this plan:
[Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm),
[signup/card/no-SLA conditions](https://www.oracle.com/cloud/free/faq/).

## 2. Actual application topology

Internet :443 -> host Nginx -> loopback :3000 Next.js -> private :8000 FastAPI.
Compose runs `postgres`, `redis`, `migrate`, `api`, `web`. Use one API process.
PostgreSQL 17 and Redis 7 are local containers, without public database access.
The existing Dockerfiles install Python 3.12, Node 22 and FFmpeg/FFprobe/fonts.
Native ARM builds and required codecs remain an on-host release gate.

The frontend requires a Node server: dynamic API proxies stream uploads and
outputs. Do not change it to static export. No separate durable queue worker
exists: Redis tracks state/leases; API tasks launch bounded subprocesses.
An interrupted job expires rather than resuming; users must submit again.
Do not scale the API to multiple replicas without redesigning cancellation,
shared media access and recovery.

Initial limits: one job, 200 MiB file, 30-minute input, 180-second processing
budget, 600-second link lifetime, approximately 1 GiB application media budget.
Sweeps run every 30 seconds with a timeout grace period; TTL is not an exact
filesystem deletion deadline. PostgreSQL uses `postgres-data`, temporary media
uses `media-data`, and Redis is deliberately ephemeral/noeviction.

Cloudflare's free proxy accepts at most 100 MB request bodies. Keep apex/www
**DNS-only** to preserve the existing 200 MiB upload feature. This means direct
origin traffic and no Cloudflare proxy/WAF protection for launch. Do not silently
lower upload limits. [Cloudflare limits](https://developers.cloudflare.com/workers/platform/limits/)

## 3. Prepare the selected release locally

The workspace has no `.git` metadata. Its original remote/branch/commit cannot
be recovered here. Archive hashes provide release identity until the owner
identifies the authoritative GitHub repository; do not guess a clone URL.

The October 14 archive was internally verified, but differs from this workspace:
Windows extraction compatibility fixes, generated Next types and React
19.3.0 -> 19.3.1 in the lockfile. Keep the current fixes; do not deploy the old
archive while assuming it contains today's deployment improvements.

Use a fresh output name with the existing packager after final checks:

```powershell
python -B scripts/package-release.py releases/socialviddownloader-oracle-2026-10-23.tar.gz
```

Preserve the old archive. Copy the new archive and its `.sha256` to a new,
empty release directory on the VM using SCP over your verified SSH connection.
Do not upload `.env`, virtual environments, node_modules, screenshots or media.

## 4. Prepare the VM (after account/instance selection)

Verify `/etc/os-release` is Ubuntu 24.04 and `uname -m` reports `aarch64`.
Use SSH keys and a non-root sudo operator account; test a second SSH login before
disabling password/root login. Keep the OCI console recovery path available.
Restrict TCP 22 to your real operator IP/CIDR in OCI security rules. Allow TCP
80/443 publicly; never add public rules for 3000/8000/5432/6379. Configure the
host firewall too, preserving existing OCI image rules. Docker published ports
can bypass UFW: retaining loopback-only Compose bindings is essential.

Install Docker Engine, Buildx and Compose plugin from the
[official Ubuntu repository instructions](https://docs.docker.com/engine/install/ubuntu/).
Install Nginx, Certbot with Nginx integration, Python 3, OpenSSL and curl:

```sh
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx python3 openssl curl
docker version
docker compose version
```

Docker access is root-equivalent; use a dedicated trusted operator. Do not
install or remove conflicting Docker packages blindly on a reused machine.
No host Python media dependencies are needed when using the API image.

## 5. Configure and build (commands run in extracted source root)

```sh
sha256sum -c socialviddownloader-oracle-2026-10-23.tar.gz.sha256
tar -xzf socialviddownloader-oracle-2026-10-23.tar.gz
cd socialviddownloader
umask 077
cp deploy/production.env.example .env
chmod 600 .env
```

Generate two independent values with `openssl rand -hex 32` privately and place
them in `POSTGRES_PASSWORD` and `IP_HASH_SECRET`; leave `ADMIN_PROVIDER_TOKEN`
blank. Do not paste values into chat or logs. Review the example's remaining
non-secret variables; it is the authoritative complete list. Compose constructs
`DATABASE_URL` and fixes `REDIS_URL`, `API_INTERNAL_URL`, `MEDIA_ROOT` internally.
Do not assume arbitrary `.env` keys are forwarded.

Use `ip route` to check that `172.30.90.0/24` is unused. If it conflicts, change
the ingress overlay subnet, web IP and `TRUSTED_PROXY_IPS` together. Trust only
the exact web peer; Nginx must overwrite `X-Real-IP`.

```sh
dc() { docker compose --project-name socialviddownloader -f docker-compose.yml -f docker-compose.production.yml -f deploy/compose.ingress.yml "$@"; }
dc config --quiet
dc build
dc up -d --wait postgres redis
dc exec -T postgres pg_isready -U socialvid -d socialvid
dc exec -T redis redis-cli ping
dc run --rm migrate
dc up -d --wait api web
dc ps -a
```

Check that the one-shot migration exited with code 0. Migrations run
`alembic upgrade head`; never seed/reset a
production database. Stop on errors. Check `dc logs --tail=100 api web` privately.
Do not print `dc config` without `--quiet`: resolved configuration contains secrets.

```sh
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/ready
curl --fail -o /dev/null http://127.0.0.1:3000/
dc exec -T api python -m yt_dlp --version
dc exec -T api ffmpeg -version
dc exec -T api ffprobe -version
docker stats --no-stream
df -h
```

Health failures mark containers unhealthy; Docker does not automatically restart
an unhealthy-but-running container. Monitor readiness and investigate failures.
Restart policies cover exited processes. Five-minute API shutdown grace permits
bounded work to finish; crashes still interrupt jobs.

## 6. DNS and HTTPS

Preserve existing MX/TXT and mail records. At Cloudflare Free, set apex A to the
actual VM IPv4 and www CNAME to the apex, both DNS-only. Add AAAA only after IPv6
is configured and tested. Never paste a placeholder IP into DNS.

On a new host with no existing website, obtain the first certificate with port
80 free (stop Nginx temporarily only on this dedicated new host):

```sh
sudo systemctl stop nginx
sudo certbot certonly --standalone -d socialviddownloader.com -d www.socialviddownloader.com
```

Copy `deploy/nginx/socialviddownloader.conf.example` into the enabled site config.
Replace certificate placeholders with the actual fullchain/privkey under
`/etc/letsencrypt/live/socialviddownloader.com/`. Resolve Ubuntu's conflicting
default site deliberately; preserve the unknown-host rejection servers. Keep
the 200m streaming upload location and all trusted identity headers.

```sh
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
sudo certbot certonly --nginx --cert-name socialviddownloader.com --force-renewal -d socialviddownloader.com -d www.socialviddownloader.com
sudo certbot renew --dry-run
```

The one-time Nginx-authenticator renewal replaces standalone renewal so automatic
renewals can run without stopping the site. Check the saved renewal authenticator
and enabled Certbot timer. Run the forced renewal once, not in a repeated script.
Only after successful HTTPS/renewal set `ENABLE_HSTS=1`, then `dc build web` and
`dc up -d --no-deps --wait web`.

## 7. Backups, monitoring and rollback

Before upgrades and daily, use `pg_dump --format=custom` as in
[manual-deployment.md](manual-deployment.md). Encrypt the dump and configuration
with your existing backup tool, then download over SSH to your own computer or
existing storage. No new paid backup service is assumed. Retain 7 daily and
4 weekly copies; a VM-only dump is not a backup. Do not back up media or Redis.
Automatic off-host transfer needs the owner's chosen destination and credentials.
Until configured, the backup requirement is incomplete; confirm each manual copy.

Practice restoration without touching production:

```sh
umask 077
mkdir -p ../private-backups
# Refuse to overwrite an earlier backup; choose a fresh filename if it exists.
(set -C; dc exec -T postgres pg_dump -U socialvid -d socialvid --format=custom > ../private-backups/pre-release.dump)
test -s ../private-backups/pre-release.dump
dc exec -T postgres createdb -U socialvid socialvid_restore_check
dc exec -T postgres pg_restore -U socialvid -d socialvid_restore_check --exit-on-error < ../private-backups/pre-release.dump
dc exec -T postgres psql -U socialvid -d socialvid_restore_check -c 'SELECT version_num FROM alembic_version; SELECT count(*) FROM seo_pages;'
```

Use an unused isolated database name; record original/restore row counts and a
representative row comparison. Do not rerun against an existing database or drop
production data. Restore verification is pending until executed.

Monitor private `/ready`, Docker health, `df -h`, `docker stats`, Redis memory
and Docker disk use. Alert before disk falls below 10 GB, above 80% host disk use,
on repeated 5xx, saturation, failed backups or certificate renewal. Docker logs
are now bounded; Nginx access logs are disabled to avoid capability-token logging.
Configure host journald/Nginx error-log retention and demonstrate alert delivery.
No monitoring subscription is needed; automatic alert delivery is not configured.

Keep previous source and images. Drain work before upgrades. Restore matching
previous web/API images/content on rollback using the same Compose project and
volumes; do not automatically downgrade migrations. If DB restore is required,
verify a separate restored DB and approve the write-loss window first. Never run
`down -v`, automatic pruning, or a seed/reset command on production.

## 8. Launch gates (all pending on the actual VM)

| Check | Required result |
|---|---|
| Native ARM build | All images/dependencies install; intended FFmpeg codecs available |
| HTTP/HTTPS | Valid TLS, apex canonical redirects, unknown hosts rejected |
| Private dependencies | PostgreSQL/Redis healthy; `/ready` 200; external ports closed |
| Website | Desktop/mobile homepage, article, tools, Arabic/Urdu and assets work |
| SEO | Existing production/sitemap scripts pass with matching release |
| Real download | Owner-authorized source produces playable file, actual provider failure stays truthful |
| FFmpeg | Remove Audio output has video/no audio, verified with FFprobe |
| Job handling | Status, failure, cancellation and saturation behave correctly |
| Upload size | 150-190 MiB valid input works; oversized input safely rejected |
| Expiry | Links expire; failed/abandoned files swept after retention/grace |
| Resource load | One worst-case job stays bounded; disk/RAM monitored |
| Restart | Readiness returns; interrupted jobs expire and can be resubmitted |
| Security | Private/metadata/DNS/redirect SSRF rejected; forged client headers ineffective |
| Recovery | Encrypted off-host backup restored and content/config recovered |

Use `node scripts/smoke-production.mjs https://socialviddownloader.com` and
`node scripts/smoke-sitemap.mjs https://socialviddownloader.com` from an operator
machine with Node 22. Optional live samples: `python3 scripts/smoke-providers.py
--help`. Do not submit third-party media without permission. Health alone is not
proof that the product works.

## If Oracle is unavailable

For an absolute $0 budget, wait or pause the launch; Render's sleeping free
instances and expiring database are not a dependable substitute. Cloudflare
Workers cannot execute the long-running media workload. A paid VM is a separate
decision requiring an approved final invoice; do not automatically purchase one.
