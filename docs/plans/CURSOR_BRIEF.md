# FantasyCTF — Cursor Brief

**Audience:** Cursor doing local-repo work on Jon's machine.
**Companion docs:**
- `HOSTING_PLAN_V3.md` — strategy and *why*. Source of truth for decisions.
- `EXECUTION_PLAYBOOK.md` — full imperative playbook with complete file contents. **You'll reference this by section number constantly. Don't duplicate content from it; read it.**
- `VPS_OPERATIONS.md` — what the terminal agent does. Out of scope for you.

This brief is a **workflow and ordering document**, not a content document. The playbook has the file contents; this doc tells you the order, the constraints, and the handoff points.

---

## What this doc owns

- The execution order across two repositories.
- Which files Cursor creates, edits, or moves.
- Explicit handoff points where Cursor stops and waits for the terminal agent or Jon.
- Lint/build verification gates between phases.
- Things Cursor must NOT do (footguns).

## What this doc does NOT own

- Anything that happens over SSH on the Hetzner VPS — the terminal agent has its own playbook (`VPS_OPERATIONS.md`).
- Web-UI clicks (Hetzner Cloud, Cloudflare DNS, Vercel project settings, GitHub OAuth App, GitHub Environments + Secrets, CTFd admin panel). Jon does these manually; Cursor must not try.
- Browser-based CTFd setup wizard.
- Any command that requires SSH access.

---

## The two working directories

| Tag | Path | Repo on GitHub |
|---|---|---|
| `MONOREPO` | `J:\projects\personal-projects\fantasy_ctf_challs` | `jondmarien/fantasy_ctf_challs` |
| `SITE_REPO` | `J:\projects\personal-projects\ctfd-live-scoreboard` | `jondmarien/ctfd-live-scoreboard` |

**Always confirm the working directory before editing.** Most files have repo-specific paths; mixing them up will break the build.

## Branches

- `MONOREPO`: active branch is `feat/hosting`. Land your work in feature branches off `feat/hosting`, PR back to `feat/hosting`, eventually merge to `main`.
- `SITE_REPO`: create `feat/full-site` off `main`. Land work there, PR to `main`. Vercel auto-deploys `main` to `ctf.chron0.tech`.

## Build/lint commands

| Repo | Build | Lint |
|---|---|---|
| `MONOREPO` | (no build — Python challenges, run individual `solve.py` files) | `gitleaks detect --no-git`, `yamllint .`, `hadolint **/Dockerfile` |
| `SITE_REPO` | `bun run build` | `bun run lint`, `bunx tsc -b --noEmit` |

**Run the appropriate lint/build after every phase before moving on.** Don't push broken code expecting CI to catch it.

---

# Execution order

Phases run roughly in parallel with the terminal agent's work. Some Cursor phases must complete before the agent can proceed; some agent phases must complete before Cursor can proceed. Handoffs are flagged as 🤝 below.

```
Cursor                                 Terminal agent
─────────────────────────────────────  ────────────────────────────────────
A.  Monorepo infra files               (waiting)
    └─ commit + push ────────────────► 2.1–2.4  bootstrap, .env, compose up
                                       2.5      🤝 wait for Jon (CTFd wizard)
                                       2.6      OAuth env wiring (after Jon)
                                       2.7      plugin clones + restart
B.  Site repo: package.json,           (independent of agent's progress)
    vercel.json, proxy edits
    └─ deploy via Vercel auto
C.  Site repo: routes + pages +
    components + hooks (the bulk)
    └─ deploy via Vercel auto

(both sides converge here)

D.  Monorepo: per-challenge compose    8.       🤝 wait for Cursor's D
    updates + .ctf/config              ────────► then bring up challenges
E.  Monorepo: CI/CD workflow YAMLs     9.       socket-proxy
                                       10–11.   restic + restore drill
F.  Site repo polish + final review    12.      operational
```

---

# Phase A — Monorepo infra files

**Goal:** create every file the terminal agent needs to bring up the stack. Push to `feat/hosting`. Stop and let the agent run.

**Working dir:** `MONOREPO`.

## A.1 Files to create

Reference: `EXECUTION_PLAYBOOK.md` §2.2, §2.4, §2.4 (litellm config). Copy file contents verbatim from the playbook.

| File | Source section | Purpose |
|---|---|---|
| `infra/bootstrap.sh` | Playbook §2.2 | Run-once script to install Docker, create `ctf` user, clone repo, harden SSH |
| `infra/docker-compose.prod.yml` | Playbook §2.4 | Production stack: Traefik, CTFd, Postgres, Redis, LiteLLM, Uptime Kuma |
| `infra/litellm/config.yml` | Playbook §2.4 | LiteLLM model routing — OpenAI, Anthropic, Gemini, OpenRouter |
| `infra/secrets/.gitkeep` | (new, empty) | Just so the directory exists in git; the actual `.env.prod` lives only on the VPS |
| `infra/README.md` | (new — write a short stub) | One paragraph: "Infra for the FantasyCTF VPS. Files in this dir are deployed to Hetzner. Secrets live on the VPS only, never in git." |
| `.gitignore` | append | Add `infra/secrets/.env*`, `infra/secrets/restic.env`, `node_modules/`, `dist/` |

## A.2 Make `bootstrap.sh` executable

```bash
chmod +x infra/bootstrap.sh
git add infra/bootstrap.sh
git update-index --chmod=+x infra/bootstrap.sh
```

## A.3 Verify

```bash
yamllint infra/docker-compose.prod.yml infra/litellm/config.yml
shellcheck infra/bootstrap.sh
hadolint infra/**/Dockerfile  # no Dockerfiles yet — should pass trivially
gitleaks detect --no-git
```

If any tool isn't installed locally, that's fine — the lint workflow will catch it on PR.

## A.4 Commit + push

```bash
git checkout -b feat/infra-foundations feat/hosting
git add infra/ .gitignore
git commit -m "infra: add bootstrap, prod compose, litellm config"
git push -u origin feat/infra-foundations
# Open PR to feat/hosting, self-review, merge.
```

## 🤝 A.5 Handoff to terminal agent

Tell Jon: **"Phase A done — terminal agent can now run sections 1–4 of `VPS_OPERATIONS.md`."**

Cursor then proceeds to Phase B (independent of agent).

---

# Phase B — Site repo: prep + proxy edits

**Goal:** site repo metadata + Vercel proxy updated to recognize the new domains. Vercel deploys; existing scoreboard users still work.

**Working dir:** `SITE_REPO`.

## B.1 Branch + scaffold

```bash
cd J:\projects\personal-projects\ctfd-live-scoreboard
git checkout -b feat/full-site main
```

## B.2 Files to edit

Reference: `EXECUTION_PLAYBOOK.md` §3.1, §3.2.

| File | Change | Source |
|---|---|---|
| `package.json` | `name`: `app` → `chron0-ctf-scoreboard`. `version`: `0.0.0` → `1.0.0`. | Playbook §3.1 |
| `vercel.json` | Replace contents with the version that adds the redirect block for `scoreboard.chron0.tech` and `scoreboard.issessions.ca` → `ctf.chron0.tech/scoreboard`. | Playbook §3.1 |
| `api/[...path].ts` | Replace lines 1–20 with the env-var-ized `CTFD_BASE_URL` and updated `ALLOWED_HOSTS` / `ALLOWED_ORIGINS` (keeps existing ISSessions entries during transition). | Playbook §3.2 |
| `.env.example` | Add `CTFD_BASE_URL=https://api.ctf.chron0.tech` line. Keep `CTFD_API_TOKEN` line. | (one-line edit) |

## B.3 Verify

```bash
bun run build               # passes
bunx tsc -b --noEmit        # no TS errors
bun run lint                # eslint clean
```

## B.4 Commit + push

```bash
git add package.json vercel.json api/[...path].ts .env.example
git commit -m "site: rename to chron0-ctf-scoreboard, add ctf.chron0.tech, redirect legacy hosts"
git push -u origin feat/full-site
# Open PR to main. Don't merge yet — wait until Phase C is also ready, ship together.
```

> **Why not merge now:** the proxy update references `ctf.chron0.tech` but the Vercel project doesn't have that domain attached yet (Jon does that manually). If you deploy this with no domain attached, nothing changes — but if you want clean PR history, batch B + C into one merge.

---

# Phase C — Site repo: routes, pages, components, hooks

**Goal:** the full SPA. Landing page, login flow, challenge browser, challenge detail with flag submission, BYO-key + LLM demo animation, session-bound solutions, about page.

**Working dir:** `SITE_REPO` on `feat/full-site`.

## C.1 Order of file creation

The order matters because some files import others. Work from leaves to roots:

| Step | File | Why now |
|---|---|---|
| 1 | `src/lib/ctfdClient.ts` | Imported by every hook |
| 2 | `src/hooks/useAuth.ts` | Imported by useSubmitFlag, all pages |
| 3 | `src/hooks/useSolves.ts` | Imported by ChallengesPage, SolutionPage |
| 4 | `src/hooks/useSubmitFlag.ts` | Imported by FlagSubmissionForm |
| 5 | `src/components/forms/FlagSubmissionForm.tsx` | Imported by ChallengeDetailPage |
| 6 | `src/components/forms/BYOKeyForm.tsx` | Imported by ChallengeDetailPage |
| 7 | `src/data/llm-demos.ts` | Imported by LLMDemoAnimation |
| 8 | `src/components/llm/LLMDemoAnimation.tsx` | Imported by ChallengeDetailPage |
| 9 | `src/pages/LandingPage.tsx` | Imported by App.tsx |
| 10 | `src/pages/ChallengesPage.tsx` | Imported by App.tsx |
| 11 | `src/pages/ChallengeDetailPage.tsx` | Imported by App.tsx |
| 12 | `src/pages/SolutionPage.tsx` | Imported by App.tsx |
| 13 | `src/pages/LoginCallbackPage.tsx` | Imported by App.tsx |
| 14 | `src/pages/AboutPage.tsx` | Imported by App.tsx |
| 15 | `src/App.tsx` | Last — wires everything up |
| 16 | Archive `SkillsSheridanPage` + SS components | After App.tsx no longer references them |

Reference: `EXECUTION_PLAYBOOK.md` §3.4–3.16. **Copy file contents verbatim** unless something doesn't compile, in which case fix and note the deviation.

## C.2 Archival of Skills Sheridan

After step 15 (App.tsx) is in place, move:

```bash
git mv src/pages/SkillsSheridanPage.tsx src/pages/_archive/SkillsSheridanPage.tsx

# These may or may not exist; ignore errors:
git mv src/components/background/SSBackground.tsx src/components/_archive/SSBackground.tsx 2>/dev/null || true
git mv src/components/ui/SSHeader.tsx src/components/_archive/SSHeader.tsx 2>/dev/null || true
git mv src/components/ui/SSFooter.tsx src/components/_archive/SSFooter.tsx 2>/dev/null || true
```

The `SS_THEME` export in `src/contexts/ThemeContext.tsx` can stay — it's an unused export but not breaking.

## C.3 Markdown rendering for SolutionPage

The playbook leaves `renderMarkdown` in `SolutionPage.tsx` as a placeholder `<pre>`. Replace with a real library:

```bash
bun add marked
bun add -d @types/marked
```

Then in `SolutionPage.tsx`, replace the `renderMarkdown` function with:

```ts
import { marked } from "marked";

function renderMarkdown(md: string): string {
  // marked is async-by-default in v15+; force sync.
  return marked.parse(md, { async: false }) as string;
}
```

Marked sanitizes some HTML by default but **not all** — if you want bulletproof XSS protection, also add `dompurify`:

```bash
bun add dompurify
bun add -d @types/dompurify
```

```ts
import { marked } from "marked";
import DOMPurify from "dompurify";

function renderMarkdown(md: string): string {
  const raw = marked.parse(md, { async: false }) as string;
  return DOMPurify.sanitize(raw);
}
```

Use the DOMPurify version. Solution writeups come from the trusted monorepo, but defense-in-depth is cheap.

## C.4 Solution writeup fetch — pin the branch

The playbook has `SOLUTIONS_BASE_URL` pointed at the `feat/hosting` branch. **Before final merge to `main`**, change it to:

```ts
const SOLUTIONS_BASE_URL =
  "https://raw.githubusercontent.com/jondmarien/fantasy_ctf_challs/main";
```

Tag this as a TODO comment so it's not forgotten:

```ts
// TODO: when monorepo merges feat/hosting → main, update branch ref.
//       Or replace with a build-time-generated manifest to avoid raw GitHub fetches entirely.
```

A build-time manifest is better long-term (no rate limits, faster, doesn't expose source URLs in DevTools). Defer that to a follow-up PR; it's not blocking launch.

## C.5 Verify

```bash
bun run build                 # MUST pass
bunx tsc -b --noEmit          # no TS errors
bun run lint                  # eslint clean
bun run dev                   # local dev server, manually click through routes
```

Manual smoke-tests on `bun run dev`:

- [ ] `/` — landing page renders, "Sign in with GitHub" button (or "Enter the Quest Hall" if logged in via dev session)
- [ ] `/scoreboard` — existing FantasyCtfPage renders
- [ ] `/challenges` — challenge browser renders (mock data fallback is fine pre-CTFd)
- [ ] `/challenges/the-enchanted-parrot` — detail page renders, shows BYO-key form + demo animation
- [ ] `/login/callback` — renders (will error on missing CTFd session in dev, expected)
- [ ] `/about` — renders, all links work
- [ ] `/solutions/the-enchanted-parrot` — shows "complete this quest first" gate
- [ ] Random unknown path — redirects to `/`

## C.6 Commit + push + merge B+C together

```bash
git add src/ package.json bun.lockb   # bun.lockb if marked / dompurify added
git commit -m "site: full SPA — landing, challenges, flag submit, solutions, BYO-key LLM, archive Skills Sheridan"
git push origin feat/full-site
```

Open PR to `main`, self-review, merge. Vercel deploys.

## 🤝 C.7 Handoff to Jon

Tell Jon:
- "Phase B+C merged and deployed to Vercel."
- "Add `ctf.chron0.tech` and `scoreboard.chron0.tech` as custom domains in the Vercel project (UI work)."
- "Set Vercel env vars (Production scope): `CTFD_BASE_URL=https://api.ctf.chron0.tech` and `CTFD_API_TOKEN=<from CTFd setup>`."
- "Smoke-test: `curl -I https://scoreboard.chron0.tech` should return 308 → `ctf.chron0.tech/scoreboard`."

---

# Phase D — Monorepo: per-challenge compose updates

**Goal:** every Dockerised challenge's compose file routes through Traefik, pulls a GHCR image instead of building locally, and reads its flag from `${FLAG_*}` env vars.

**Working dir:** `MONOREPO` on a new branch `feat/challenge-composes` off `feat/hosting`.

## D.1 .ctf/config

`.ctf/config` is gitignored; Cursor can't write the live token. Just edit the in-repo template (if there is one) or the `EXECUTION_PLAYBOOK.md` reference for Jon to copy locally.

```bash
# Skip — Jon updates this manually with his actual token.
```

## D.2 Challenges to update

Reference: `EXECUTION_PLAYBOOK.md` §4.3 for the per-challenge compose template. There are 10 Dockerised challenges:

| Challenge dir | Subdomain | Notes |
|---|---|---|
| `crypto/The-Lichs-Cursed-Oracle-Hard` | `lich.ctf.chron0.tech` | TCP socket — use HostSNI router |
| `prog/The-Arcane-Protocol-Hard` | `arcane.ctf.chron0.tech` | TCP socket |
| `prog/The-Prophecy-Engine-Expert` | `prophecy.ctf.chron0.tech` | TCP socket |
| `prog/` (root compose, consolidated) | `chrono.ctf.chron0.tech`, `architect.ctf.chron0.tech` | Two challenges in one container, two TCP routers |
| `llm/The-Enchanted-Parrot-Beginner` | `parrot.ctf.chron0.tech` | HTTP — use HTTP router |
| `llm/The-Whispering-Merchant-Easy` | `whispering.ctf.chron0.tech` | HTTP |
| `llm/The-Court-Wizards-Familiar-Medium` | `court.ctf.chron0.tech` | HTTP |
| `llm/The-Oracle-of-Shadows-Hard` | `oracle.ctf.chron0.tech` | HTTP |
| `llm/The-Mindflayers-Sanctum-Expert` | `mindflayer.ctf.chron0.tech` | HTTP |
| `misc/The-Ogres-Audition-Hard` | `ogre.ctf.chron0.tech` | HTTP |

For each, edit the existing `docker-compose.yml`:

1. Replace `build: .` (or `build:` with a context) → `image: ghcr.io/jondmarien/fantasy-ctf-<slug>:latest`
2. Replace any direct provider-key env (LLM challenges using Gemini directly) → `LITELLM_BASE_URL=http://litellm:4000/v1`
3. Replace hardcoded flag → `FLAG=${FLAG_<NAME>}` reading from compose's env
4. Add Traefik labels (HTTP or TCP form per playbook §4.3)
5. Add `networks: [chal_<name>, proxy]` and define `chal_<name>` with `internal: true`, `proxy` as `external: true`
6. Add basic hardening (Phase F refines): `read_only: true`, `cap_drop: [ALL]`, `security_opt: [no-new-privileges:true]`, `mem_limit: 256m`

## D.3 LLM `llm/shared/` rewire

Each LLM challenge's FastAPI server currently calls `google-genai` directly. Rewire to call LiteLLM:

```python
# Before:
from google import genai
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

# After (using openai-python lib pointed at LiteLLM):
from openai import OpenAI
client = OpenAI(
    base_url=os.environ.get('LITELLM_BASE_URL', 'http://litellm:4000/v1'),
    api_key=request.headers.get('X-Player-API-Key', 'dummy'),  # forwarded from SPA
)
```

Player keys arrive in the request from the SPA's BYO-key form (header `X-Player-API-Key`). Forward to LiteLLM via the `Authorization` header. **Confirm with Jon before changing the request contract** — there may be existing solve scripts that assume a specific shape.

## D.4 Verify

```bash
yamllint $(find {crypto,prog,llm,osint,rev,misc} -name 'docker-compose.yml')
hadolint $(find {crypto,prog,llm,osint,rev,misc} -name 'Dockerfile')
```

Don't try to `docker compose up` locally — these reference GHCR images that don't exist yet (CI builds them on push) and the `proxy` external network only exists on the VPS.

## D.5 Commit + push

```bash
git add crypto/ prog/ llm/ misc/
git commit -m "challenges: switch composes to GHCR images, Traefik labels, LiteLLM rewire"
git push origin feat/challenge-composes
# Open PR to feat/hosting, self-review, merge.
```

## 🤝 D.6 Handoff to terminal agent

Tell Jon: **"Phase D merged — terminal agent can now run section 8 of `VPS_OPERATIONS.md` (per-challenge flags + bring up Dockerised challenges)."**

The agent will need flag values from Jon (each challenge's intended flag) to populate `.env.prod`.

---

# Phase E — Monorepo: CI/CD workflow YAMLs

**Goal:** GitHub Actions sync challenges automatically and run lint + solve tests on PRs.

**Working dir:** `MONOREPO` on `feat/ci-cd` off `feat/hosting`.

## E.1 Files to create

Reference: `EXECUTION_PLAYBOOK.md` §5.1, §5.2, §5.3.

| File | Source section |
|---|---|
| `.github/workflows/sync-ctfd.yml` | Playbook §5.1 |
| `.github/workflows/lint.yml` | Playbook §5.2 |
| `.github/workflows/test-solves.yml` | Playbook §5.3 |

## E.2 ⚠️ Watch the MAP shorthand in sync-ctfd.yml

The `sync-metadata` step in the playbook has:

```yaml
declare -A MAP=( ... )   # paste same map
```

**Don't leave `( ... )`.** Paste the same map array as in the `build-images` step's `paths` step — all 22 challenge keys. If you leave it abbreviated, the sync silently does nothing.

## E.3 Verify

```bash
yamllint .github/workflows/
# actionlint if installed:
actionlint .github/workflows/
```

## E.4 Commit + push

```bash
git add .github/
git commit -m "ci: add sync-ctfd, lint, test-solves workflows"
git push origin feat/ci-cd
```

Open PR. The lint workflow will run against itself — expect green. Merge.

## 🤝 E.5 Handoff to Jon

Tell Jon to populate GitHub Environment secrets (UI work):

| Env | Secret | Value |
|---|---|---|
| `production` | `CTFD_URL` | `https://api.ctf.chron0.tech` |
| `production` | `CTFD_TOKEN` | from CTFd setup wizard |
| `production` | `VPS_HOST` | Hetzner IP |
| `production` | `VPS_SSH_KEY` | private key for `ctf` user (PEM) |

Test by triggering `workflow_dispatch` with `environment: production` and confirming the job pauses for your approval.

---

# Phase F — Monorepo: hardening + restic script

**Goal:** every challenge compose has full hardening; restic backup script is in the repo.

**Working dir:** `MONOREPO` on `feat/hardening` off `feat/hosting`.

## F.1 Audit per-challenge composes

Walk every Dockerised compose and confirm:

- [ ] `read_only: true`
- [ ] `user: "1001:1001"`
- [ ] `cap_drop: [ALL]`
- [ ] `security_opt: [no-new-privileges:true, apparmor=docker-default]`
- [ ] `pids_limit: 128`
- [ ] `mem_limit: 256m`
- [ ] `cpus: '0.5'`
- [ ] `tmpfs:` for `/tmp` (and any other path the challenge writes to)
- [ ] Per-challenge bridge `internal: true`
- [ ] `proxy` network attached if exposed via Traefik

If a challenge writes to disk (e.g., uploads its own files), it can't use `read_only: true` — note the exception and use `tmpfs` instead, or accept a writable layer.

## F.2 docker-socket-proxy in main compose

Add the `socket-proxy` service to `infra/docker-compose.prod.yml`. Reference: `EXECUTION_PLAYBOOK.md` §6.2.

## F.3 Restic script

Create `infra/backups/restic.sh` from `EXECUTION_PLAYBOOK.md` §6.4.

```bash
chmod +x infra/backups/restic.sh
git update-index --chmod=+x infra/backups/restic.sh
```

## F.4 Verify

```bash
yamllint infra/docker-compose.prod.yml
shellcheck infra/backups/restic.sh
```

## F.5 Commit + push

```bash
git add infra/ crypto/ prog/ llm/ osint/ rev/ misc/
git commit -m "hardening: audit per-chal composes, add socket-proxy, add restic backup script"
git push origin feat/hardening
```

Open PR to `feat/hosting`, self-review, merge.

## 🤝 F.6 Handoff to terminal agent

Tell Jon: **"Phase F merged — terminal agent can now run sections 9 + 10 of `VPS_OPERATIONS.md` (socket-proxy + restic setup)."**

---

# Phase G — Final review + merge to main

**Goal:** site repo and monorepo both clean and ready for soft launch.

## G.1 Site repo final review

```bash
cd SITE_REPO
git checkout main
git pull
bun run build
bun run lint
bunx tsc -b --noEmit
```

Click through every route on the deployed `https://ctf.chron0.tech`:

- [ ] `/` — landing
- [ ] OAuth login round-trip works
- [ ] `/challenges` shows real challenge data (not mock)
- [ ] `/challenges/the-scribes-encoded-scroll` (or another live challenge) — flag submission works (correct flag returns "Quest completed")
- [ ] `/solutions/the-scribes-encoded-scroll` — gates on solve, shows writeup once solved
- [ ] LLM challenge: BYO-key form persists across reload (sessionStorage), demo animation plays
- [ ] `/scoreboard` — live data
- [ ] `/about` — links work
- [ ] `curl -I https://scoreboard.chron0.tech` returns 308 → `ctf.chron0.tech/scoreboard`
- [ ] `curl -I https://scoreboard.issessions.ca` returns 308 → `ctf.chron0.tech/scoreboard`

## G.2 Monorepo: merge feat/hosting → main

```bash
cd MONOREPO
git checkout main
git merge feat/hosting --no-ff
git push origin main
```

This kicks the `sync-ctfd.yml` workflow's `push` trigger → staging deploy.

## G.3 Update SOLUTIONS_BASE_URL

In `SITE_REPO/src/pages/SolutionPage.tsx`, change the branch ref from `feat/hosting` to `main`. Commit + push.

## G.4 Tag both repos

```bash
# Monorepo:
cd MONOREPO
git tag -a v1.0.0 -m "FantasyCTF — chron0.tech launch"
git push origin v1.0.0

# Site:
cd SITE_REPO
git tag -a v1.0.0 -m "Site launch on ctf.chron0.tech"
git push origin v1.0.0
```

---

# What Cursor must NOT do

These are footguns that will break the migration. Do not:

- ❌ **Rename the GitHub repo `ctfd-live-scoreboard`.** It stays. Only `package.json` `name` changes. Renaming breaks Vercel project linkage and any external links.
- ❌ **Run `docker compose down -v`** in any context. The `-v` deletes volumes (DB, uploads, certs). If you must take the stack down, use `docker compose down` only.
- ❌ **Edit the read-only proxy in `api/[...path].ts` to allow POSTs.** Authenticated calls go direct to `api.ctf.chron0.tech`, not through the proxy. The proxy is deliberately scoped to public reads.
- ❌ **Commit `infra/secrets/.env.prod`** or any file with real secrets. Verify gitignore catches it before commit.
- ❌ **Delete `SkillsSheridanPage.tsx`** rather than archiving. Move to `_archive/` so the multi-CTF capability is recoverable from working tree, not just git history.
- ❌ **SSH into the VPS.** That's the terminal agent's job. If a build error suggests an SSH operation, flag it back to Jon — don't try to fix it from your side.
- ❌ **Click through Vercel/Hetzner/Cloudflare/GitHub UIs.** Those are Jon's. If something needs UI work, list it as a handoff item, don't attempt it via API.
- ❌ **Push directly to `main` in either repo.** PR-and-merge always.
- ❌ **Skip `bun run build` before committing site repo changes.** Vercel will catch it but that's wasted deploy cycles and a broken deploy URL.
- ❌ **Pin `ctfcli` to anything other than `0.1.7`.** Alpha tool with breaking changes between minor versions.
- ❌ **Leave `MAP=( ... )` shorthand in `sync-ctfd.yml`.** Paste the full array.
- ❌ **Forget to bump `SOLUTIONS_BASE_URL` from `feat/hosting` → `main`** during Phase G.

---

# Quick file reference

| Want to | File | Repo |
|---|---|---|
| Update CTFd version | `infra/docker-compose.prod.yml` (`image: ctfd/ctfd:X.Y.Z`) | MONOREPO |
| Add a new challenge subdomain | edit that challenge's `docker-compose.yml`, add Traefik labels | MONOREPO |
| Add a new LLM provider | `infra/litellm/config.yml` | MONOREPO |
| Add a new SPA route | `src/pages/<Page>.tsx` + register in `src/App.tsx` | SITE_REPO |
| Update OAuth callback URL | `src/lib/ctfdClient.ts` (`loginUrl` function) | SITE_REPO |
| Change theme palette | `src/contexts/ThemeContext.tsx` (`FANTASY_THEME.classes`) | SITE_REPO |
| Add a hint to a challenge | `<chal>/ctfd_meta.json` (`hints` array) | MONOREPO — re-sync via ctfcli |
| Update writeup | `<chal>/solution/SOLUTION.md` | MONOREPO — `SolutionPage` fetches at runtime |
| Add a CI lint check | `.github/workflows/lint.yml` | MONOREPO |
| Update site SEO | `index.html` `<head>` and `vercel.json` headers | SITE_REPO |

---

# When in doubt

1. **Re-read the relevant section of `EXECUTION_PLAYBOOK.md`** before improvising. The playbook has the canonical content; this brief has the workflow.
2. **Stop and tell Jon** if a step's verification fails. Don't continue with broken state.
3. **Prefer small commits** with clear messages over large omnibus PRs.
4. **The proxy stays read-only.** If you find yourself wanting to add POST handling there, you're solving the wrong problem — go direct to `api.ctf.chron0.tech` instead.
