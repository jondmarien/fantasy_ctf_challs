# Operator brief (Jon) — firewall, ctfcli sync, external smoke-test

**Context:** Cursor has fixed port collisions and filled in `connection_info`. The terminal agent has redeployed the affected challenge containers on the VPS. Your part: open Hetzner firewall ports so the public can reach them, sync the connection_info strings to CTFd, and confirm everything works from outside the VPS.

**Companion docs:**
- `CURSOR_PORTS_FIX.md` — Cursor's repo edits (already merged before you reach this step)
- `TERMINAL_PORTS_FIX.md` — terminal agent's VPS redeploy (already done before you reach this step)

---

## Where this fits in the sequence

```
Cursor merged ──► Terminal agent redeployed ──► you (this doc) ──► Phase G
                                                       ▲
                                                   you are here
```

You're the last step of this round. After your verifications pass, you're cleared for Phase G (merge interlude → soft launch).

---

## Precondition checklist

Before starting, confirm:

- [ ] Cursor's PR `fix/ports-and-connection-info` has merged to `feat/hosting`
- [ ] Terminal agent reported back: all targeted containers up with distinct ports, internal smoke-tests pass
- [ ] You're on a machine with `ctf` (ctfcli) and a working `.ctf/config` pointing at `https://api.ctf.chron0.tech`

If any of the above is false, don't start this — the steps below will fail or produce a misleading-but-wrong state in CTFd.

---

## Step 1 — Open Hetzner firewall ports

Hetzner Cloud Console → **Firewalls** → your firewall (`fw-ctf-prod` or whatever you named it) → **Inbound rules** → **Add rule** twice:

| Direction | Protocol | Ports | Source |
|---|---|---|---|
| In | TCP | `1337-1340` | `0.0.0.0/0, ::/0` |
| In | TCP | `7001-7005` | `0.0.0.0/0, ::/0` |

Save. Active immediately, no VPS restart needed.

> Don't open ports you're not actually using (e.g. 1341-7000). Tight inbound surface is one of your hardening wins; don't undo it casually. If you later add a challenge on a new port, open just that one then.

### Verify

From your laptop:

```bash
nc -zv lich.ctf.chron0.tech 1337
# Connection succeeded if firewall is open + container is up.
```

---

## Step 2 — External smoke-test each challenge

From your laptop, NOT inside the VPS:

```bash
# TCP challenges (-zv just checks port openness):
nc -zv lich.ctf.chron0.tech 1337
nc -zv arcane.ctf.chron0.tech 1338
nc -zv prophecy.ctf.chron0.tech 1339

# HTTP challenges (curl -I, expect any 2xx/4xx/5xx, NOT connection refused):
curl -sI http://parrot.ctf.chron0.tech:7001/
curl -sI http://whispering.ctf.chron0.tech:7002/
curl -sI http://court.ctf.chron0.tech:7003/
curl -sI http://oracle.ctf.chron0.tech:7004/
curl -sI http://mindflayer.ctf.chron0.tech:7005/
curl -sI http://ogre.ctf.chron0.tech:1340/

# End-to-end on one LLM challenge with your own key:
curl -X POST http://parrot.ctf.chron0.tech:7001/chat \
  -H "X-Player-API-Key: <YOUR_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"message":"hi","history":[]}'
# Expect: HTTP 200 with JSON {"reply": "..."}
```

**If any TCP check fails:** firewall rule for that port range didn't save, or DNS is wrong. Re-check Step 1 and `dig +short lich.ctf.chron0.tech` (should return your Hetzner IP via the `*.ctf` wildcard).

**If HTTP curls fail with "connection refused":** same as TCP — firewall or DNS.

**If HTTP curls succeed but `/chat` returns 500:** that's a known LLM challenge app-level bug (separate from this fix). Note it, move on. Players will use `/chat`, not `/`.

---

## Step 3 — Sync metadata to CTFd

`ctf challenge sync` pushes the updated `connection_info` (and any other `challenge.yml` changes) to your live CTFd instance. Run from the repo root on your laptop:

```bash
cd J:\projects\personal-projects\fantasy_ctf_challs
.venv\Scripts\activate

# Or on a Unix-style shell: source .venv/bin/activate

for c in \
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
  echo ">>> $c"
  ctf challenge sync "$c"
done
```

PowerShell equivalent if the bash for-loop doesn't work in your shell:

```powershell
$challs = @(
  "crypto/The-Lichs-Cursed-Oracle-Hard",
  "prog/The-Arcane-Protocol-Hard",
  "prog/The-Prophecy-Engine-Expert",
  "misc/The-Ogres-Audition-Hard",
  "llm/The-Enchanted-Parrot-Beginner",
  "llm/The-Whispering-Merchant-Easy",
  "llm/The-Court-Wizards-Familiar-Medium",
  "llm/The-Oracle-of-Shadows-Hard",
  "llm/The-Mindflayers-Sanctum-Expert"
)
foreach ($c in $challs) {
  Write-Host ">>> $c"
  ctf challenge sync $c
}
```

Watch for any sync errors. Common ones:
- "Challenge not found" — that challenge's `name` in `challenge.yml` doesn't match what's in CTFd. Either re-`install` it or fix the name.
- 401/403 — `.ctf/config` token expired or wrong. Regenerate.
- Connection error — VPS down or DNS broken.

---

## Step 4 — Verify in CTFd admin UI

Open `https://api.ctf.chron0.tech/admin/challenges` in your browser, log in.

For each of the 9 challenges synced above:
1. Click the challenge.
2. Confirm the **Connection Info** field shows the right string (e.g. `nc lich.ctf.chron0.tech 1337` for Lich).
3. Confirm **State** is still `hidden` (you don't flip to `visible` until Phase 7).

If any challenge shows an empty or wrong Connection Info: re-run `ctf challenge sync <path>` for that one, or edit it manually in the admin UI as a fallback.

---

## Step 5 — Mark this round done

If all four steps pass:

- [ ] Firewall ports `1337-1340` and `7001-7005` open
- [ ] External smoke-tests reach each challenge
- [ ] At least one LLM `/chat` round-trip returns 200 with a real reply
- [ ] `ctf challenge sync` succeeded for all 9 listed challenges
- [ ] CTFd admin UI shows correct connection info on each

You're cleared for **Phase G — Merge interlude**.

---

## What this doc does NOT cover

- The site repo `ChallengeDetailPage.tsx` truncation (still outstanding, separate fix)
- The null-byte corruption source on your laptop (separate investigation)
- Phase G itself (merge `feat/hosting` → `main`, bump `SOLUTIONS_BASE_URL` in site repo, tag both repos v1.0.0)
- Phase 7 soft launch (friend beta, triage, flip visible, public announce)

Refer to `CURSOR_BRIEF.md` Phase G and `HOSTING_PLAN_V3.md` §7 for those.
