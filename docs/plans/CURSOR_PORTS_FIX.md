# Cursor brief — port collisions + connection_info

**Context:** four Dockerised challenges have host-port collisions (all bind 1337). Plus every Dockerised challenge's `challenge.yml` has an empty or placeholder `connection_info`, so players see no connection string in CTFd. Fix both in one PR.

**Companion docs:**
- `TERMINAL_PORTS_FIX.md` — what the terminal agent does after this PR merges
- `OPERATOR_PORTS_FIX.md` — what Jon does (firewall + ctfcli sync)
- Source of truth for the wider plan: `HOSTING_PLAN_V3.md`

**Working dir:** `J:\projects\personal-projects\fantasy_ctf_challs`.
**Branch:** create `fix/ports-and-connection-info` off `feat/hosting`.

---

## Where this fits in the sequence

```
Cursor (this doc) ──► merge ──► Terminal agent pulls + redeploys ──► Jon syncs metadata + firewall
       ▲
   you are here
```

You go first. Terminal agent and Jon are blocked until your PR merges.

---

## Step 1 — Resolve port collisions

Edit each compose's `ports:` line to a unique host port. Container port stays the same.

| File | Current `ports:` | New `ports:` |
|---|---|---|
| `crypto/The-Lichs-Cursed-Oracle-Hard/docker-compose.yml` | `"1337:1337"` | `"1337:1337"` (keep — this is the canonical) |
| `prog/The-Arcane-Protocol-Hard/docker-compose.yml` | `"1337:1337"` | `"1338:1337"` |
| `prog/The-Prophecy-Engine-Expert/docker-compose.yml` | `"1337:1337"` | `"1339:1337"` |
| `misc/The-Ogres-Audition-Hard/docker-compose.yml` | `"1337:1337"` | `"1340:1337"` |

LLM challenges already have distinct host ports (7001–7005). Don't touch them.

For Chronomancer / Architect (consolidated under `prog/docker-compose.yml`): see Step 2 — likely retired.

---

## Step 2 — Retire the consolidated composes (recommended)

The agent's hardening pass operated on per-challenge composes. The root-level `prog/docker-compose.yml`, `llm/docker-compose.yml`, and `llm/docker-compose.dev.yml` are legacy duplicates that collide on host ports (1338, 7000) and lack the hardening.

Move them out of the way:

```bash
mkdir -p _archive/legacy-composes/prog _archive/legacy-composes/llm
git mv prog/docker-compose.yml _archive/legacy-composes/prog/docker-compose.yml
git mv llm/docker-compose.yml _archive/legacy-composes/llm/docker-compose.yml
git mv llm/docker-compose.dev.yml _archive/legacy-composes/llm/docker-compose.dev.yml
```

> **If `prog/docker-compose.yml` is load-bearing for Chronomancer + Architect** (they were originally consolidated into one container per the README), don't archive. Instead:
> - Reassign its host ports to non-colliding values (e.g. 1341, 1342)
> - Add the same hardening as the per-challenge composes (`read_only`, `cap_drop: [ALL]`, `no-new-privileges`, `mem_limit: 256m`, `cpus: '0.5'`, `pids_limit: 128`, `tmpfs: /tmp`)
> - Confirm with Jon before deleting either way

---

## Step 3 — Fill in `connection_info` in each Dockerised `challenge.yml`

Set the top-level `connection_info:` field. It's a sibling of `name:`, `category:`, etc. — plain string value.

| File | `connection_info:` value |
|---|---|
| `crypto/The-Lichs-Cursed-Oracle-Hard/challenge.yml` | `nc lich.ctf.chron0.tech 1337` |
| `prog/The-Arcane-Protocol-Hard/challenge.yml` | `nc arcane.ctf.chron0.tech 1338` |
| `prog/The-Prophecy-Engine-Expert/challenge.yml` | `nc prophecy.ctf.chron0.tech 1339` |
| `misc/The-Ogres-Audition-Hard/challenge.yml` | `http://ogre.ctf.chron0.tech:1340` |
| `llm/The-Enchanted-Parrot-Beginner/challenge.yml` | `http://parrot.ctf.chron0.tech:7001` |
| `llm/The-Whispering-Merchant-Easy/challenge.yml` | `http://whispering.ctf.chron0.tech:7002` |
| `llm/The-Court-Wizards-Familiar-Medium/challenge.yml` | `http://court.ctf.chron0.tech:7003` |
| `llm/The-Oracle-of-Shadows-Hard/challenge.yml` | `http://oracle.ctf.chron0.tech:7004` |
| `llm/The-Mindflayers-Sanctum-Expert/challenge.yml` | `http://mindflayer.ctf.chron0.tech:7005` |

For Chronomancer / Architect: if kept (see Step 2), pick subdomain + port and add their entries. If retired, skip.

YAML shape:

```yaml
name: The Enchanted Parrot
category: llm
connection_info: http://parrot.ctf.chron0.tech:7001
# ... rest unchanged
```

---

## Step 4 — Verify

```bash
# YAML still parses:
yamllint $(find {crypto,prog,llm,osint,rev,misc} -name 'challenge.yml')

# All compose files still parse:
for d in $(find {crypto,prog,llm,osint,rev,misc} -name 'docker-compose.yml' -not -path '*_archive*'); do
  docker compose -f "$d" config --quiet || echo "FAIL: $d"
done

# No port collisions remain:
grep -rE '^\s+-\s+"[0-9]+:' {crypto,prog,llm,misc}/*/docker-compose.yml | awk -F'"' '{print $2}' | sort | uniq -d
# Should output nothing — any output means a host-port is reused
```

If the verify block returns errors, fix and re-run before pushing.

---

## Step 5 — Commit and push

```bash
git add -A
git commit -m "infra: resolve port collisions (4×1337 → 1337/1338/1339/1340), fill connection_info"
git push origin fix/ports-and-connection-info
```

Open PR to `feat/hosting`, self-review, merge.

After merge, tell Jon: **"Cursor PR merged. Terminal agent can run `TERMINAL_PORTS_FIX.md` now."**

---

## ⚠️ Watch for null bytes

The repo has had recurring null-byte corruption. After editing, before commit:

```bash
for f in $(git diff HEAD --name-only); do
  count=$(LC_ALL=C grep -c $'\0' "$f" 2>/dev/null || echo 0)
  [ "$count" != "0" ] && echo "$f has $count null bytes — clean before commit"
done
```

If any file has nulls:

```bash
tr -d '\0' < $f > $f.clean && mv $f.clean $f
```

Re-run the verify block (Step 4), then commit.

---

## What this doc does NOT cover

- Hetzner Cloud Firewall changes (Jon's manual UI task)
- Deploying the new composes on the VPS (terminal agent)
- `ctf challenge sync` to push metadata to CTFd (Jon, from his laptop)
- Smoke-testing from outside the VPS (Jon)
- The site repo `ChallengeDetailPage.tsx` truncation (separate brief, still outstanding)
