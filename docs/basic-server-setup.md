# Basic server setup and Git handoff

Based on the owner's server transcript, 26 October 2026. These commands are instructions, not actions executed by the assistant. Server: 108.165.128.66, Ubuntu 24.04 x86_64, approximately 4 GB RAM, 2 GB swap, 29 GB free. SSH root login works. Nginx, Certbot and its Nginx plugin are installed. Docker is absent and the installed kernel needs a reboot.

## 1. Server: install Git and Docker

Run in the existing root SSH session. Execute blocks one at a time; stop if a command fails. This assumes the fresh host in the supplied transcript, without another Docker installation.

```sh
apt-get update
apt-get upgrade -y
apt-get install -y git ca-certificates curl ufw sudo
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
```

Add Docker's official repository, then install the engine and Compose plugin:

```sh
cat > /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: noble
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker nginx
docker version
docker compose version
docker run --rm hello-world
git --version
```

Source: [Docker's Ubuntu installation instructions](https://docs.docker.com/engine/install/ubuntu/). No host Node.js, PostgreSQL, Redis or FFmpeg installation is needed for the application containers. Smoke scripts can run on the local Node 22 machine. Keep the existing swap.

## 2. Server: create the deployment account

If `id deploy` reports that the user exists, do not recreate it or overwrite its SSH configuration; inspect the existing account first. Otherwise:

```sh
adduser deploy
usermod -aG sudo deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
install -m 600 -o deploy -g deploy /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
```

Choose a strong account password privately; sudo uses it. Keep this root session open. In a SECOND LOCAL GIT BASH window:

```bash
ssh -o IdentitiesOnly=yes -i /c/Users/lenovo/.ssh/ironhosting_socialvid deploy@108.165.128.66
```

In that new server session verify `sudo -v`. Do not change SSH authentication settings until the new account works. Keep provider console access available. Additional PCs can have separate public keys appended later; never distribute private keys.

## 3. Server: basic firewall and reboot

Back in the root session, SSH is port 22 according to the transcript. Allow it before enabling the firewall:

```sh
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status verbose
```

If a provider firewall is enabled, allow these same ports there. Verify another SSH login after enabling UFW. Docker-published ports can bypass UFW, so retain the project's loopback bindings for 3000/8000/5432/6379; do not open those ports publicly.

After successful deployment-user and firewall checks, reboot for the pending kernel update:

```sh
reboot
```

Reconnect as `deploy` after the VM comes back. Verify:

```sh
uname -r
free -h
df -h
sudo docker version
sudo docker compose version
sudo systemctl is-active docker nginx
sudo nginx -t
git --version
```

Use `sudo docker` for now rather than adding accounts to the root-equivalent Docker group. This completes the basic host preparation, not application deployment.

## 4. Local PC: finish replacing the source before Git setup

Finish copying the new code into the actual project root first. Preserve existing deployment improvements and do not copy secrets or delete unknown files. Tell the assistant when copying is finished so the current source, ignore rules and deployment configuration can be checked together.

The current root is `D:/Personal/Projects/socialviddownloader/socialviddownloader`, containing `package.json`, `apps`, `content` and `docker-compose.yml`. The parent directory shown in the earlier Git Bash prompt is not the same folder. If the replacement moves the project, use its actual new root.

Before the first commit, audit ignore rules and the proposed file list. Existing ignores cover node_modules, common Python caches, .env and release archives, but should also be reviewed for local verification output, test media, credentials, database dumps and private keys. Do not blindly run `git add .` on this workspace. The repository must retain required public website assets and non-secret configuration examples.

The intended sequence after that audit is:

1. Initialize a `main` branch in the actual root.
2. Set the owner's real Git author name/email, preferably locally for this repository.
3. Review files and secret exclusions, stage intended source/configuration/content, inspect the staged diff, and commit.
4. Create an EMPTY PRIVATE GitHub repository, without generated README/license/gitignore.
5. Add its actual URL as origin and push main after GitHub authentication.

Do not put a GitHub token in a command URL. The VPS login key is not automatically a GitHub authentication key. Do not commit .env, private keys, backups, temporary media, node_modules or build output. No local Git initialization, commit or push has been performed by this guide.

## 5. Server: access the private repository

Once the actual repository exists, create a SEPARATE read-only GitHub deploy key while logged in as `deploy`:

```sh
ssh-keygen -t ed25519 -f ~/.ssh/socialvid_github -C socialvid-server-readonly
cat ~/.ssh/socialvid_github.pub
```

If that path already exists, decline overwrite and inspect it first. For unattended Git pulls a key without a passphrase is an operational option; restrict it to this one read-only repository. Add only the public key in GitHub repository Settings > Deploy keys; leave write access OFF. Protect the private key on the server. Verify GitHub's host fingerprint against its official documentation at first connection; do not bypass host checking.

Then use the ACTUAL repository SSH URL, replacing OWNER/REPOSITORY below (these are placeholders, not a discovered repository):

```sh
mkdir -p ~/apps
GIT_SSH_COMMAND='ssh -i /home/deploy/.ssh/socialvid_github -o IdentitiesOnly=yes' git clone git@github.com:OWNER/REPOSITORY.git ~/apps/socialviddownloader
```

Use the same `GIT_SSH_COMMAND` for subsequent pulls, or configure this identity in the server's SSH config. Keep production secrets only in the server checkout's ignored .env. Never overwrite local server changes with an automatic Git reset.

## 6. Application deployment follows source review

After the updated source and private repository are ready:

- Recheck actual Compose/Dockerfiles and app changes. Prepare a 4 GB profile; current production ceilings exceed physical RAM when summed.
- Set production secrets privately and keep one media job at a time.
- Build sequentially, start PostgreSQL/Redis, run migrations and start API/web. Stop on failures; never seed/reset production.
- Configure apex/www DNS, Nginx and HTTPS using the project's existing templates. Use Cloudflare DNS-only initially to preserve large uploads.
- Test actual media downloads, processing, large uploads, cleanup and restart behavior; check RAM/disk.
- Take an encrypted off-server database/configuration backup and test restoration before public launch.

See [deployment procedure](manual-deployment.md) and [monthly hosting plan](monthly-hosting-decision.md) for detailed gates. Do not use the latter's proposed small-VM overlay commands until that overlay has actually been implemented and reviewed against the UPDATED code.
