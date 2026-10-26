# Manual handoff — 18 October 2026 P1 + P2 release

This is a source release, not a prebuilt Docker image. No external deployment was performed. Use the accompanying `release-2026-10-18-p1-p2.json` for this release's inventory and verification results. It supersedes the historical **counts and archive name only** in `manual-deployment.md`, `launch-checklist.md` and `launch-freeze.json`: the current inventory contains **1,027 indexable URLs**, including the Facebook account-deletion article and 246 approved link additions (188 P1 contextual links plus 58 P2 guide links across 30 English tool pages). Packaging does not change application, content or deployment configuration. The approved P2 mappings and English-only renderers are included; CTA replacements and localized P3 additions are excluded. All 532 article digests remain unchanged and valid.

The older `scripts/smoke-sitemap.mjs` intentionally reads the historical 1,020-URL freeze. Do not use its old expected set to judge this release or remove the seven newer approved URLs. Use the current-inventory check below. Preserve all previous releases and backups.

## Deployment order

1. Transfer `socialviddownloader-release-2026-10-18-p1-p2.tar.gz` and its `.sha256` companion to a new release directory. Run `sha256sum -c socialviddownloader-release-2026-10-18-p1-p2.tar.gz.sha256`, extract it and enter `socialviddownloader`. Verify every entry of `RELEASE-SHA256.json` using the Python command in `docs/manual-deployment.md`.
2. On the Linux host, install Docker/Compose v2, host Nginx, Certbot, OpenSSL and Node 22 for smoke commands. Copy `deploy/production.env.example` to an owner-only `.env`. Generate separate PostgreSQL and IP-hashing secrets. Keep Redis/API/database ports private and verify the exact ingress proxy IP/subnet. The API Docker image installs FFmpeg/FFprobe; do not copy local virtual environments or media.
3. Define `dc` below. Run `dc config --quiet`, then `dc build` (the web Dockerfile uses Webpack). Start PostgreSQL and Redis, check readiness, back up any existing database, run migrations, and start API/web. Never reset/reseed or use `down -v`.
4. Manually configure apex/www DNS. Obtain the HTTPS certificate **before enabling the supplied TLS Nginx configuration**. Set its certificate paths, preserve upload limits and trusted identity headers, run `nginx -t`, then enable/reload Nginx. Verify certificate renewal before enabling HSTS. Follow the existing manual for standalone versus existing-host ACME handling.
5. Run the smoke commands below. Check desktop/mobile, Arabic/Urdu and a real upload → processing → download. Verify the downloaded media with FFprobe. Check cancellation and expiry on the deployed host without weakening resource or abuse protections.
6. Schedule encrypted off-host PostgreSQL backups, retain the matching release and encrypted secrets separately, and test restoration in an isolated database. Verify ownership and submit `https://socialviddownloader.com/sitemap.xml` manually in Search Console. No WhatsApp Status retrieval, QR login or private-content support is advertised by this release.

```sh
dc() { docker compose --project-name socialviddownloader -f docker-compose.yml -f docker-compose.production.yml -f deploy/compose.ingress.yml "$@"; }
dc config --quiet
dc build
dc up -d --wait postgres redis
dc exec -T postgres pg_isready -U socialvid -d socialvid
dc exec -T redis redis-cli ping
# Take the documented database backup before migrations on an existing installation.
dc run --rm migrate
dc up -d api web
dc exec -T api ffmpeg -version
dc exec -T api ffprobe -version
curl --fail http://127.0.0.1:8000/ready
# Complete DNS, certificate, Nginx and renewal setup before these HTTPS checks.
node scripts/smoke-production.mjs https://socialviddownloader.com
curl --fail https://socialviddownloader.com/api/processing/capabilities/
curl -I http://socialviddownloader.com/
curl -I https://www.socialviddownloader.com/
```

Current-release sitemap check, run from the extracted release root:

```sh
node --input-type=module - <<'JS'
import {readFileSync} from 'node:fs';
const origin='https://socialviddownloader.com';
const inventory=JSON.parse(readFileSync('docs/release-2026-10-18-p1-p2.json'));
async function xml(url){const r=await fetch(url,{redirect:'manual',signal:AbortSignal.timeout(30000)});if(r.status!==200||!r.headers.get('content-type')?.includes('xml'))throw Error('Sitemap response: '+url);return r.text();}
const locs=s=>[...s.matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
const root=await xml(origin+'/sitemap.xml');let urls=[];
if(root.includes('<sitemapindex')){for(const shard of locs(root)){const u=new URL(shard);if(u.origin!==origin||!u.pathname.startsWith('/sitemaps/'))throw Error('Unexpected shard');urls.push(...locs(await xml(shard)));}}else urls=locs(root);
const expected=new Set(inventory.indexablePaths.map(p=>origin+p));const actual=new Set(urls);
if(actual.size!==urls.length||actual.size!==expected.size||[...actual].some(u=>!expected.has(u)))throw Error('Current-release sitemap mismatch');
console.log('PASS: '+actual.size+' exact approved canonical sitemap URLs');
JS
```

Docker image startup, PostgreSQL/Redis production readiness, HTTPS, DNS, backups and Search Console are operator checks on the deployment host. Local smoke uses the existing development API state store; it does not certify those external services.
