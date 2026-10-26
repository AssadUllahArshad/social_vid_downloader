# Monthly hosting decision and setup checklist

Research date: 26 October 2026. Budget: no more than USD 5 paid now and each month; no annual or quarterly prepayment. Owner has a debit card. No purchase, account creation, server benchmark, support conversation or deployment was performed for this report.

## Decision

**Do not buy ByteHosty on the evidence currently available.** Its advertised specifications could support an experiment, but its homepage FAQ lists cryptocurrency payments, and its refund policy excludes cryptocurrency from cash refunds. Debit-card acceptance is unverified. The provider's track record, ownership and actual server performance have not been independently established. This is insufficient evidence to entrust the owner's only hosting budget to it; it is not proof of fraud.

**No fully qualified, dependable host for the complete existing application was established within the strict USD 5 monthly total.** Several advertised plans meet the base-price constraint, but payment, tax, workload permission or reliability remain unresolved. Do not turn an advertised price into a purchase recommendation until those gaps are resolved.

The most useful next lead is **IronHosting Iron Standard 4 GB at USD 4.99/month**, conditional on written workload permission, debit-card acceptance and an invoice within budget. It is a lead, not an endorsement or a confirmed better provider. Its terms restrict sustained CPU/network use and high-throughput relays, relevant to a public downloader. It does not yet pass this project's purchase gate.

## ByteHosty findings

| Question | Evidence and implication |
| --- | --- |
| Genuine monthly price? | Earlier inspected checkout offered 4 GB, 2 vCPU, 30 GB NVMe, one IPv4 at USD 4.99 monthly. Checkout could not be refreshed during this research. Price/stock remain subject to confirmation. |
| Debit-card payment? | [Homepage FAQ](https://bytehosty.com/) lists Bitcoin, Ethereum and USDT. [Privacy policy](https://bytehosty.com/privacy-policy) describes a cryptocurrency processor. Card logos are not evidence that this customer's debit card will work. |
| Refund protection? | [Refund policy](https://bytehosty.com/refund-policy) advertises 48 hours for eligible first KVM orders, but cryptocurrency is refundable only as account credit. This conflicts with the broad original-method refund wording; request clarification before payment. |
| Reliability promise? | [Terms](https://bytehosty.com/terms-of-service) state a 99.2% monthly network availability target, with exclusions and conditional credits. At 30 days, 0.8% is about 5 h 46 min; this is arithmetic, not measured downtime. |
| CPU/network suitability? | Terms permit throttling/suspension for abusive extended CPU use. Unmetered transfer has fair-use limits without a quantified sustained allowance on the inspected pages. |
| Backups? | Included backup availability is service/node dependent. Independent backups remain the customer's responsibility. |
| Who operates it? | The previously inspected checkout footer names ByteHosty LLC at a Wyoming address. The inspected [imprint](https://bytehosty.com/imprint) gives a brand and contact links without independently verifiable ownership detail. Incorporation and ownership were not verified against an authoritative company registry. |
| Independent experience? | Exact brand/domain searches and targeted Trustpilot, Reddit and LowEndTalk searches did not surface useful attributable customer history. This establishes a research gap, not that no customers or reviews exist. Do not confuse ByteHosty with similarly named hosts. |

No authenticated checkout, payment acceptance, cash refund, support response time, status history, assigned datacenter, IP reputation or actual media workload was tested. Website claims about owned hardware and DDoS protection are provider claims, not independently validated results.

## Alternatives screened

Prices below are published base prices, not certified final invoices. Tax, bank fees, setup costs and current stock must be checked. No payment method is assumed to work for the owner.

| Provider/plan | Advertised terms | Result for this application |
| --- | --- | --- |
| [IronHosting Iron Standard](https://www.ironhosting.net/vps/) | USD 4.99 monthly, 4 GB, 2 vCPU, 35 GB NVMe, 2.5 TB transfer, IPv4 | Conditional lead only. [Terms](https://www.ironhosting.net/tos/) restrict sustained resource use and high-throughput relays; bandwidth can incur additional charges. Payment/total and downloader permission unconfirmed. A community provider listing establishes presence, not reliability. |
| [Cloudnium Dallas Dal-2](https://portal.cloudnium.net/cart/dallas--tx----kvm-vps/) | USD 4.99 monthly, 4 GB, 2 vCPU, 30 GB, 2 TB, IPv4 | No confident recommendation. A small review sample and older first-person complaints raise concerns; neither establishes current performance. Final checkout and payment terms unverified. |
| [HostEONS Gigabit VPS 3](https://hosteons.com/kvm_vps.php) | USD 5 monthly, 2 GB, 2 fair-share cores, 25 GB, 3 TB, IPv4 | Insufficient memory headroom for the current full-stack plan without substantial compromises and testing. Site advertises debit cards, but that does not fix the resource issue. |
| [InterServer](https://www.interserver.net/vps/affordable-vps-hosting-provider.html) | VPS slices from USD 3/month; published [slice comparison](https://www.interserver.net/vps/wordpress.html) shows 2 GB for USD 3 and 4 GB for USD 6 | 2 GB is too constrained for this deployment recommendation; 4 GB exceeds budget. WordPress template is evidence of slice pricing, not the product to order for this app. |
| [ServerCheap 4 GB](https://servercheap.com/) | USD 3/month equivalent, billed USD 9 quarterly | Excluded: exceeds amount available now. |
| [RackNerd 4 GB special](https://www.racknerd.com/specials/) | USD 59.99 annually | Excluded: annual prepayment. |
| [Hetzner CX23](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/) | Published revised USD 6.49/month before IPv4/tax | Excluded: exceeds budget. |
| [VPS Mart Express Linux](https://www.vps-mart.com/ram/4gb) | 4 GB/60 GB; promotional prices with selectable billing cycles; shared IPv4 | Not qualified. Need actual one-month renewal price and confirmation that the shared-IP reverse proxy supports 200 MiB streaming, long requests and correct client identity. Existing direct-IP ingress cannot be assumed compatible. |
| [S4Hosting Starter](https://s4hosting.com/kvm-vps) | Advertises USD 4.99 and a one-month option, 4 GB/1 vCPU/50 GB | Not qualified: actual checkout, payment, location and track record not established. One CPU and fair-use throttling need media tests. |

Review evidence: [Cloudnium Trustpilot profile](https://www.trustpilot.com/review/cloudnium.net) contained only one review, insufficient for a reliable statistical judgment. [LowEndTalk customer discussion](https://lowendtalk.com/discussion/comment/3763686/) contains older complaints and provider responses, not proof of present service. [LowEndSpirit registered providers](https://lowendspirit.com/discussion/registeredproviders) lists Iron Hosting; registration is not an uptime audit. Older similarly named Minecraft hosts are not treated as proof of the current IronHosting operator's history.

## Step 1: resolve purchase conditions without spending

Use the provider's official contact form or support ticket. Send this yourself; no messages were sent on your behalf:

> I need a VPS for SocialVidDownloader.com, a small public video downloader and processor using Docker Compose, Next.js, FastAPI, PostgreSQL, Redis, yt-dlp and FFmpeg. Initially one media job at a time, 200 MiB maximum input, 180-second processing budget and automatic temporary-file cleanup. Is this specifically permitted on your 4 GB monthly plan? Please state sustained CPU limits, transfer limits and whether overages can be disabled with a hard cap. I am in Pakistan and have a debit card: can you accept it directly? Please confirm the complete initial and renewal monthly amount, including tax/setup/payment fees, minimum deposit, exact datacenter, IPv4, Ubuntu 24.04 availability and refund method. My total available is USD 5, with no annual/quarterly prepayment. Please provide a test IP and public status-history link.

Buy only if the response confirms the workload, price, direct payment, no larger deposit and acceptable limits. Check the bank's international-payment fee too: a USD 4.99 invoice is not automatically a USD 4.99 bank debit. Request the renewal total, not a first-month coupon alone. Do not buy cryptocurrency just to make this recommendation work.

For a qualifying plan choose monthly, Ubuntu 24.04 LTS 64-bit, included IPv4, no control panel, no paid management or resource upgrades. Retain invoice/terms/support confirmation and note the exact refund deadline. A 30-35 GB disk needs disciplined image/log retention; 40-60 GB would be preferable at the same total.

## Step 2: requirements before server setup

- Access to existing domain DNS and a working account email; enable account MFA if available.
- Actual server IPv4, OS, SSH port/user and console recovery access. Do not send passwords, private keys or payment details in chat.
- A local SSH public key. In Windows PowerShell, use `ssh-keygen -t ed25519` only if you need a new key; choose a fresh filename and passphrase, preserving existing keys. Upload only the `.pub` key.
- A release from the current source, not the old October 14 archive. Current source includes later hardening. Identify the authoritative GitHub repository if available; do not guess its URL.
- An existing off-host backup destination, such as your own computer, with encryption and sufficient space.

The remaining steps assume a fresh dedicated Ubuntu 24.04 KVM server with its own public IPv4. They are proposed procedures, not executed work. Shared-IP/NAT hosts require a separate verified ingress design.

## Step 3: inspect and secure the fresh server

Log in using the provider's instructions; verify its SSH host fingerprint through its console. Inspect before installing:

```sh
cat /etc/os-release
uname -m
free -h
df -h
ip route
sudo ss -lntup
```

Confirm approximately 4 GB RAM, expected disk and architecture. Create an unprivileged sudo deployment account, install your public key and verify a second SSH session before disabling password/root login. Keep console recovery available. Restrict SSH to your operator IP where practical; expose only SSH and TCP 80/443 through both provider and host firewall. Account for IPv6 if enabled. Do not enable a firewall until the actual SSH port is allowed.

Update the OS and install Docker Engine, Buildx and Compose using the [official Ubuntu apt-repository instructions](https://docs.docker.com/engine/install/ubuntu/). Do not remove packages blindly on a reused host. Docker access is root-equivalent. Install Nginx, Certbot with Nginx integration, curl, OpenSSL and Python 3. Node 22 is needed on the operator machine for the supplied smoke scripts, but host Node is not required by the container runtime.

```sh
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx curl openssl python3
docker version
docker compose version
```

Use `sudo docker` if the operator is not authorized for Docker. Configure security updates and bounded system logs. Review whether 1-2 GiB swap is suitable with the provider and disk allowance; swap is emergency headroom, not usable FFmpeg capacity. No swap configuration has been executed or validated.

## Step 4: prepare the release and 4 GB resource profile

See [manual deployment](manual-deployment.md) for the existing application procedure. Before packaging, the deployment implementation needs a reviewed small-VM overlay. Current production ceilings total 4.25 GiB before host overhead and are unsuitable as a memory budget for a 4 GB machine. Ceilings are not reservations, but simultaneous peaks can exhaust the host.

Suggested starting ceilings, **not performance-tested**: API 1536 MiB, web 768 MiB, PostgreSQL 512 MiB and Redis 256 MiB (3 GiB total), leaving about 1 GiB for the OS and other services. Keep one media job and existing file/time limits. Native media subprocesses must fit inside the API ceiling. If representative jobs fail or thrash, do not call the plan adequate or silently shrink the product's upload contract.

Add these values in a separate reviewed Compose overlay after host selection, preserving the existing health checks, private ports, shutdown grace, log rotation and exact proxy trust. All deployment commands must include this overlay last. No runtime files were changed by this research report.

Build API/migration and web images sequentially before starting the application. Build-time memory is separate from container runtime ceilings. If the Next.js build cannot finish within this host's resources, build matching Linux images on a suitable machine and transfer them; do not build a Windows image for the Linux host. Do not run an image build alongside live transcoding. Leave at least 5 GiB disk headroom and retain only deliberately selected releases/images after review; no automatic destructive pruning.

Once the reviewed overlay and checks are ready, package locally with a fresh name:

```powershell
python -B scripts/package-release.py releases/socialviddownloader-monthly-2026-10-26.tar.gz
```

Copy the archive and generated `.sha256` to a new private release directory over SCP. Never upload local secrets, virtualenvs, node_modules, test media or caches. On the server in that new directory:

```sh
sha256sum -c socialviddownloader-monthly-2026-10-26.tar.gz.sha256
tar -xzf socialviddownloader-monthly-2026-10-26.tar.gz
cd socialviddownloader
umask 077
cp deploy/production.env.example .env
chmod 600 .env
```

Generate two independent secrets privately using `openssl rand -hex 32` and enter them in `POSTGRES_PASSWORD` and `IP_HASH_SECRET`. Leave admin diagnostics disabled. Review [production environment example](../deploy/production.env.example), including `MAX_CONCURRENT_JOBS=1`, site URL and proxy settings. Never print resolved Compose secrets to shared logs.

Confirm `172.30.90.0/24` is unused; otherwise update [ingress overlay](../deploy/compose.ingress.yml) and the exact trusted web IP together. Define the following helper **only after** creating/reviewing the proposed small-VM overlay at the path shown:

```sh
dc() { docker compose --project-name socialviddownloader -f docker-compose.yml -f docker-compose.production.yml -f deploy/compose.ingress.yml -f deploy/compose.small-vm.yml "$@"; }
dc config --quiet
dc build api migrate
dc build web
dc up -d --wait postgres redis
dc exec -T postgres pg_isready -U socialvid -d socialvid
dc exec -T redis redis-cli ping
dc run --rm migrate
dc up -d --wait api web
dc ps -a
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/ready
docker stats --no-stream
df -h
```

Stop on any failure. Migration is `alembic upgrade head`; never seed/reset production. The proposed `deploy/compose.small-vm.yml` does not exist as part of this report and must be implemented before using this helper. Redis tracks ephemeral state, not a durable queue. Interrupted jobs require resubmission. Keep one API process.

## Step 5: domain and HTTPS

Preserve mail/TXT records. Point the apex A record at the actual server IPv4 and `www` CNAME at the apex. Initially use Cloudflare DNS-only. The project's 200 MiB uploads exceed the documented 100 MB Free/Pro proxy request limit; routing through a constrained proxy would change the supported upload behavior. Verify current [Cloudflare connection limits](https://developers.cloudflare.com/fundamentals/reference/connection-limits/) before enabling its proxy. Do not add AAAA until IPv6 routing/firewall/TLS are tested.

For a new dedicated server, temporarily stop Nginx and issue the certificate:

```sh
sudo systemctl stop nginx
sudo certbot certonly --standalone -d socialviddownloader.com -d www.socialviddownloader.com
```

Install [the existing Nginx example](../deploy/nginx/socialviddownloader.conf.example) as the enabled site after replacing certificate placeholders with the issued fullchain and private-key paths. Review conflicting default sites without deleting unrelated configurations. Preserve the streaming upload location and identity headers. Then:

```sh
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
```

Configure renewal with the Nginx authenticator or a verified webroot method so it works while Nginx runs; standalone renewal alone will conflict with the running server. Run `sudo certbot renew --dry-run` and verify the Certbot timer. Enable HSTS only after HTTPS and renewal succeed, then rebuild/recreate web with the same Compose overlays.

## Step 6: prove the product works before public launch

From the matching checkout on an operator machine with Node 22:

```sh
node scripts/smoke-production.mjs https://socialviddownloader.com
node scripts/smoke-sitemap.mjs https://socialviddownloader.com
```

Verify desktop/mobile pages, one article, one downloader, processing pages and Urdu/Arabic. Use owner-authorized source URLs for real provider downloads and check the actual playable output. Datacenter-IP blocking is provider-specific and cannot be solved by promising a VPS works.

Test Remove Audio with a valid local MP4 and inspect the output with FFprobe. Test a valid 150-190 MiB upload, oversized rejection, cancellation, expiry cleanup, controlled busy responses and restart behavior. Observe host/container memory, swap, disk and provider transfer accounting throughout. A successful health check is insufficient.

Confirm PostgreSQL, Redis, API and web ports cannot be reached publicly. Verify forged client headers do not bypass rate limits, unknown hosts are rejected and URL validation blocks private/metadata destinations. Retain existing SSRF controls and disabled production admin pages.

If the server cannot pass these checks at one job without OOM, sustained swap or unacceptable processing failures, the plan has failed acceptance. Do not claim production readiness; use the refund window where applicable or pause deployment.

## Step 7: backups, ongoing cost and rollback

Use [the existing backup procedure](backups.md) and [manual deployment](manual-deployment.md) for daily PostgreSQL custom-format dumps, encryption and off-host copies. Keep the matching source/content archive and encrypted configuration too; omit temporary media and Redis. Test restoration into a separate database and compare schema/representative rows before launch. A provider snapshot is not the only backup.

Monitor private readiness, external HTTPS, failed jobs, disk, memory and monthly transfer. Set alerts before 80% disk/transfer usage, and maintain at least 5 GiB free. At 2.5 TB/month, 100 MB delivered per file gives a rough theoretical 25,000 files before website traffic, uploads/download accounting and retries; this is not a capacity promise. Provider accounting may count ingress as well as egress. Obtain a hard cap if overages would break the budget.

Keep backups on an existing destination to avoid another subscription. Domain renewal is separate from server cost. Monthly renewals and bank fees must remain affordable. Review operating-system updates and certificate/backup failures regularly. No monitoring/backup subscription or scheduled automation has been created.

For rollback preserve the Compose project, volumes, prior images and matching content. Drain jobs before changes. Never run `down -v`, reseed, automatically downgrade migrations or overwrite production with a restore test. See [rollback](rollback.md).

## Current completion status

Completed: public-source research, alternative screening, inspection of existing deployment files, this decision and setup plan.

Not completed: provider qualification, authenticated final invoice, debit-card acceptance, support permission, purchase, small-VM overlay implementation, fresh release creation, full build/runtime/media tests, DNS/TLS configuration, backup restore or deployment. Those cannot be represented as verified results without an actual qualified host.
