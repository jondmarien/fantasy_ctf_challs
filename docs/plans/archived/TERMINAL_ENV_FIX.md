# Terminal agent brief — fix env file + restore TLS on 443

**Context:** `docker compose` is throwing warnings that every env var is unset (`CTFD_SECRET_KEY`, `POSTGRES_PASSWORD`, `CF_DNS_API_TOKEN`, etc.). This is almost certainly why `https://api.ctf.chron0.tech:443` is timing out from the public internet — Traefik came up without the Cloudflare DNS API token, so it can't complete ACME DNS-01 challenges, so it has no valid wildcard cert, so TLS handshakes hang or fail.

The env file exists (or should) at `/opt/fantasy_ctf_challs/infra/secrets/.env.prod`. The issue is compose isn't loading it — either because `--env-file` wasn't passed, or because the file is missing/empty.

**Companion docs:**
- `VPS_OPERATIONS.md` §3 — original env file creation
- `OPERATOR_PORTS_FIX.md` — Jon's blocked on this fix before he can resume Step 3 (ctfcli sync)

**Run as `ctf` user on the VPS.**

---

## Where this fits in the sequence

```
You (this doc) ──► env file restored + Traefik cert acquired ──► Jon retests 443 + runs ctfcli sync
       ▲
   you are here
```

Jon is blocked. He can't run `ctf challenge sync` because the API endpoint is unreachable. Fix the env, restore the cert, hand back.

---

## Step 1 — Diagnose

Run:

```bash
FILE=/opt/fantasy_ctf_challs/infra/secrets/.env.prod
ls -la "$FILE" 2>&1
echo "---"
[ -f "$FILE" ] && wc -l "$FILE" && grep -c '^[A-Z_]*=' "$FILE"
echo "---"
[ -f "$FILE" ] && LC_ALL=C grep -c $'\0' "$FILE" 2>/dev/null && echo "null bytes counted above"
```

Three cases:

| Case | Symptom | Path forward |
|---|---|---|
| **A** | `ls` says "No such file" | File was deleted/never created. You cannot fully recover this in-session — see Step 2A. **Stop and tell Jon.** |
| **B** | File exists, has ≥10 lines, ≥10 `KEY=value` matches, 0 null bytes | File is fine — compose just wasn't loading it. Go to Step 3. |
| **C** | File exists but line count or KEY=value count is suspiciously low, or null bytes present | File is corrupted. See Step 2C. |

---

## Step 2A — File is missing (cannot self-recover)

Some values are unrecoverable from the VPS side:
- `CF_DNS_API_TOKEN` (lives in Jon's password manager)
- `GITHUB_OAUTH_CLIENT_ID` / `GITHUB_OAUTH_CLIENT_SECRET` (Jon's password manager)
- `FLAG_*` (Jon owns these)
- `POSTGRES_PASSWORD` (must match what's already on disk in the running Postgres volume — regenerating breaks DB access)

**Stop. Tell Jon:** "`.env.prod` is missing. I cannot fully reconstruct it without your password manager. Specifically, I need: CF_DNS_API_TOKEN, GITHUB_OAUTH_CLIENT_ID, GITHUB_OAUTH_CLIENT_SECRET, all 5 FLAG_* values, plus confirmation that POSTGRES_PASSWORD matches the existing DB."

Jon will paste replacements. Then proceed to Step 3.

> If POSTGRES_PASSWORD is lost, the DB volume needs to be wiped and CTFd reinitialized — Jon will decide that.

---

## Step 2C — File exists but corrupted (null bytes or truncated)

```bash
# Backup first:
cp /opt/fantasy_ctf_challs/infra/secrets/.env.prod \
   /opt/fantasy_ctf_challs/infra/secrets/.env.prod.bak.$(date +%s)

# Strip null bytes if present:
tr -d '\0' < /opt/fantasy_ctf_challs/infra/secrets/.env.prod > /tmp/env.clean
mv /tmp/env.clean /opt/fantasy_ctf_challs/infra/secrets/.env.prod
chmod 600 /opt/fantasy_ctf_challs/infra/secrets/.env.prod

# Confirm clean:
LC_ALL=C grep -c $'\0' /opt/fantasy_ctf_challs/infra/secrets/.env.prod
# Should output: 0
```

Then verify the file's contents look intact:

```bash
grep -c '^[A-Z_]*=' /opt/fantasy_ctf_challs/infra/secrets/.env.prod
# Should be ≥10
```

If lines are still missing after the null-byte strip (truncation), **stop and tell Jon** — same Step 2A handoff.

---

## Step 3 — Make compose find the env file automatically

Symlink rather than `--env-file` every command. Compose's default discovery is `.env` in the working directory of the compose file, so:

```bash
ln -sf /opt/fantasy_ctf_challs/infra/secrets/.env.prod \
       /opt/fantasy_ctf_challs/infra/.env

# Verify:
ls -la /opt/fantasy_ctf_challs/infra/.env
# Should show: ... .env -> .../secrets/.env.prod
```

> Symlink is preferred over copy: rotating a secret means changing one file, not two.

Confirm compose now reads it without warnings:

```bash
cd /opt/fantasy_ctf_challs/infra
docker compose -f docker-compose.prod.yml config 2>&1 | grep -i "warning\|variable" | head -20
# Should output: nothing about unset variables
```

If `docker compose config` still warns about unset variables, the symlink isn't being picked up — check `.env` actually exists in `/opt/fantasy_ctf_challs/infra/` and points to a readable file.

---

## Step 4 — Restart the stack so Traefik picks up the Cloudflare token

```bash
cd /opt/fantasy_ctf_challs/infra

# Bring down so containers re-read env on next up:
docker compose -f docker-compose.prod.yml down

# Bring back up:
docker compose -f docker-compose.prod.yml up -d

# Watch Traefik acquire the wildcard cert (this can take 30-90s):
docker compose -f docker-compose.prod.yml logs -f traefik
```

**You're looking for either:**

- `Certificate obtained for [...] *.ctf.chron0.tech` — success, cert acquired
- `Provider [cloudflare] error` — Cloudflare API token wrong/expired/scoped incorrectly. Stop and tell Jon to verify the token in his password manager.
- `Unable to obtain ACME certificate` — DNS-01 challenge failed. Could be a DNS propagation issue or token problem. Capture the full error message and report to Jon.

Stop watching with Ctrl+C once you see either success or error.

---

## Step 5 — Internal smoke-test (before handing back to Jon)

```bash
# Is anything bound to host port 443?
sudo ss -tulpn | grep -E ':443\b'
# Expect: docker-proxy on 0.0.0.0:443

# Does HTTPS work from the VPS to itself?
curl -k -I https://localhost/ 2>&1 | head -5
# Expect: HTTP/2 404 or similar — NOT "connection refused" or hang

# Does the actual CTFd hostname work from inside the VPS?
curl -I https://api.ctf.chron0.tech/healthcheck 2>&1 | head -5
# Expect: HTTP/2 200 (cert resolves, CTFd responds)
```

**If all three pass:** the fix is complete from the VPS side. Hand back to Jon.

**If `curl -k -I https://localhost/` succeeds but `curl -I https://api.ctf.chron0.tech/...` fails:** the issue is no longer Traefik; it's network-edge (Hetzner firewall blocking 443 inbound, or DNS pointing elsewhere). Tell Jon — that's his Hetzner UI task.

**If `curl -k -I https://localhost/` fails too:** Traefik isn't listening or didn't bind. Get logs:

```bash
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml ps traefik
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml logs --tail=200 traefik
```

Paste both to Jon.

---

## Step 6 — Report back

Tell Jon:

- Which Case you hit in Step 1 (A / B / C)
- Whether Traefik successfully acquired the cert in Step 4
- Results of the three smoke-tests in Step 5
- If anything errored, the relevant log excerpt

Once Traefik's cert is good and `api.ctf.chron0.tech` answers from inside the VPS, Jon can re-test from his laptop and resume `OPERATOR_PORTS_FIX.md` Step 3 (ctfcli sync).

---

## ⚠️ Don't touch

- **The actual values in `.env.prod`** unless Step 2A/2C explicitly required regeneration. Random secrets are fine as-is; Jon-owned secrets (CF token, OAuth client info, flags) must not be invented.
- **`POSTGRES_PASSWORD`** — never regenerate this if the DB volume already exists. It must match what's stored in the Postgres data dir, or CTFd loses access to its data. If you must regenerate (Case A, no recovery), Jon will explicitly approve wiping the DB volume.
- **Hetzner Cloud Firewall** — Jon's UI work, not yours
- **Cloudflare DNS records** — Jon's UI work

## ⚠️ Watch out for

- **Subshell env scoping:** if you `export VAR=...` in one command and then `docker compose ...` in the next without sourcing the file, you're testing your own shell env, not compose's. Always test with `docker compose config` to confirm compose itself sees the values.
- **Compose v1 vs v2:** the `--env-file` flag exists in both but the discovery rules for default `.env` differ slightly. You're on Docker Compose v2 (it's `docker compose ...`, not `docker-compose ...`), which discovers `.env` in the same dir as the compose file. The symlink in Step 3 targets that.
- **Traefik cert cache:** if the previous cert is still in `/acme.json` and hasn't expired, Traefik may serve the old cert even with a broken Cloudflare config. If `curl -I` from the VPS works but external still fails, this is a separate problem (firewall/DNS), not a cert problem.
