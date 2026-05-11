# Terminal agent brief — redeploy + smoke-test

**Context:** Cursor has just merged a PR that resolves port collisions (4 challenges were all binding host port 1337) and fills in `connection_info` strings. You need to pull the changes, stop the conflicting containers, redeploy with new port mappings, and confirm each challenge is reachable from inside the VPS.

**Companion docs:**
- `CURSOR_PORTS_FIX.md` — what Cursor already did (the PR you're consuming)
- `OPERATOR_PORTS_FIX.md` — what Jon does after you finish (firewall + ctfcli sync + external smoke-test)
- `VPS_OPERATIONS.md` — broader operational reference

**Run as `ctf` user on the VPS.**
**Precondition:** Cursor's PR merged to `feat/hosting`. Confirm with `git log --oneline -3` showing a commit like `infra: resolve port collisions ...`.

---

## Where this fits in the sequence

```
Cursor merged ──► Terminal agent (this doc) ──► Jon syncs + opens firewall + external smoke-test
                          ▲
                      you are here
```

Your part is the VPS-side redeploy. Jon does the metadata sync and firewall work after — those don't block your work, but external smoke-tests do.

---

## Step 1 — Pull latest

```bash
cd /opt/fantasy_ctf_challs
git fetch origin
git checkout feat/hosting
git pull origin feat/hosting
git log --oneline -3
```

Expect the most recent commit to mention "resolve port collisions" or similar. If not, stop and tell Jon — Cursor's PR may not have merged.

---

## Step 2 — Stop the four 1337-conflict challenges first

These were all binding the same host port; stopping them clears the binding before you bring up the new (distinct) ports.

```bash
ENV_FILE=/opt/fantasy_ctf_challs/infra/secrets/.env.prod

for d in \
  crypto/The-Lichs-Cursed-Oracle-Hard \
  prog/The-Arcane-Protocol-Hard \
  prog/The-Prophecy-Engine-Expert \
  misc/The-Ogres-Audition-Hard \
; do
  echo ">>> stopping $d"
  (cd "/opt/fantasy_ctf_challs/$d" && docker compose --env-file "$ENV_FILE" down)
done
```

Confirm nothing's bound to 1337 anymore:

```bash
ss -tlnp | grep ':1337' || echo "1337 free"
```

---

## Step 3 — Bring all Dockerised challenges back up with the new composes

```bash
ENV_FILE=/opt/fantasy_ctf_challs/infra/secrets/.env.prod

for d in \
  crypto/The-Lichs-Cursed-Oracle-Hard \
  prog/The-Arcane-Protocol-Hard \
  prog/The-Prophecy-Engine-Expert \
  misc/The-Ogres-Audition-Hard \
  llm/The-Enchanted-Parrot-Beginner \
  llm/The-Whispering-Merchant-Easy \
  llm/The-Court-Wizards-Familiar-Medium \
  llm/The-Oracle-of-Shadows-Hard \
  llm/The-Mindflayers-Sanctum-Expert \
; do
  echo ">>> $d"
  (cd "/opt/fantasy_ctf_challs/$d" && docker compose --env-file "$ENV_FILE" up -d)
done
```

> If Chronomancer + Architect (consolidated under `prog/docker-compose.yml`) are still in play, Jon will tell you in his hand-off. Add their compose to the loop above only if explicitly listed.

---

## Step 4 — Confirm all containers are up with the right ports

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | grep -E '7001|7002|7003|7004|7005|1337|1338|1339|1340'
```

**Expected:** each challenge listed with its assigned port like `0.0.0.0:1338->1337/tcp`. None missing, none `Exited` or `Restarting`.

**Two things to verify carefully:**

1. **No two rows share the same host port.** If `docker ps` shows two containers both bound to 1337, the second `up -d` either failed silently or you missed a `down` step. Re-run Step 2 for the offenders, then Step 3.
2. **Every targeted challenge appears.** If a row is missing, that container failed to start. Get logs:
   ```bash
   docker ps -a --filter 'status=exited' --filter 'status=restarting'
   docker logs <container_name> --tail 50
   ```

---

## Step 5 — Internal smoke-test (from the VPS, before firewall opens)

The Hetzner firewall doesn't yet allow inbound on these ports — Jon does that. But you can hit them from inside the VPS to confirm the containers themselves work.

```bash
# TCP challenges:
nc -zv localhost 1337 && echo "Lich ok"
nc -zv localhost 1338 && echo "Arcane ok"
nc -zv localhost 1339 && echo "Prophecy ok"
nc -zv localhost 1340 && echo "Ogre ok (HTTP but TCP-connectable)"

# HTTP challenges (LLM + Ogre):
for p in 7001 7002 7003 7004 7005 1340; do
  code=$(curl -s -o /dev/null -w "%{http_code}\n" http://localhost:$p/)
  echo "port $p → HTTP $code"
done
```

**Expected:** every port responds. For HTTP, any of 200/404/500 means the container is up and routing (a 500 at `/` is a known cosmetic issue — Jon flagged it earlier; the real LLM endpoint is `POST /chat`). A code of `000` means nothing's listening — that container didn't start.

---

## Step 6 — Report to Jon

Paste back:

1. The output of `docker ps --format ...` (Step 4), showing all targeted containers running with distinct ports
2. The internal smoke-test results from Step 5
3. Any `docker compose up` errors or container restart loops

Once Jon confirms, he'll open the Hetzner firewall ports and run external smoke-tests + `ctf challenge sync` from his laptop. Your part is done at that point.

---

## ⚠️ Don't touch

- `infra/secrets/.env.prod` — already correct, no changes needed
- The metadata-block `iptables` rule — Jon's handled it separately
- Hetzner Cloud Firewall — that's Jon's UI work
- Any non-Dockerised challenge (crypto/prog/osint/rev with static files) — no containers, no compose
- The site repo — Cursor's territory

## ⚠️ If anything goes wrong

Don't improvise. Specifically:

- Don't run `docker compose down -v` (deletes volumes including DB)
- Don't edit `infra/docker-compose.prod.yml` directly — that's the main stack, not per-challenge
- If a container won't start and the logs are confusing, capture the logs and tell Jon. Don't try to "fix" the compose file from the VPS — that goes through Cursor + a fresh PR

## ⚠️ Null-byte corruption awareness

The repo has had recurring null-byte corruption on Jon's laptop. After `git pull`, the deployed files might have null bytes that Docker Compose has been tolerant of so far. If `docker compose up` or `compose config` throws a parse error you can't explain, paste it to Jon — it may be a corruption case rather than a real config bug.
