# FantasyCTF — VPS Operations Guide

**Audience:** the terminal agent SSHed into the Hetzner CPX21 box at Ashburn.
**Companion docs:** `HOSTING_PLAN_V3.md` (strategy/why) and `EXECUTION_PLAYBOOK.md` (full imperative playbook including local repo edits). This doc extracts only the VPS-side work.
**Hostname:** `ctf-chron0-prod` (or whatever you named it). Public DNS: `api.ctf.chron0.tech`, wildcard `*.ctf.chron0.tech`.
**Repo location on VPS:** `/opt/fantasy_ctf_challs` (clone target).
**Branch:** `feat/hosting` until merged to `main`.

---

## What this doc owns

VPS-side commands, file contents that live on the VPS only, and operational tasks (deploys, plugin installs, backups, restore drills). Anything that's a local repo edit, web-UI click, or browser action is **out of scope** — see `EXECUTION_PLAYBOOK.md` for those.

## What this doc does NOT own

- Hetzner Cloud Firewall rules (web UI — already done by Jon)
- Cloudflare DNS records (web UI — already done by Jon)
- Cloudflare API token generation (web UI — already done by Jon)
- GitHub Environments + Secrets (web UI — Jon)
- CTFd setup wizard walkthrough (browser — Jon)
- GitHub OAuth App creation (web UI — Jon, you'll receive the client ID + secret as input)
- Local repo edits to challenge composes, workflow YAML, site repo (Cursor handles those)

## Conventions

- All shell snippets target Linux (Ubuntu 24.04) on the VPS.
- `<HETZNER_IP>` — public IPv4 of the box (find via `curl -4 ifconfig.me` or in Hetzner console).
- `<CF_DNS_TOKEN>`, `<CTFD_ADMIN_TOKEN>`, `<GITHUB_OAUTH_CLIENT_ID>`, `<GITHUB_OAUTH_CLIENT_SECRET>` — Jon will paste these into the appropriate file when prompted.
- All commands assume you SSH in as the `ctf` user **after** the bootstrap script has run. Before bootstrap runs, you SSH as root.
- Run commands one section at a time; verify at each checkpoint before moving on.

---

# Section 1 — Initial root SSH + system update

**State:** server is freshly provisioned, cloud-init has run, `ufw` should already allow 22/80/443. You can SSH as root with the key you provided at provision time.

```bash
ssh root@<HETZNER_IP>

# Confirm cloud-init completed cleanly:
tail -30 /var/log/cloud-init-output.log
ufw status                          # → Status: active, 22/80/443 ALLOW
systemctl is-active fail2ban        # → active
systemctl is-active ssh             # → active

# Patch:
apt update && apt upgrade -y
apt install -y htop tmux jq git curl ca-certificates apache2-utils
```

### Verification

```bash
[ "$(systemctl is-active fail2ban)" = "active" ] && echo "fail2ban: ok"
[ "$(systemctl is-active ssh)" = "active" ] && echo "ssh: ok"
ufw status verbose | grep -q "22/tcp.*ALLOW" && echo "ufw 22: ok"
ufw status verbose | grep -q "443/tcp.*ALLOW" && echo "ufw 443: ok"
```

If any check fails, **stop** and ask Jon — don't proceed without a hardened baseline.

---

# Section 2 — Run the bootstrap script

**State:** `infra/bootstrap.sh` exists in the repo (Cursor created it). You'll fetch and run it.

The script (full contents in `EXECUTION_PLAYBOOK.md` §2.2) does:

1. Installs Docker via the official script.
2. Creates a `ctf` non-root user, copies your SSH key from root into the new user.
3. Adds a narrow sudoers rule allowing `ctf` to run only `infra/deploy.sh` without a password.
4. Clones the repo to `/opt/fantasy_ctf_challs` and chowns to `ctf`.
5. Creates `infra/secrets/` with mode 700.
6. Configures Docker log rotation in `/etc/docker/daemon.json`.
7. Adds an `iptables` rule to block droplet metadata (`169.254.169.254`) from Docker networks, and persists it.
8. **Disables root SSH login.**

### Run

```bash
# As root:
cd /tmp
curl -fsSL https://raw.githubusercontent.com/jondmarien/fantasy_ctf_challs/feat/hosting/infra/bootstrap.sh > bootstrap.sh
chmod +x bootstrap.sh

# Read it before running — it's about to disable root SSH.
less bootstrap.sh

# Run:
./bootstrap.sh
```

### Verification

After the script finishes, **disconnect** and try again as the new user:

```bash
exit     # back to your laptop

ssh ctf@<HETZNER_IP>                    # should succeed
ssh root@<HETZNER_IP>                   # should fail: "Permission denied"
```

On the VPS as `ctf`:

```bash
docker info >/dev/null && echo "docker: ok"
[ -d /opt/fantasy_ctf_challs/.git ] && echo "repo: ok"
[ "$(stat -c '%a' /opt/fantasy_ctf_challs/infra/secrets)" = "700" ] && echo "secrets dir: ok"
sudo cat /etc/sudoers.d/ctf-deploy | grep -q "deploy.sh" && echo "sudoers: ok"
sudo iptables -L DOCKER-USER -n | grep -q "169.254.169.254" && echo "metadata block: ok"
```

If anything fails, paste the error to Jon — likely a typo in the bootstrap script that needs a Cursor fix.

### Rollback (if something goes wrong)

If you can't SSH back in as either user, use the Hetzner web console (independent of SSH) to:

1. Re-enable root SSH: `sed -i 's/^PermitRootLogin no/PermitRootLogin yes/' /etc/ssh/sshd_config && systemctl restart ssh`
2. Investigate from there.

---

# Section 3 — Create the production secrets file

**State:** running as `ctf` in `/opt/fantasy_ctf_challs`. The file lives only on the VPS — never in git.

### Create the file

```bash
cd /opt/fantasy_ctf_challs/infra/secrets

# Generate the random secrets:
CTFD_SECRET=$(openssl rand -hex 32)
PG_PASSWORD=$(openssl rand -base64 32 | tr -d '/=+' | head -c 32)
TRAEFIK_PW_HASH=$(htpasswd -nbB admin "$(openssl rand -base64 16 | head -c 16)" | cut -d: -f2)

# Write the env file:
cat > .env.prod <<EOF
# CTFd
CTFD_SECRET_KEY=$CTFD_SECRET
CTFD_DATABASE_URL=postgresql+psycopg2://ctfd:$PG_PASSWORD@db/ctfd
CTFD_REDIS_URL=redis://cache:6379

# Postgres
POSTGRES_DB=ctfd
POSTGRES_USER=ctfd
POSTGRES_PASSWORD=$PG_PASSWORD

# Cloudflare DNS-01 for Traefik
# Jon will paste this from his password manager:
CF_DNS_API_TOKEN=<PASTE_CF_DNS_TOKEN_HERE>

# Traefik dashboard basic-auth (status.ctf.chron0.tech)
TRAEFIK_DASHBOARD_USER=admin
TRAEFIK_DASHBOARD_PASS_HASH=$TRAEFIK_PW_HASH

# CTFd OAuth (filled after §6 — leave blank for first boot)
GITHUB_OAUTH_CLIENT_ID=
GITHUB_OAUTH_CLIENT_SECRET=

# Per-challenge flags (filled in Section 8)
# FLAG_LICH=FantasyCTF{...}
# FLAG_ARCANE=FantasyCTF{...}
# FLAG_PROPHECY=FantasyCTF{...}
# FLAG_CHRONOMANCER=FantasyCTF{...}
# FLAG_ARCHITECT=FantasyCTF{...}
# FLAG_PARROT=FantasyCTF{...}
# FLAG_WHISPERING=FantasyCTF{...}
# FLAG_COURT=FantasyCTF{...}
# FLAG_ORACLE=FantasyCTF{...}
# FLAG_MINDFLAYER=FantasyCTF{...}
EOF

chmod 600 .env.prod

# IMPORTANT: also save this to Jon's password manager — Traefik admin creds and Postgres password.
echo "Save to password manager — Traefik admin password (the plaintext, before hashing):"
# Re-print from the htpasswd command above so Jon can copy it.
```

> **Cursor / Jon: replace `<PASTE_CF_DNS_TOKEN_HERE>` with the actual token before continuing.** Without this, Traefik can't request the wildcard cert.

### Verification

```bash
[ "$(stat -c '%a' .env.prod)" = "600" ] && echo "perms: ok"
grep -c '^[A-Z_]*=' .env.prod | grep -E '^[7-9]|^[1-9][0-9]' && echo "fields: ok"   # at least 7
! grep -q 'PASTE_' .env.prod && echo "no placeholders: ok"                          # all replaced
```

---

# Section 4 — Bring up the docker-compose stack

**State:** `infra/docker-compose.prod.yml` and `infra/litellm/config.yml` exist in the repo (Cursor created them). `.env.prod` is populated.

### First boot

```bash
cd /opt/fantasy_ctf_challs
git pull origin feat/hosting

cd infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml pull
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d
```

### Watch Traefik acquire the cert

```bash
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml logs -f traefik
```

You're looking for either:

- `Certificate obtained for [...] *.ctf.chron0.tech` — success.
- DNS-01 challenge errors — the `CF_DNS_API_TOKEN` is wrong or scoped incorrectly.

Cert acquisition typically takes 30–90 seconds. If it's been > 5 min, kill the watch (`Ctrl+C`) and:

```bash
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml logs traefik | grep -iE "error|cloudflare|acme" | tail -20
```

Paste any errors to Jon.

### Verification

```bash
# Cert obtained?
docker compose -f docker-compose.prod.yml logs traefik 2>/dev/null | grep -i "obtained certificate" && echo "cert: ok"

# CTFd healthy from inside the network?
docker compose -f docker-compose.prod.yml exec ctfd curl -sf http://localhost:8000/healthcheck && echo "ctfd internal: ok"

# CTFd reachable from the public internet (Jon's laptop)?
# Jon: run `curl -I https://api.ctf.chron0.tech/healthcheck` — expect 200.

# Database healthy?
docker compose -f docker-compose.prod.yml exec db pg_isready -U ctfd && echo "db: ok"

# All five core services up?
docker compose -f docker-compose.prod.yml ps --format json | jq -r '.[] | select(.State != "running") | .Service'
# Expect: empty output (all running)
```

### Rollback

```bash
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml down
# Volumes are preserved — DB, uploads, certs stick around.
# Only use `down -v` if you're intentionally wiping state (you'll lose CTFd setup, not just config).
```

---

# Section 5 — Hand off to Jon for CTFd setup wizard

**State:** CTFd is reachable at `https://api.ctf.chron0.tech` and showing the setup wizard.

Jon will walk through the wizard in his browser:

- Set CTF name `FantasyCTF`
- User mode: Users (single)
- Create admin: `jon-admin` / `jon@d-sports.org` / strong password
- Theme: `core-beta`
- Generate a token at `Settings → Tokens` named `ci-bot-prod`

**You wait.** When Jon says he has the token, proceed to Section 6.

---

# Section 6 — Wire OAuth (after Jon creates the GitHub OAuth App)

**State:** Jon has created a GitHub OAuth App with callback `https://api.ctf.chron0.tech/redirect`. He'll paste the Client ID and Client Secret here.

```bash
cd /opt/fantasy_ctf_challs/infra/secrets
nano .env.prod
# Update these two lines (replace the empty values):
#   GITHUB_OAUTH_CLIENT_ID=Iv1.xxxxxxxxxxxx
#   GITHUB_OAUTH_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Restart CTFd to pick up the new env

```bash
cd /opt/fantasy_ctf_challs/infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml restart ctfd
```

---

# Section 7 — Install CTFd plugins

**State:** CTFd is running; OAuth env is set. Now install the OAuth and Whale plugins.

### OAuth plugin

```bash
cd /opt/fantasy_ctf_challs/infra/ctfd/plugins
git clone https://github.com/tamuctf/CTFd-oauth.git oauth

cd /opt/fantasy_ctf_challs/infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml restart ctfd

# Wait ~5s for boot:
sleep 5

# Verify the plugin is loaded:
curl -sI https://api.ctf.chron0.tech/oauth | head -1
# Expect: HTTP/2 302 (redirect to GitHub)
```

### Whale plugin

```bash
cd /opt/fantasy_ctf_challs/infra/ctfd/plugins
git clone https://github.com/glzjin/CTFd-Whale.git whale

cd /opt/fantasy_ctf_challs/infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml restart ctfd
```

After restart, **Jon will configure Whale in the CTFd admin UI** at `Plugins → Whale`:

- `WHALE_DOCKER_MAX_CONTAINERS=15`
- `WHALE_DOCKER_API_URL=tcp://socket-proxy:2375` (the socket-proxy comes online in Section 11)
- Default container memory: 256MB
- Default TTL: 30 min
- Globally disabled for now; enabled per-challenge in Section 8

### Verification

```bash
# Plugins load on boot — check CTFd logs for any plugin errors:
docker compose -f docker-compose.prod.yml logs ctfd 2>&1 | grep -iE "plugin|error" | tail -10
```

---

# Section 8 — Per-challenge flags + image tags

**State:** Jon has run `ctf challenge install` for all 22 challenges from his laptop. Cursor has updated the per-challenge `docker-compose.yml` files to use `image: ghcr.io/jondmarien/fantasy-ctf-<slug>:latest` and added Traefik labels.

Your job: populate the per-challenge flags in `.env.prod` and bring up the challenge composes.

### Flags

Edit `infra/secrets/.env.prod` and uncomment/fill the flag block. Jon supplies the values from each challenge's `solution/SOLUTION.md` or `ctfd_meta.json`:

```bash
cd /opt/fantasy_ctf_challs/infra/secrets
nano .env.prod
# Fill in the FLAG_* lines that were commented placeholders.
```

### Bring up Dockerised challenges

Each Dockerised challenge has its own `docker-compose.yml` in its folder. Bring them up:

```bash
cd /opt/fantasy_ctf_challs

# Discover all Dockerised challenges:
for d in $(find {crypto,prog,llm,osint,rev,misc} -name 'docker-compose.yml' -not -path 'infra/*'); do
  dir=$(dirname "$d")
  echo ">>> $dir"
  (cd "$dir" && docker compose --env-file /opt/fantasy_ctf_challs/infra/secrets/.env.prod up -d)
done
```

> **Heads-up:** the consolidated composes at `prog/docker-compose.yml` and `llm/docker-compose.yml` cover multiple challenges each. Don't double-up by also bringing up the per-challenge composes inside their subfolders.

### Verification

```bash
# All challenge containers running?
docker ps --format '{{.Names}} {{.Status}}' | grep -v 'Up '
# Expect: empty output

# Traefik routing each subdomain?
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs traefik 2>&1 \
  | grep -i "router" | grep -iE "lich|arcane|prophecy|oracle|parrot" | tail -20
```

Jon can run each challenge's `solution/solve.py` from his laptop pointed at `<chal>.ctf.chron0.tech` to confirm flags come back.

---

# Section 9 — Hardening: docker-socket-proxy

**State:** challenges are running. Whale needs the Docker socket; we expose it via a narrow proxy rather than bind-mounting it directly.

The socket-proxy service is already in `docker-compose.prod.yml` (Cursor added it). Just bring it up:

```bash
cd /opt/fantasy_ctf_challs/infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d socket-proxy

# Verify CTFd-Whale can reach it (after Jon configures Whale to use tcp://socket-proxy:2375):
docker compose -f docker-compose.prod.yml exec ctfd curl -sf http://socket-proxy:2375/version | jq .ApiVersion
```

---

# Section 10 — Restic backups

**State:** primary work is done; now harden the backup story.

### Create restic.env

```bash
cd /opt/fantasy_ctf_challs/infra/secrets

# Jon will provide:
#   - Backblaze B2 application key (B2_ACCOUNT_ID, B2_ACCOUNT_KEY)
#   - or Hetzner Storage Box credentials (sftp:user@host:/path)
#   - RESTIC_PASSWORD (generate fresh: openssl rand -base64 32)

cat > restic.env <<EOF
RESTIC_REPOSITORY=b2:fantasy-ctf-backups:/prod
RESTIC_PASSWORD=<PASTE_OR_GENERATE>
B2_ACCOUNT_ID=<PASTE>
B2_ACCOUNT_KEY=<PASTE>
EOF
chmod 600 restic.env
```

### Install restic

```bash
sudo apt install -y restic

# Initialize the repo (one-time):
source /opt/fantasy_ctf_challs/infra/secrets/restic.env
restic init
# Save the displayed master key to Jon's password manager — losing it = losing all backups.
```

### Install the cron entry

The script `infra/backups/restic.sh` is in the repo. Just install the cron line:

```bash
echo '0 4 * * 0 root /opt/fantasy_ctf_challs/infra/backups/restic.sh >> /var/log/restic.log 2>&1' \
  | sudo tee -a /etc/crontab

# Verify cron sees it:
sudo crontab -l 2>/dev/null
sudo grep restic /etc/crontab
```

### Test the script manually before the first scheduled run

```bash
sudo /opt/fantasy_ctf_challs/infra/backups/restic.sh
# Watch for errors. On success: pg_dump completes, uploads tarball is created, restic backup pushes,
# and old local files in /var/backups/ctf-prod older than 2 days are pruned.

sudo restic snapshots
# Should list at least one snapshot.
```

---

# Section 11 — Restore drill (one-time, before Phase 7)

**Goal:** prove the backup restores cleanly. Don't skip this.

```bash
# Provision a throwaway CX11 in the same Hetzner project (Jon does this in the web UI).
# SSH in as root:
ssh root@<TEST_IP>

# Bootstrap minimally — just Docker:
curl -fsSL https://get.docker.com | sh
apt install -y restic git

# Clone the repo:
git clone https://github.com/jondmarien/fantasy_ctf_challs.git /opt/fantasy_ctf_challs
cd /opt/fantasy_ctf_challs

# Copy the secrets directory from the prod box (or paste manually):
mkdir -p infra/secrets
# scp ctf@<HETZNER_IP>:/opt/fantasy_ctf_challs/infra/secrets/{restic.env,.env.prod} infra/secrets/

# Restore the latest snapshot:
source infra/secrets/restic.env
restic restore latest --target /tmp/restore

# Bring up just the database:
cd infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d db

# Wait for Postgres to be ready:
until docker compose -f docker-compose.prod.yml exec db pg_isready -U ctfd; do sleep 1; done

# Restore the dump:
gunzip -c /tmp/restore/var/backups/ctf-prod/ctfd-*.sql.gz \
  | docker compose -f docker-compose.prod.yml exec -T db psql -U ctfd ctfd

# Restore uploads volume:
docker run --rm \
  -v fantasy_ctf_challs_ctfd_uploads:/data \
  -v /tmp/restore/var/backups/ctf-prod:/backup:ro \
  alpine tar -xzf /backup/uploads-*.tar.gz -C /data

# Bring up everything:
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d

# Smoke-test: CTFd loads, scoreboard shows expected state:
curl -k -I https://api.ctf.chron0.tech    # cert won't match this IP — that's expected, just check 200
docker compose -f docker-compose.prod.yml exec ctfd curl -sf http://localhost:8000/api/v1/challenges | jq '.data | length'
# Expect: 22 (or whatever was live at backup time)

# Tear down the test droplet (Jon does in the web UI).
```

If anything fails: fix the script or the procedure, re-run the drill. **Don't move to Phase 7 launch until a clean restore round-trips.**

---

# Section 12 — Operational tasks (recurring)

## 12.1 Deploy challenge changes (after Cursor merges to `main`)

This is what GitHub Actions automates, but you can do it manually:

```bash
cd /opt/fantasy_ctf_challs
git pull origin main
cd infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml pull
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d --remove-orphans

# Then for each challenge directory whose Dockerfile changed:
# (cd <chal_dir> && docker compose pull && docker compose up -d)
```

## 12.2 Tail logs

```bash
# CTFd:
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs -f --tail 100 ctfd

# Traefik (cert renewals, routing errors):
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs -f --tail 100 traefik

# A specific challenge:
docker logs -f --tail 100 <container_name>

# All containers, errors only:
docker ps -aq | xargs -I{} sh -c 'docker logs --tail 50 {} 2>&1 | grep -i "error\|exception" | head -5'
```

## 12.3 Rotate the CTFd admin token

```bash
# Jon: in CTFd UI, Settings → Tokens → revoke old, generate new.
# Then update the value in:
#   - GitHub Environment `production` → secret `CTFD_TOKEN`
#   - Local `.ctf/config` (Jon's laptop)
# No VPS-side change needed — the token isn't stored on the box.
```

## 12.4 Update Hetzner snapshot before risky changes

Tell Jon to take a snapshot via the Hetzner UI before:

- CTFd version bumps
- Plugin updates
- Cloud-init or kernel changes
- Any "I think this will work" change

If anything explodes, restore from snapshot in the Hetzner console (~2 min).

## 12.5 Watch disk usage

```bash
df -h /                                 # root partition
docker system df                        # Docker layers + volumes
du -sh /var/lib/docker/volumes/         # individual volume sizes

# Prune unused Docker layers (run weekly via cron, or manually if /opt fills up):
docker system prune -a -f --volumes
# WARNING: --volumes also removes unused volumes. Confirm no live container needs them first.
```

## 12.6 OAuth provider failover (if GitHub revokes the app)

```bash
# Plug Google OAuth instead. Jon creates the OAuth client in Google Cloud Console.
# Then update .env.prod:
nano /opt/fantasy_ctf_challs/infra/secrets/.env.prod
# Replace GITHUB_OAUTH_CLIENT_ID / SECRET with GOOGLE equivalents. Plugin already supports both.

cd /opt/fantasy_ctf_challs/infra
docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml restart ctfd
```

---

# Section 13 - Aachen scoring rollout (terminal-agent flow)

Use this when the repository includes the Aachen scoring plugin and dynamic
challenge metadata updates.

## 13.1 Pull + restart CTFd

```bash
ssh ctf@<HETZNER_IP>
cd /opt/fantasy_ctf_challs
bash infra/scripts/aachen_rollout_vps.sh feat/hosting
```

Expected:

- Script checks out and pulls `feat/hosting`.
- CTFd restarts.
- Healthcheck probe inside container succeeds.

## 13.2 Verify plugin registration and runtime registry

```bash
cd /opt/fantasy_ctf_challs
bash infra/scripts/aachen_verify_vps.sh
```

Expected:

- Finds `infra/ctfd/plugins/dynamic_challenges_aachen`.
- CTFd logs include the Aachen registration line.
- In-container Python prints `aachen` in `DECAY_FUNCTIONS`.

## 13.3 Hand off to Jon for metadata sync

After VPS verification is green, Jon should run ctfcli sync from the laptop for
the 22 dynamic challenges that now contain `extra.function: aachen`.

If verification fails:

- Re-run `docker compose -f infra/docker-compose.prod.yml logs ctfd --tail=500`.
- Confirm plugin files exist at `/opt/fantasy_ctf_challs/infra/ctfd/plugins/dynamic_challenges_aachen`.
- Re-run `aachen_rollout_vps.sh`, then `aachen_verify_vps.sh`.

---

# What to do if you get stuck

1. **Don't improvise on security.** If a step says "verify perms 600" and you got 644, fix the perms — don't continue.
2. **Don't `docker compose down -v`** unless you're intentionally wiping state. The `-v` removes volumes (DB, uploads, certs).
3. **Don't disable `ufw` or open ports** the firewall doesn't have.
4. **Don't expose `/var/run/docker.sock`** to a container that doesn't need it. Use `socket-proxy`.
5. **If you're unsure**, paste the failing command + output to Jon and wait. It's a personal portfolio site — there's no SLA, no rush.

---

# Quick command reference

| Want to | Run |
|---|---|
| SSH in | `ssh ctf@<HETZNER_IP>` |
| Pull & redeploy | `cd /opt/fantasy_ctf_challs && git pull && cd infra && docker compose --env-file secrets/.env.prod -f docker-compose.prod.yml up -d --remove-orphans` |
| Tail CTFd logs | `docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs -f --tail 100 ctfd` |
| Restart one service | `docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml restart <svc>` |
| Backup now | `sudo /opt/fantasy_ctf_challs/infra/backups/restic.sh` |
| List snapshots | `source /opt/fantasy_ctf_challs/infra/secrets/restic.env && restic snapshots` |
| Disk + Docker space | `df -h / && docker system df` |
| Check certs | `docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs traefik 2>&1 \| grep -i certificate \| tail -10` |
