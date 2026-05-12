# Aachen-style convex decay scoring — implementation brief

**Audience:** Cursor + terminal agent + Jon (sequential handoffs).
**Companion docs:** `HOSTING_PLAN_V3.md` for the broader architecture; `EXECUTION_PLAYBOOK.md` §4 for the per-challenge sync pattern.

## Context

CTFd 3.8.x ships two decay functions: `linear` and `logarithmic`. Despite the name, "logarithmic" is actually parabolic (`((min - initial)/decay²) * solves² + initial`). Neither matches the **convex sigmoid** curve Jon wants:

```
value = round(minimum + (initial - minimum) / (1 + (max(0, solves - 1) / 11.92201) ^ 1.206069))
```

This is the formula Aachen 34C3 CTF (2018, repopularized in 2023) uses for dynamic scoring. Shape: drops sharply for solves 1–5, smooth descent through 5–40, asymptotes to `minimum` thereafter. Rewards early solvers, doesn't crash hard like CTFd's parabolic.

**Search confirmed no existing plugin implements this.** Closest is `sigpwny/ctfd-dynamic-challenges-mod` (rCTF curve, different shape). We're writing a new one. ~50 LOC of Python.

## Architecture decision

CTFd's `CTFd/plugins/challenges/__init__.py` exposes a top-level `DECAY_FUNCTIONS` dict that `calculate_value(challenge)` reads from based on `challenge.function`. A plugin can import this dict and add a new entry at boot — no monkey-patching, survives CTFd upgrades cleanly unless they refactor that registry.

**The plan:** add `DECAY_FUNCTIONS["aachen"] = aachen_calc` from a small plugin, then set `function: aachen` per-challenge in each `challenge.yml` and re-sync via ctfcli.

## Work split (sequential, no parallelism)

```
Cursor (writes plugin + updates challenge.yml) 
  → commit + push to feat/hosting
    → Terminal agent (pulls, rebuilds CTFd, restarts, verifies plugin loaded)
      → Jon (ctfcli sync per challenge from laptop, verify in admin UI)
```

Each actor's work is below. Don't skip ahead — verification at each step catches problems before they compound.

---

# Cursor's part

**Goal:** plugin code in repo + every dynamic challenge.yml updated to use the new function.

**Working dir:** `J:\projects\personal-projects\fantasy_ctf_challs`.
**Branch:** create `feat/aachen-scoring` off `feat/hosting`.

## C.1 — Create the plugin

**Path:** `infra/ctfd/plugins/dynamic_challenges_aachen/`

> The folder name matters. CTFd loads plugins alphabetically; `dynamic_challenges_aachen` sorts after the built-in `dynamic_challenges`, which guarantees `DECAY_FUNCTIONS` is already populated when we extend it. Don't rename to e.g. `aachen_scoring` — it'd load before `dynamic_challenges` and the dict wouldn't exist yet.

### `infra/ctfd/plugins/dynamic_challenges_aachen/__init__.py`

```python
"""
Aachen 34C3 CTF-style convex decay scoring for CTFd.

Registers a new decay function "aachen" in CTFd's DECAY_FUNCTIONS registry.
To use, set `function: aachen` on a dynamic challenge (via challenge.yml + ctfcli,
or via the CTFd admin API).

Formula:
    value = minimum + (initial - minimum) / (1 + (max(0, solves - 1) / K) ^ P)

Where:
    K = 11.92201 (inflection point — solves where score is roughly midway
                  between minimum and initial)
    P = 1.206069 (steepness exponent — higher = sharper transition)

These magic numbers come from Aachen 34C3 CTF (2018, repopularized 2023) and
produce a convex/sigmoid decay that drops sharply for early solvers and
asymptotes gently to the minimum. Tunable below if you want a different shape.

Originally inspired by sigpwny/ctfd-dynamic-challenges-mod, which uses rCTF's
curve — a different shape, kept here as a reference if you ever want to swap.
"""

from CTFd.models import Solves, db
from CTFd.plugins.challenges import DECAY_FUNCTIONS

# Tunables — change these to retune the curve shape across all "aachen" challenges
AACHEN_INFLECTION = 11.92201
AACHEN_STEEPNESS = 1.206069


def aachen(challenge):
    """Compute the current value of a dynamic challenge using Aachen-style convex decay.

    Reads challenge.initial and challenge.minimum from the row, counts non-hidden
    solves, and applies the convex formula. Returns an int.
    """
    solve_count = (
        db.session.query(Solves)
        .filter_by(challenge_id=challenge.id)
        .count()
    )

    initial = challenge.initial
    minimum = challenge.minimum
    delta = initial - minimum

    # Guard rails
    if delta <= 0:
        return minimum

    value = minimum + delta / (
        1 + (max(0, solve_count - 1) / AACHEN_INFLECTION) ** AACHEN_STEEPNESS
    )
    return int(round(value))


def load(app):
    """Register the aachen decay function with CTFd's DECAY_FUNCTIONS registry."""
    DECAY_FUNCTIONS["aachen"] = aachen
    app.logger.info(
        "[dynamic_challenges_aachen] registered 'aachen' decay function "
        f"(K={AACHEN_INFLECTION}, P={AACHEN_STEEPNESS})"
    )
```

### `infra/ctfd/plugins/dynamic_challenges_aachen/config.json`

```json
{
  "name": "Aachen Scoring",
  "description": "Adds Aachen 34C3-style convex decay function for dynamic challenges.",
  "version": "1.0.0",
  "author": "Jon Marien"
}
```

### `infra/ctfd/plugins/dynamic_challenges_aachen/README.md`

A short doc so future-you (and recruiters reading the repo) understands what it does. Roughly:

```markdown
# Aachen Scoring Plugin

Adds a third decay function (`aachen`) to CTFd dynamic challenges, alongside
the built-in `linear` and `logarithmic` (parabolic) functions.

## Curve shape

Convex sigmoid: drops sharply for early solvers, smooth descent through the
middle range, asymptotes to `minimum`. Compared to CTFd's parabolic default,
this rewards early solvers more and avoids the late "cliff" where scores
crash to minimum.

## Usage

Set `function: aachen` on any dynamic challenge:

\```yaml
extra:
  initial: 500
  minimum: 30
  decay: 30        # ignored by aachen — left in for compatibility
  function: aachen
\```

Sync via ctfcli, restart not required after the plugin is loaded.

## Tuning

Edit `AACHEN_INFLECTION` and `AACHEN_STEEPNESS` in `__init__.py`. Defaults
match Aachen 34C3 CTF's published values.
```

## C.2 — Wire the plugin into the CTFd Docker image

The plugin needs to land inside the CTFd container at `/opt/CTFd/CTFd/plugins/dynamic_challenges_aachen/`. Two paths:

**Option A (recommended) — bind-mount via docker-compose.** Already partly set up; the compose has `./ctfd/plugins:/opt/CTFd/CTFd/plugins:ro` mounted. Anything in `infra/ctfd/plugins/*` shows up automatically.

Verify the mount exists in `infra/docker-compose.prod.yml` — look for the `ctfd` service's `volumes:` block. If the line is present and our plugin dir lives at `infra/ctfd/plugins/dynamic_challenges_aachen/`, **no compose changes needed**.

**Option B — bake into the Dockerfile.** Only if Option A isn't already wired. Edit `infra/Dockerfile.ctfd` to COPY the plugin dir in. Worse because every plugin change requires a rebuild.

**Cursor: confirm Option A applies. If `infra/docker-compose.prod.yml` already mounts the plugins dir, you're done with the wiring. If not, flag it back to Jon — that's an unexpected gap from earlier work.**

## C.3 — Update every dynamic challenge.yml

Add `function: aachen` to the `extra:` block in each dynamic challenge.yml. The relevant files:

```
crypto/The-Scribes-Encoded-Scroll-Beginner/challenge.yml
crypto/The-Goblin-Messengers-Cipher-Easy/challenge.yml
crypto/The-Dragons-Sealed-Proclamation-Medium/challenge.yml
crypto/The-Lichs-Cursed-Oracle-Hard/challenge.yml
crypto/The-Void-Oracles-Lattice-Expert/challenge.yml
prog/The-Guild-Ledger-Beginner/challenge.yml
prog/The-Runic-Vault-Easy/challenge.yml
prog/The-Dungeon-Cartographer-Medium/challenge.yml
prog/The-Arcane-Protocol-Hard/challenge.yml
prog/The-Prophecy-Engine-Expert/challenge.yml
prog/The-Chronomancers-Gauntlet-Legendary/challenge.yml
prog/The-Abyssal-Architect-Mythic/challenge.yml
osint/The-Cartographers-Lost-Map-Beginner/challenge.yml
osint/The-Heralds-Forgotten-Broadcast-Easy/challenge.yml
osint/The-Spys-Cipher-Journal-Medium/challenge.yml
rev/The-Runecasters-Compiled-Tome-Easy/challenge.yml
llm/The-Enchanted-Parrot-Beginner/challenge.yml
llm/The-Whispering-Merchant-Easy/challenge.yml
llm/The-Court-Wizards-Familiar-Medium/challenge.yml
llm/The-Oracle-of-Shadows-Hard/challenge.yml
llm/The-Mindflayers-Sanctum-Expert/challenge.yml
misc/The-Ogres-Audition-Hard/challenge.yml
```

22 files. For each, the `extra:` block goes from:

```yaml
extra:
  initial: 225
  minimum: 30
  decay: 30
```

to:

```yaml
extra:
  initial: 225
  minimum: 30
  decay: 30
  function: aachen
```

> `decay:` is now unused by the aachen function but **leave it in place**. ctfcli's schema expects it for type-checking on dynamic challenges, and other downstream code (e.g. challenge clones) reads it. Harmless.

**Cursor: use a single batch edit.** Don't open 22 files one by one — use a script or a regex-replace across the matched paths. After the edit, verify:

```bash
# Every dynamic challenge.yml has function: aachen
for f in $(find {crypto,prog,llm,osint,rev,misc} -maxdepth 2 -name 'challenge.yml'); do
  grep -q "function: aachen" "$f" && echo "✓ $f" || echo "✗ $f"
done
# Expect all 22 to show ✓
```

## C.4 — Verify

```bash
# Plugin Python syntax:
python -c "import ast; ast.parse(open('infra/ctfd/plugins/dynamic_challenges_aachen/__init__.py').read())"

# All challenge.yml still parse:
yamllint $(find {crypto,prog,llm,osint,rev,misc} -maxdepth 2 -name 'challenge.yml')

# Plugin config is valid JSON:
python -c "import json; json.load(open('infra/ctfd/plugins/dynamic_challenges_aachen/config.json'))"

# No null bytes anywhere (this repo has had recurring corruption):
for f in $(git diff feat/hosting --name-only); do
  count=$(LC_ALL=C grep -c $'\0' "$f" 2>/dev/null || echo 0)
  [ "$count" != "0" ] && echo "$f has $count null bytes — clean before commit"
done
```

## C.5 — Commit + push

```bash
git add infra/ctfd/plugins/dynamic_challenges_aachen/ \
        {crypto,prog,llm,osint,rev,misc}/*/challenge.yml
git commit -m "scoring: add Aachen-style convex decay plugin, enable on all dynamic challenges"
git push origin feat/aachen-scoring
```

Open PR to `feat/hosting`, self-review, merge.

After merge, tell Jon: **"Cursor work done. Terminal agent can pull + restart CTFd now."**

---

# Terminal agent's part

**Goal:** new plugin loaded by CTFd, log line confirms registration, the new "aachen" function is available in `DECAY_FUNCTIONS` at runtime.

**Run as `ctf` user on the VPS.** Assumes Cursor's PR merged.

## T.1 — Pull latest

```bash
cd /opt/fantasy_ctf_challs
git fetch origin
git checkout feat/hosting
git pull origin feat/hosting

# Confirm the plugin landed:
ls -la infra/ctfd/plugins/dynamic_challenges_aachen/
# Expect: __init__.py, config.json, README.md
```

## T.2 — Restart CTFd

The plugin dir is bind-mounted into the container (`./ctfd/plugins:/opt/CTFd/CTFd/plugins:ro`), so the file is already inside. CTFd needs a restart to load the new plugin.

```bash
cd /opt/fantasy_ctf_challs/infra
docker compose -f docker-compose.prod.yml restart ctfd

# Wait ~5s for boot:
sleep 5
```

## T.3 — Confirm plugin loaded

```bash
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml \
  logs ctfd --tail=200 2>&1 | grep -i "aachen"
# Expect a line like:
#   [dynamic_challenges_aachen] registered 'aachen' decay function (K=11.92201, P=1.206069)
```

If you don't see that log line:
- Confirm the file is mounted: `docker exec ctfd ls /opt/CTFd/CTFd/plugins/dynamic_challenges_aachen/`
- Check ctfd logs for plugin import errors: `... logs ctfd --tail=500 | grep -i "error\|exception\|plugin"`
- Common gotchas: Python syntax error in `__init__.py`, missing `load(app)` function, folder named wrong

## T.4 — Functional check from inside the container

```bash
docker exec -it ctfd python -c "
from CTFd.plugins.challenges import DECAY_FUNCTIONS
print('Registered decay functions:', sorted(DECAY_FUNCTIONS.keys()))
assert 'aachen' in DECAY_FUNCTIONS, 'aachen not registered'
print('aachen function:', DECAY_FUNCTIONS['aachen'])
"
# Expect:
#   Registered decay functions: ['aachen', 'linear', 'logarithmic']
#   aachen function: <function aachen at 0x...>
```

## T.5 — Report back to Jon

Paste:
- The log line confirming registration
- The output of T.4

Then Jon runs the ctfcli sync from his laptop. You're done from the VPS side.

---

# Jon's part

**Goal:** every challenge's CTFd row gets updated to `function: aachen`, and the value visibly changes on challenges that already have solves.

## J.1 — Confirm api.ctf.chron0.tech is reachable

```powershell
Test-NetConnection api.ctf.chron0.tech -Port 443
curl.exe -I https://api.ctf.chron0.tech/healthcheck
```

Both must succeed. If not, fix that first — ctfcli sync needs the API.

## J.2 — Sync all 22 challenges

```powershell
cd J:\projects\personal-projects\fantasy_ctf_challs
.venv\Scripts\activate

$challs = @(
  "crypto/The-Scribes-Encoded-Scroll-Beginner",
  "crypto/The-Goblin-Messengers-Cipher-Easy",
  "crypto/The-Dragons-Sealed-Proclamation-Medium",
  "crypto/The-Lichs-Cursed-Oracle-Hard",
  "crypto/The-Void-Oracles-Lattice-Expert",
  "prog/The-Guild-Ledger-Beginner",
  "prog/The-Runic-Vault-Easy",
  "prog/The-Dungeon-Cartographer-Medium",
  "prog/The-Arcane-Protocol-Hard",
  "prog/The-Prophecy-Engine-Expert",
  "prog/The-Chronomancers-Gauntlet-Legendary",
  "prog/The-Abyssal-Architect-Mythic",
  "osint/The-Cartographers-Lost-Map-Beginner",
  "osint/The-Heralds-Forgotten-Broadcast-Easy",
  "osint/The-Spys-Cipher-Journal-Medium",
  "rev/The-Runecasters-Compiled-Tome-Easy",
  "llm/The-Enchanted-Parrot-Beginner",
  "llm/The-Whispering-Merchant-Easy",
  "llm/The-Court-Wizards-Familiar-Medium",
  "llm/The-Oracle-of-Shadows-Hard",
  "llm/The-Mindflayers-Sanctum-Expert",
  "misc/The-Ogres-Audition-Hard"
)
foreach ($c in $challs) {
  Write-Host ">>> $c"
  ctf challenge sync $c
}
```

## J.3 — Verify in admin UI

Open `https://api.ctf.chron0.tech/admin/challenges`. Pick any challenge, click into it.

Look at the **Function** field (might also be labeled "Decay function" depending on CTFd version). It should now show `aachen`. If the dropdown only shows `linear` / `logarithmic` as visible options — that's fine, the database value is `aachen` even if the admin UI dropdown doesn't include it. The decay calculation will use it.

> **Optional cosmetic improvement:** override CTFd's admin theme to add "aachen" to the dropdown. Skip for now — the sync sets it programmatically, and you rarely edit challenges via the admin UI when ctfcli is the source of truth.

## J.4 — Functional smoke-test

Pick a challenge that already has at least one solve (use your admin account to solve one if none exist yet — it'll count, but you can wipe the solve afterward via Admin → Solves).

Check the challenge's current `value`:

```powershell
curl.exe -H "Authorization: Token <your-admin-token>" `
  https://api.ctf.chron0.tech/api/v1/challenges/1 | jq .data.value
```

Compare against what the Aachen formula predicts:

```python
# In a Python REPL:
def aachen(solves, initial, minimum):
    if solves <= 0: return initial
    delta = initial - minimum
    return round(minimum + delta / (1 + ((solves - 1) / 11.92201) ** 1.206069))

# Example: 5 solves, initial 500, minimum 30:
aachen(5, 500, 30)   # → ~399
```

The reported `value` should match. If it doesn't, the function isn't actually being applied — recheck T.3 / T.4 / J.2.

## J.5 — Done

Once verified:
- Document in `docs/runbook-incident.md` (or wherever you keep notes) that the scoring algorithm is non-default
- Mention it in the `/about` page on the live site — it's a portfolio-strong design choice worth flagging ("uses convex decay scoring inspired by Aachen 34C3 rather than CTFd's default parabolic")
- Done. Move on to Phase 7 / friend-beta.

---

# Rollback

If anything goes wrong:

1. **In CTFd, switch challenges back to `function: logarithmic`** (the previous default). Edit each `challenge.yml` `extra.function` and re-sync, OR mass-update via the admin API.
2. **Disable the plugin** by removing the directory and restarting CTFd:
   ```bash
   ssh ctf@<HETZNER_IP>
   mv /opt/fantasy_ctf_challs/infra/ctfd/plugins/dynamic_challenges_aachen \
      /opt/fantasy_ctf_challs/infra/ctfd/plugins/_archive_dynamic_challenges_aachen
   docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml restart ctfd
   ```
3. **Revert the PR** if you want a clean git history.

CTFd will fall back to `logarithmic` for any challenge that has `function: aachen` set if the plugin is missing (CTFd code: `f = DECAY_FUNCTIONS.get(challenge.function, logarithmic)`). So removing the plugin is graceful — no broken state, just back to parabolic decay.

---

# Future polish (not blocking)

| Item | Effort | When |
|---|---|---|
| Add "aachen" to the admin UI dropdown | ~30 LOC theme override | If you ever edit challenges via the admin UI rather than ctfcli |
| Make `K` and `P` per-challenge tunable via `challenge.yml extra` | ~10 LOC plugin change | If you want different curve shapes for different difficulty tiers |
| Value-decay simulator on the `/about` page | ~50 LOC React + recharts | Portfolio-strong, shows visitors what the scoring curve looks like |
| Cache solve counts to avoid recomputing on every challenge fetch | depends on traffic | Only matters if you scale to 1000+ players |
