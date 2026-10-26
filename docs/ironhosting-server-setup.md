# IronHosting: server preparation and deployment

Prepared from the owner's terminal transcript, 26 October 2026. These commands are instructions for the owner to execute; the assistant has not connected to or modified the server.

## Confirmed starting state

- Server: `108.165.128.66`, SSH TCP 22, root key login works.
- Ubuntu 24.04.5 LTS, x86_64, 3.8 GiB RAM, 2 GiB swap, about 29 GiB free on root.
- Nginx, Certbot, its Nginx plugin, Python 3, curl and OpenSSL installed.
- Docker is not installed. A kernel update requires reboot.
- No deployment user, firewall setup, Docker installation, release upload, DNS, TLS or application deployment was demonstrated in the transcript.

Run each numbered block separately; stop and share the error if anything fails. Do not paste the whole document as one script. Commands marked SERVER run after SSH login. Commands marked LOCAL run in Windows Git Bash. Preserve the attachment and existing keys.

## 1. SERVER: create a deployment user

Keep the current root session open. Confirm the server host fingerprint through the provider console if not already done:

```sh
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

Compare with the fingerprint observed by your SSH client. Then create a new operator account; use a strong local password for sudo, not a chat-shared password:

```sh
adduser deploy
usermod -aG sudo deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
test ! -e /home/deploy/.ssh/authorized_keys && install -m 600 -o deploy -g deploy /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
```

If `deploy` or its authorized-keys file already exists, inspect it and preserve existing access instead of overwriting it. The copy contains public keys only. The private key stays on your PC.

## 2. LOCAL: verify the new login in a second Git Bash window

```bash
ssh -o IdentitiesOnly=yes -i /c/Users/lenovo/.ssh/ironhosting_socialvid deploy@108.165.128.66
```

In that NEW server session:

```sh
whoami
sudo -v
```

Expected: `deploy`, then successful sudo authentication using the password chosen with `adduser`. Keep this session and the root session open until access is confirmed. For each additional PC, create its own key pair locally and append only its public-key line to `/home/deploy/.ssh/authorized_keys`; do not reinstall the OS or copy private keys between computers.

## 3. SERVER as deploy: firewall, updates and reboot

```sh
sudo apt-get update
sudo apt-get install -y ufw ca-certificates curl gnupg nano unattended-upgrades
sudo ufw status verbose
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
sudo ufw status verbose
```

This initial policy permits SSH from any address for access from multiple PCs. Key authentication remains essential. Check provider firewall rules too: permit TCP 22/80/443; do not expose 3000/8000/5432/6379. Do not reset an existing firewall or remove unknown rules. Open another deploy SSH connection now to verify new connections work, not just the existing one.

Update the fresh server, review any package prompts, and reboot:

```sh
sudo apt-get upgrade -y
sudo systemctl enable --now unattended-upgrades
sudo reboot
```

The disconnect is expected. Reconnect as deploy using step 2 after the server returns. Verify `uname -r`, `free -h`, `swapon --show` and `df -h`. Do not recreate swap: 2 GiB already exists. OS security updates are enabled by Ubuntu configuration; inspect with `sudo apt-config dump | grep -E 'APT::Periodic|Unattended-Upgrade'` and verify later runs rather than assuming every package will update automatically.

## 4. SERVER: harden SSH only after verified deploy access

Do this after reboot and a fresh successful deploy/sudo login. Keep an authenticated deploy session open and provider console available.

```sh
sudo nano /etc/ssh/sshd_config.d/00-socialvid.conf
```

Add:

```text
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
```

Validate syntax AND effective values before reload; an existing earlier directive or Match block may override expectations:

```sh
sudo sshd -t
sudo sshd -T -C user=deploy,host=socialviddownloader,addr=127.0.0.1 | grep -E '^(pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|permitrootlogin) '
```

Expected: public-key yes, password no, keyboard-interactive no, root login no. Resolve conflicting settings before continuing. Then:

```sh
sudo systemctl reload ssh
```

Verify another NEW deploy SSH login succeeds before closing old sessions. If it fails, use the still-open session to fix/revert the new drop-in and validate/reload; never disable your only working access.

## 5. SERVER: install Docker from its official repository

For the verified Ubuntu 24.04 amd64 host. First inspect any conflicting packages:

```sh
dpkg -l docker.io docker-compose docker-compose-v2 podman-docker containerd runc 2>/dev/null
ls -l /etc/apt/sources.list.d/
```

The transcript showed no Docker command. If conflicting packages or a Docker repository are already present, inspect before proceeding; do not blindly uninstall or duplicate configuration. On this fresh host:

```sh
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo docker run --rm hello-world
```

Use `sudo docker`; membership in the docker group would grant root-equivalent access and is unnecessary for this guide. No Docker Desktop, Snap Docker, paid control panel or host FFmpeg installation is needed. The API image installs FFmpeg/FFprobe and runtime dependencies.

Reference: [Docker Ubuntu instructions](https://docs.docker.com/engine/install/ubuntu/). Docker-published ports can bypass UFW; preserving the project's loopback bindings is required.

## 6. SERVER: prepare private directories and bounded system logs

```sh
sudo install -d -m 750 -o deploy -g deploy /srv/socialviddownloader
mkdir -p /srv/socialviddownloader/releases /srv/socialviddownloader/backups
chmod 700 /srv/socialviddownloader/backups
sudo install -d -m 755 /etc/systemd/journald.conf.d
sudo nano /etc/systemd/journald.conf.d/socialvid.conf
```

Add:

```ini
[Journal]
SystemMaxUse=200M
RuntimeMaxUse=100M
```

Then:

```sh
sudo systemctl restart systemd-journald
sudo systemctl is-active docker nginx
sudo ufw status
free -h
df -h
sudo docker system df
```

Nginx's Ubuntu logrotate configuration should remain enabled. Do not globally overwrite Docker daemon configuration; project containers already have bounded logs. Do not run automatic image/volume pruning.

**At this point the host prerequisites are prepared.** Application deployment below is separate and must pass runtime validation.

## 7. LOCAL: create and upload a fresh source release

Use Git Bash on your PC, not the server:

```bash
cd /d/Personal/Projects/socialviddownloader/socialviddownloader
python -B scripts/package-release.py releases/socialviddownloader-ironhosting-2026-10-26.tar.gz
```

If the filename already exists, choose a fresh suffix and use it consistently below; the packager refuses overwrites. It validates archive structure/checksums, not a production build. Do not use the older October 14 archive. The new archive includes [the 4 GB overlay](../deploy/compose.small-vm.yml).

```bash
scp -i /c/Users/lenovo/.ssh/ironhosting_socialvid releases/socialviddownloader-ironhosting-2026-10-26.tar.gz releases/socialviddownloader-ironhosting-2026-10-26.tar.gz.sha256 deploy@108.165.128.66:/srv/socialviddownloader/releases/
```

Do not upload local `.env`, private keys, dependencies, test media or entire working directories.

## 8. SERVER: extract into a fresh release directory

```sh
cd /srv/socialviddownloader/releases
sha256sum -c socialviddownloader-ironhosting-2026-10-26.tar.gz.sha256
mkdir ironhosting-2026-10-26
tar -xzf socialviddownloader-ironhosting-2026-10-26.tar.gz -C ironhosting-2026-10-26
cd ironhosting-2026-10-26/socialviddownloader
```

Stop if `mkdir` reports an existing directory; choose another name instead of extracting over an existing release. This extracted project directory is the SERVER working directory for all subsequent `dc` commands. Verify internal file hashes:

```sh
python3 - <<'PY'
import hashlib, json, pathlib
for name, digest in json.load(open('RELEASE-SHA256.json')).items():
    assert hashlib.sha256(pathlib.Path(name).read_bytes()).hexdigest() == digest, name
print('Release hashes verified')
PY
```

## 9. SERVER: configure private production secrets

```sh
umask 077
cp -i deploy/production.env.example .env
chmod 600 .env
nano .env
```

Generate two independent values privately using `openssl rand -hex 32`, and enter them as `POSTGRES_PASSWORD` and `IP_HASH_SECRET`. Do not paste values into chat. Preserve:

```text
ENVIRONMENT=production
STATE_BACKEND=redis
NEXT_PUBLIC_SITE_URL=https://socialviddownloader.com
ENABLE_HSTS=0
MAX_CONCURRENT_JOBS=1
TRUSTED_CLIENT_IP_HEADER=X-Real-IP
TRUSTED_PROXY_IPS=172.30.90.10
```

Leave `ADMIN_PROVIDER_TOKEN` blank. Keep existing file/time/cleanup limits. Check `ip route` and `sudo docker network ls` before using `172.30.90.0/24`; if it overlaps, change the ingress subnet, web static IP and exact trusted IP together. Do not trust an entire subnet or wildcard.

## 10. SERVER: validate, build sequentially and start

Define this helper in each deployment shell, while inside the extracted project directory:

```sh
dc() { sudo docker compose --project-name socialviddownloader -f docker-compose.yml -f docker-compose.production.yml -f deploy/compose.ingress.yml -f deploy/compose.small-vm.yml "$@"; }
dc config --quiet
df -h
dc build api migrate
dc build web
```

Stop if a command fails. Use sequential builds before running media jobs. Resource settings are runtime ceilings, not Docker build memory limits. The 4 GB overlay budgets API 1536 MiB, web 768 MiB, PostgreSQL 512 MiB and Redis 256 MiB, about 3 GiB steady state, plus a separate 256 MiB one-shot migration limit. It enforces one job and limits API CPU to 1.5 cores. This is a starting configuration, not proof the full media workload fits. If a build exhausts RAM/disk, inspect before retrying; do not repeatedly build or automatically delete data.

```sh
dc up -d --wait postgres redis
dc exec -T postgres pg_isready -U socialvid -d socialvid
dc exec -T redis redis-cli ping
dc run --rm migrate
dc up -d --wait api web
dc ps -a
curl --fail http://127.0.0.1:8000/health
curl --fail http://127.0.0.1:8000/ready
curl --fail -o /dev/null http://127.0.0.1:3000/
dc exec -T api ffmpeg -version
dc exec -T api ffprobe -version
sudo docker stats --no-stream
df -h
```

Expected: PostgreSQL ready, Redis PONG, migration succeeds, API/web healthy, HTTP 200, binaries available. On failure inspect `dc logs --tail=100 api web` privately. Never run resolved `dc config` without `--quiet` in shared output because it contains secrets. Never seed/reset the production DB or use `down -v`.

## 11. DNS: existing domain provider or Cloudflare dashboard

Preserve MX/TXT/mail records. Set:

| Type | Name | Value | Cloudflare proxy |
| --- | --- | --- | --- |
| A | `@` | `108.165.128.66` | DNS only |
| CNAME | `www` | `socialviddownloader.com` | DNS only |

Replace conflicting web A/AAAA records deliberately; do not leave an old AAAA pointing elsewhere. Do not add IPv6 until tested. No nameserver change is required if your existing DNS provider can manage these records. Initially avoid Cloudflare's proxy because of the project's 200 MiB upload requirement.

SERVER checks after DNS propagation:

```sh
getent ahostsv4 socialviddownloader.com
getent ahostsv4 www.socialviddownloader.com
```

Both should reach this server. If certificate validation fails, check public DNS including AAAA/CAA, firewall and domain ownership rather than retrying issuance repeatedly.

## 12. SERVER: issue HTTPS and install the existing ingress

On this fresh dedicated server with only the default Nginx site:

```sh
sudo certbot certonly --nginx -d socialviddownloader.com -d www.socialviddownloader.com
sudo certbot certificates
```

Enter your real email and agree to certificate terms. The Nginx authenticator obtains certificates without permanently configuring the application site; later renewals use that authenticator. Inspect the certificate paths output instead of assuming a filename if a prior certificate exists.

Prepare a copy of the project config:

```sh
cp -i deploy/nginx/socialviddownloader.conf.example /tmp/socialviddownloader.nginx.conf
nano /tmp/socialviddownloader.nginx.conf
```

Replace every `/REPLACE/WITH/fullchain.pem` and `/REPLACE/WITH/privkey.pem` with the ACTUAL certificate paths reported by Certbot, usually under `/etc/letsencrypt/live/socialviddownloader.com/`. Preserve streaming limits, exact identity headers, private diagnostic paths and disabled access logs. Then:

```sh
sudo cp -i /tmp/socialviddownloader.nginx.conf /etc/nginx/sites-available/socialviddownloader
sudo ln -s /etc/nginx/sites-available/socialviddownloader /etc/nginx/sites-enabled/socialviddownloader
```

Review `ls -l /etc/nginx/sites-enabled/`. On this dedicated new server only, if `/etc/nginx/sites-enabled/default` is the standard symlink to the default site, unlink that symlink to resolve the duplicate default server:

```sh
sudo unlink /etc/nginx/sites-enabled/default
sudo nginx -t
```

The original default file remains in sites-available. If validation fails, fix the config before reload; the running configuration remains active. Do not unlink another site's configuration. If this symlink already does not exist, skip the unlink command.

```sh
sudo systemctl reload nginx
sudo systemctl enable --now certbot.timer
sudo certbot renew --dry-run
```

Create a renewal deployment hook so Nginx loads renewed certificates:

```sh
sudo install -d -m 755 /etc/letsencrypt/renewal-hooks/deploy
sudo nano /etc/letsencrypt/renewal-hooks/deploy/socialvid-nginx
```

Contents:

```sh
#!/bin/sh
set -eu
/usr/sbin/nginx -t
/usr/bin/systemctl reload nginx
```

```sh
sudo chmod 755 /etc/letsencrypt/renewal-hooks/deploy/socialvid-nginx
sudo /etc/letsencrypt/renewal-hooks/deploy/socialvid-nginx
systemctl list-timers certbot.timer
curl -I https://socialviddownloader.com/
curl -I http://socialviddownloader.com/
curl -I https://www.socialviddownloader.com/
```

Expect HTTPS apex to respond successfully and HTTP/www to redirect to it. Reference: [Certbot Nginx authenticator and renewal](https://eff-certbot.readthedocs.io/en/stable/using.html#nginx).

After HTTPS and renewal work, set `ENABLE_HSTS=1` in `.env`, then `dc build web` and `dc up -d --no-deps --wait web`. Do this before opening to public processing traffic. Enabling HSTS requires the web image rebuild because it is a build argument.

## 13. LOCAL: smoke checks and actual media tests

From the matching local project checkout with Node 22:

```bash
node scripts/smoke-production.mjs https://socialviddownloader.com
node scripts/smoke-sitemap.mjs https://socialviddownloader.com
```

Use desktop/mobile browsers to verify home, article, downloader, all intended processing capabilities and Urdu/Arabic layouts. Test owner-authorized provider URLs and inspect actual playable files. Test Remove Audio with a valid MP4 and check the output has video and no audio using FFprobe.

Also test 150-190 MiB input, oversized rejection, cancellation, expiry and cleanup, controlled saturation at one job and interrupted jobs after restart. Watch `sudo docker stats`, `free -h`, `df -h` and provider traffic. CPU sharing and provider-IP blocking remain real runtime risks. Existing backend tests/full container builds have not been executed by the assistant on this host.

Externally confirm 3000/8000/5432/6379 are closed. Inspect `sudo ss -lntup` on the server for loopback-only application/dependency listeners. Verify client-IP trust and existing SSRF guards. Do not turn on production admin pages.

## 14. SERVER + LOCAL: backup and restoration before launch

In the project directory on SERVER, define `dc` from step 10 if necessary:

```sh
umask 077
backup_file="/srv/socialviddownloader/backups/socialvid-$(date -u +%Y%m%dT%H%M%SZ).dump"
(set -C; dc exec -T postgres pg_dump -U socialvid -d socialvid --format=custom > "$backup_file")
test -s "$backup_file"
printf '%s\n' "$backup_file"
```

Stop if dump fails. Create a separate restore-check database with an unused name (do not rerun against an existing database):

```sh
dc exec -T postgres createdb -U socialvid socialvid_restore_check_20261026
dc exec -T postgres pg_restore -U socialvid -d socialvid_restore_check_20261026 --exit-on-error < "$backup_file"
dc exec -T postgres psql -U socialvid -d socialvid_restore_check_20261026 -c 'SELECT version_num FROM alembic_version; SELECT count(*) FROM seo_pages;'
dc exec -T postgres psql -U socialvid -d socialvid -c 'SELECT version_num FROM alembic_version; SELECT count(*) FROM seo_pages;'
```

Compare row counts/schema and representative reads. Do not drop production or assume row counts alone prove a perfect restore.

Encrypt the dump and configuration separately using an existing trusted encryption tool. A built-in option, with a strong passphrase entered interactively, is:

```sh
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -in "$backup_file" -out "$backup_file.enc"
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -in .env -out /srv/socialviddownloader/backups/environment-20261026.enc
```

Do not overwrite an existing encrypted backup; use fresh names on later runs. Keep passphrases in your password manager, separately from backups. Download the exact encrypted files over SCP from LOCAL; substitute the actual timestamp printed above:

```bash
mkdir -p /d/Personal/SocialVidBackups
scp -i /c/Users/lenovo/.ssh/ironhosting_socialvid deploy@108.165.128.66:/srv/socialviddownloader/backups/ACTUAL-DUMP-FILENAME.dump.enc /d/Personal/SocialVidBackups/
scp -i /c/Users/lenovo/.ssh/ironhosting_socialvid deploy@108.165.128.66:/srv/socialviddownloader/backups/environment-20261026.enc /d/Personal/SocialVidBackups/
```

Retain the source archive and checksum locally too. Verify an encrypted copy decrypts and restores using a private temporary location before relying on it. Schedule daily encrypted off-host database backups with failure monitoring after choosing an available destination and secure credential storage. Until scheduled transfer is configured and tested, do a confirmed daily manual copy; backup automation is not complete. See [backup requirements](backups.md). Do not put encryption passphrases in crontab or chat.

## 15. Operations and rollback

Keep 7 daily/4 weekly backups off-host. Check readiness, disk (keep at least 5 GiB free), swap pressure, failed jobs, certificate expiry and provider bandwidth; alert before 80% disk/transfer. A long-running shell check is not automatic monitoring. Do not enable paid overages or services without reviewing cost.

```sh
dc ps -a
curl --fail http://127.0.0.1:8000/ready
sudo docker stats --no-stream
sudo docker system df
df -h
free -h
sudo journalctl -u docker --since today --no-pager -n 50
```

When upgrading, take a verified backup and preserve the prior source/images. Use the same Compose project and volumes. Drain media work first; do not build while serving heavy jobs. A rollback needs matching images/content and schema compatibility, not automatic migration downgrades. Never `down -v`, reset/reseed or automatically prune volumes. See [rollback](rollback.md).

The server is ready for public launch only when real media, security, resource, renewal and off-host restoration checks pass. Working SSH or a healthy homepage alone is not deployment acceptance.
