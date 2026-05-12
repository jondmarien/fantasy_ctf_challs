# FantasyCTF — Hosting Plan v3

**Target:** `ctf.chron0.tech` — Jon's permanent personal-portfolio CTF site hosting all 22 FantasyCTF challenges.
**Framing:** Personal portfolio under Jon's own domain. Originally designed for ISSessions Fantasy 2026 CTF; Jon has stepped down from exec to advisor, so the site is no longer a club service. Footer credit acknowledges the origin.
**Architecture (locked 2026-05-09, refined 2026-05-10):** Self-hosted CTFd on a Hetzner CPX21 VPS in Ashburn (~$10/mo all-in), behind Traefik with a Let's Encrypt wildcard. The frontend lives in the existing `ctfd-live-scoreboard` repo (kept as the GitHub repo name; `package.json` renamed internally to `chron0-ctf-scoreboard`), deployed on Vercel — extended from a scoreboard into a full SPA with flag submission, challenge browsing, and gated solution writeups. Two repos, two independent deploys.
**Author:** Jon Marien · written 2026-05-09, refined 2026-05-10. Supersedes archived `HOSTING_PLAN_V2.md` and the original `HOSTING_PLAN.md`, both in `docs/plans/archived/`. Plans now live in `docs/plans/`.

---

## 0 · TL;DR

The architectural pivot from v2: **drop the `frontend/` plan from the monorepo.** The existing `ctfd-live-scoreboard` repo is already 80–90% of what `frontend/` would have been — production-grade Vercel + Bun setup with a hardened CTFd proxy (rate limiting, host/origin allowlist, edge caching, 420 retry). Extending that repo to handle the full site (landing, login, challenges, flag submission, solutions, about) is dramatically less work than building parallel.

**The proxy stays read-only.** It's deliberately scoped to public scoreboard reads with an admin token. For player-authenticated actions (flag submit, hint unlock, `/users/me/solves`), the SPA hits `api.ctf.chron0.tech` **directly** with a player bearer token — no proxy involvement. This keeps the proxy small and hardened, matches CTFd's headless-API model, and avoids growing the proxy into something it wasn't designed for.

**Two repos:**

| Repo | Deploys to | Owns |
|---|---|---|
| `fantasy_ctf_challs` (this monorepo) | Hetzner CPX21 via SSH | Challenges, CTFd config, Traefik, LiteLLM, infra |
| `ctfd-live-scoreboard` (repo name unchanged; `package.json` → `chron0-ctf-scoreboard`) | Vercel | The full SPA (landing, scoreboard, challenges, flag submission, solutions, about) |

**Server is already provisioned.** Hetzner CPX21 in Ashburn is up, SSH works, cloud-init has run. Phase 1 is effectively done. Phase 2 (VPS bring-up: Docker, compose stack, CTFd setup wizard) is the next work.

**Total recurring cost: ~$10–13/mo** (~$120–155/year).

---

## 1 · Decisions log

| Decision | Choice | Reasoning |
|---|---|---|
| Backend platform | Self-hosted CTFd | Plugin support (Whale, OAuth), full theme control |
| VPS provider | Hetzner Cloud | ~5× cheaper than DO for the same shape |
| VPS instance | **CPX21** (3 vCPU AMD, 4 GB, 80 GB) | Headroom for CTFd + Postgres + Redis + Whale-spawned containers |
| VPS region | **Ashburn, VA (US-East)** | ~25ms RTT from Ontario; matters for socket challenges |
| Hetzner Backups | Enabled (~$1.50/mo) | Daily snapshot, 7-day retention |
| Reverse proxy | **Traefik v3** | Wildcard DNS-01, Docker-label discovery, native CORS middleware |
| TLS | Let's Encrypt wildcard `*.ctf.chron0.tech` via Cloudflare DNS-01 | One cert, all subdomains |
| Cloudflare proxy | On for SPA hosts (`ctf.`, `scoreboard.`); **off** for `api.` and `*.ctf.` | Preserves cookie origin headers; raw TCP for socket challenges |
| Public domains | `ctf.chron0.tech` (main), `api.ctf.chron0.tech` (CTFd API), `<chal>.ctf.chron0.tech` (per-challenge), `scoreboard.chron0.tech` → 301 to `ctf.chron0.tech/scoreboard`, `scoreboard.issessions.ca` → 301 to `ctf.chron0.tech/scoreboard` | Same eTLD+1 for cookie compatibility; legacy URLs redirect to canonical |
| Repo strategy | **Two repos, both deployable independently** — monorepo (challenges + infra) + sibling site (SPA) | Existing site repo is already most of the work |
| Site repo | GitHub repo stays `ctfd-live-scoreboard`; `package.json` `name` field → `chron0-ctf-scoreboard` | Avoids breaking GitHub history, deployed-domain memory, or any external references; internal name reflects new scope |
| Site stack | **Bun 1.x runtime**, Vite 7, React 19.2, TypeScript 5.9, Tailwind v4 (`@tailwindcss/vite`), shadcn, radix-ui, react-router-dom 7, framer-motion + motion, GSAP, lucide-react, recharts, tsparticles, OGL | All already installed in the existing repo |
| Site scope | Full custom UI with flag submission baked in | Theme control matters for portfolio |
| Multi-CTF support | Skills Sheridan **archived** (kept in repo history, removed from active routes); Fantasy theme becomes default at `/` | Single-tenant for now; multi-CTF capability remains in the codebase for future revival |
| Auth surface | OAuth via CTFd plugin (default GitHub) | Less spam, lower friction |
| Auth pattern | Bearer-token in `sessionStorage`, SPA hits `api.ctf.chron0.tech` directly for authenticated calls | Bypasses the read-only proxy cleanly |
| Public-read pattern | SPA → Vercel proxy (`/api/...`) → CTFd | Existing hardened proxy unchanged |
| LLM provider strategy | **BYO API key** via **LiteLLM** sidecar | $0 server-side LLM cost |
| LLM "demo" | Framer Motion animation of a successful solve | Zero abuse vector |
| Solutions visibility | Session-bound `/solutions/:slug` — checks `GET /api/v1/users/me/solves` | Robust, no fingerprinting fragility |
| ctfcli pin | `==0.1.7` with hand-rolled REST fallback documented | Alpha-tagged tool |
| CI/CD | GitHub Actions, two Environments (`staging`, `production`); prod requires manual approval | Cheapest blast-radius control |
| Image registry | GHCR (free for public repos) | One less account to manage |
| ISSessions branding | Footer credit only ("Originally designed for ISSessions Fantasy 2026 CTF") | Honors origin without claiming current affiliation |

---

## 2 · Architecture

```
                        ┌─────────────────────────────┐
                        │   Cloudflare DNS + proxy    │
                        │   (chron0.tech zone)        │
                        └──────────────┬──────────────┘
                                       │
        ┌──────────────────────────────┼─────────────────────────────┐
        │ proxied                      │ proxied                     │ DNS-only
        ▼                              ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐    ┌─────────────────────────┐
│       VERCEL         │    │   (legacy scoreboard │    │   Hetzner CPX21         │
│  ctf.chron0.tech     │    │    URL — see §4)     │    │   Ashburn, US-East      │
│  fantasy-ctf-site    │    │                      │    │   3 vCPU AMD / 4 GB     │
│  Bun + Vite + React  │    │                      │    │  ┌─────────────────┐    │
│                      │    │                      │    │  │  Traefik v3     │    │
│  Routes:             │    │                      │    │  │  *.ctf wildcard │    │
│   /                  │    │                      │    │  └────────┬────────┘    │
│   /scoreboard        │    │                      │    │           │             │
│   /challenges        │    │                      │    │   ┌───────┼───────┐     │
│   /challenges/:slug  │    │                      │    │   ▼       ▼       ▼     │
│   /solutions/:slug   │    │                      │    │ ┌────┐ ┌──┐ ┌──────┐    │
│   /login /about      │    │                      │    │ │CTFd│ │PG│ │Redis │    │
│                      │    │                      │    │ └────┘ └──┘ └──────┘    │
│  ┌────────────────┐  │    │                      │    │ ┌──────────────────────┐│
│  │ Vercel proxy   │  │    │                      │    │ │ Per-chal bridges     ││
│  │ /api/* → CTFd  │  │    │                      │    │ │ internal: true       ││
│  │ READ-ONLY      │  │    │                      │    │ │ oracle.ctf.… ↘       ││
│  │ admin token    │  │    │                      │    │ │ lich.ctf.…   →Traefik│
│  │ host allowlist │  │    │                      │    │ │ arcane.ctf.… ↗       ││
│  │ rate limited   │  │    │                      │    │ │ + LiteLLM sidecar    ││
│  └───────┬────────┘  │    │                      │    │ │   for LLM challs     ││
│          │           │    │                      │    │ └──────────────────────┘│
│  ┌───────┼───────┐   │    │                      │    │ ┌──────────────────────┐│
│  │ Direct API    │   │    │                      │    │ │ Uptime Kuma          ││
│  │ for auth ops  │   │    │                      │    │ └──────────────────────┘│
│  │ (POST attempt,│   │    │                      │    └────────┬────────────────┘
│  │ unlock hint,  │   │    │                      │             │
│  │ /me/solves)   │   │    │                      │             ▼
│  │ Bearer token  │   │    │                      │     api.ctf.chron0.tech
│  └───────────────┘   │    │                      │     (DNS-only — no CF proxy)
└──────────────────────┘    └──────────────────────┘    Hetzner Storage Box (opt)
                                                        weekly restic snapshot
```

### Subdomain plan

| Subdomain | Origin | CF proxy | Purpose |
|---|---|---|---|
| `ctf.chron0.tech` | Vercel (`fantasy-ctf-site`) | yes | Main SPA — landing + scoreboard + challenges + flag submission + writeups + about |
| `api.ctf.chron0.tech` | Hetzner → Traefik → CTFd | **no** | CTFd headless API; cookie + auth flow needs origin headers preserved |
| `<challenge>.ctf.chron0.tech` | Hetzner → Traefik → container | **no** | Per-challenge service (oracle, lich, arcane, prophecy, llm-*) — CF free tier doesn't proxy raw TCP |
| `status.ctf.chron0.tech` | Hetzner → Traefik | yes | Uptime Kuma (basic-auth) |
| `scoreboard.chron0.tech` | (deferred) | — | See §4 |

### Why two-path frontend (proxy + direct)

The existing Vercel proxy is **deliberately read-only** — `api/[...path].ts` rejects non-GET. It uses a server-side admin token to elevate reads (e.g., fetch user details with sensitive fields stripped) without exposing the token to clients. Don't extend it for player POSTs — that breaks the security model.

For authenticated calls (flag submit, hint unlock, `/users/me/solves`), the SPA bypasses the proxy entirely:

1. User logs in via OAuth → CTFd returns a session.
2. SPA calls `POST https://api.ctf.chron0.tech/api/v1/tokens` (with `credentials: 'include'`) to mint a personal bearer token.
3. SPA stores the bearer in `sessionStorage` (cleared on tab close).
4. All authenticated calls go directly to `api.ctf.chron0.tech` with `Authorization: Bearer <token>`.

This keeps the proxy's surface area tiny, leverages the same eTLD+1 (`chron0.tech`) so cookies cooperate, and matches CTFd's intended headless-API pattern.

CTFd CORS env (set in `infra/.env`):
```
CORS_ORIGIN=https://ctf.chron0.tech,https://localhost:5173
CORS_ALLOW_CREDENTIALS=true
SESSION_COOKIE_SAMESITE=Lax
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_DOMAIN=.chron0.tech
```

---

## 3 · Site repo (`ctfd-live-scoreboard`) — concrete migration

The existing `J:\projects\personal-projects\ctfd-live-scoreboard\` repo becomes the SPA. Stack already installed: Bun 1.x, Vite 7, React 19.2, TypeScript 5.9, Tailwind v4 (`@tailwindcss/vite`), shadcn, radix-ui, react-router-dom 7, framer-motion + motion, GSAP, tsparticles, OGL, lucide-react, recharts. **No new dependencies required** for the migration.

### Repo-level changes

| File | Change |
|---|---|
| `package.json` | `name: "app"` → `name: "chron0-ctf-scoreboard"`. Bump version to `1.0.0`. |
| `README.md` | Rewrite to reflect new scope (full SPA, not just scoreboard). |
| GitHub repo name | **Stays `ctfd-live-scoreboard`** — no rename, no broken URLs, no Vercel project disruption. |
| Vercel project name | **Stays as-is** — same project, just adds the new `ctf.chron0.tech` custom domain. |
| Vercel domains | Add `ctf.chron0.tech` (production primary). Add `scoreboard.chron0.tech` configured to 301-redirect to `ctf.chron0.tech/scoreboard`. Keep `scoreboard.issessions.ca` until cutover, then 301 to same. |
| `.env.example` | Add `CTFD_BASE_URL=https://api.ctf.chron0.tech`. Keep `CTFD_API_TOKEN`. |

### `api/[...path].ts` (proxy) changes

Three small edits, all preserve the existing hardening:

```ts
// Line 1 — make CTFd base URL configurable
const CTFD_BASE_URL = process.env.CTFD_BASE_URL ?? "https://api.ctf.chron0.tech";

// Lines 7-12 — ALLOWED_HOSTS (Vercel deployment URLs unchanged because repo name is unchanged)
const ALLOWED_HOSTS: (string | RegExp)[] = [
  "ctf.chron0.tech",                                    // NEW — production primary
  "scoreboard.chron0.tech",                             // NEW — redirect target
  "iss-ctfd-live-scoreboard.vercel.app",                // existing — keep until cutover complete
  /^iss-ctfd-live-scoreboard-.*\.vercel\.app$/,         // existing — Vercel branch previews
  "scoreboard.issessions.ca",                           // existing — drop after redirect verified
  "localhost:8000",
  "localhost",
];

// Lines 15-20 — ALLOWED_ORIGINS
const ALLOWED_ORIGINS: (string | RegExp)[] = [
  "https://ctf.chron0.tech",                            // NEW
  "https://scoreboard.chron0.tech",                     // NEW
  "https://iss-ctfd-live-scoreboard.vercel.app",        // existing
  /^https:\/\/iss-ctfd-live-scoreboard-.*\.vercel\.app$/,
  "https://scoreboard.issessions.ca",                   // existing — drop after cutover
  "http://localhost:8000",
  "http://localhost:5173",                              // NEW — Vite default
];
```

**`ALLOWED_PATHS` stays unchanged** — proxy remains read-only.

### `App.tsx` — new routes

```tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import FantasyCtfPage from "@/pages/FantasyCtfPage";        // existing — becomes /scoreboard
import ChallengesPage from "@/pages/ChallengesPage";
import ChallengeDetailPage from "@/pages/ChallengeDetailPage";
import SolutionPage from "@/pages/SolutionPage";
import LoginCallbackPage from "@/pages/LoginCallbackPage";
import AboutPage from "@/pages/AboutPage";
import { ThemeContext, FANTASY_THEME } from "@/contexts/ThemeContext";

export default function App() {
  return (
    <ThemeContext.Provider value={FANTASY_THEME}>
      <BrowserRouter>
        <Routes>
          <Route path="/"                     element={<LandingPage />} />
          <Route path="/scoreboard"           element={<FantasyCtfPage />} />
          <Route path="/challenges"           element={<ChallengesPage />} />
          <Route path="/challenges/:slug"     element={<ChallengeDetailPage />} />
          <Route path="/solutions/:slug"      element={<SolutionPage />} />
          <Route path="/login/callback"       element={<LoginCallbackPage />} />
          <Route path="/about"                element={<AboutPage />} />
          <Route path="*"                     element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeContext.Provider>
  );
}
```

`SkillsSheridanPage` archived — moved out of the `Routes` block. Keep the file in `src/pages/_archive/SkillsSheridanPage.tsx` (or delete and rely on git history) so multi-CTF capability can be revived later without re-implementing.

### New components / pages

| File | Purpose |
|---|---|
| `pages/LandingPage.tsx` | Tavern hero, lore intro, "Enter the Quest" CTA → `/login` (or `/challenges` if logged in). Reuses `TavernBackground`, `ClickSpark`, `Header`. |
| `pages/ChallengesPage.tsx` | Challenge browser, grouped by category, status badges (solved / unsolved / locked). Reuses `ChallengesView`. Hits `/api/v1/challenges` via Vercel proxy. |
| `pages/ChallengeDetailPage.tsx` | Per-challenge page: lore, files, hints (paid via API direct), `FlagSubmissionForm`. For LLM challenges: `BYOKeyForm` + `LLMDemoAnimation`. |
| `pages/SolutionPage.tsx` | Calls `/api/v1/users/me/solves` direct (not proxy), gates writeup render on `slug` being in solves. 403 page if not solved. |
| `pages/LoginCallbackPage.tsx` | OAuth callback handler — receives session, mints bearer via `/api/v1/tokens`, stores in `sessionStorage`, redirects. |
| `pages/AboutPage.tsx` | Portfolio context — Jon Marien, GitHub/LinkedIn, technical writeup of the architecture, ISSessions footer credit. |
| `components/forms/FlagSubmissionForm.tsx` | Direct POST to `api.ctf.chron0.tech/api/v1/challenges/attempt` with bearer. Handle correct/wrong/already-solved/rate-limited. |
| `components/forms/BYOKeyForm.tsx` | Provider dropdown (OpenAI / Anthropic / Gemini / OpenRouter), API key input (sessionStorage only), model selector. |
| `components/llm/LLMDemoAnimation.tsx` | Framer-motion typewriter replay. Per-challenge transcript in `data/llm-demos.ts`. |
| `components/ui/AuthGate.tsx` | Wrapper component — renders children only if user has bearer token; redirects to `/login` otherwise. |
| `hooks/useAuth.ts` | OAuth flow, bearer token management, `useUser()` hook. |
| `hooks/useSolves.ts` | Calls `/users/me/solves` direct; powers solution page gating. |
| `hooks/useSubmitFlag.ts` | Mutation hook wrapping the direct POST. |
| `lib/ctfdClient.ts` | Centralised fetch helpers: `proxyGet()` (uses `/api/*`), `directGet()`, `directPost()` (use `api.ctf.chron0.tech` with bearer). |
| `data/llm-demos.ts` | Hardcoded successful prompt + response transcripts for each LLM challenge. |

Estimated new code: **~1500–2500 LOC** across the new pages, components, and hooks. Existing scoreboard code (~3000 LOC) stays. Total post-migration: ~4500–5500 LOC of TS/TSX.

---

## 4 · Scoreboard URL strategy — locked

Single canonical URL: **`ctf.chron0.tech/scoreboard`**. Two legacy URLs both 301-redirect to it:

- `scoreboard.chron0.tech` → 301 → `ctf.chron0.tech/scoreboard`
- `scoreboard.issessions.ca` → 301 → `ctf.chron0.tech/scoreboard`

Implementation in `vercel.json`:

```json
{
  "redirects": [
    {
      "source": "/(.*)",
      "has": [{ "type": "host", "value": "scoreboard.chron0.tech" }],
      "destination": "https://ctf.chron0.tech/scoreboard",
      "permanent": true
    },
    {
      "source": "/(.*)",
      "has": [{ "type": "host", "value": "scoreboard.issessions.ca" }],
      "destination": "https://ctf.chron0.tech/scoreboard",
      "permanent": true
    }
  ]
}
```

Vercel project owns all three custom domains; only `ctf.chron0.tech` actually serves content, the other two redirect.

**Why redirect both rather than keeping one as an alias:** single canonical URL is better for SEO, link sharing, and portfolio framing. If you later want a kiosk-mode scoreboard for projection at events, add `?embed=1` to `/scoreboard` and hide the chrome — same effect, no extra domain to maintain.

---

## 5 · Monorepo (`fantasy_ctf_challs`) — layout

```
fantasy_ctf_challs/
├── crypto/                    # ─┐
├── prog/                      #  │
├── llm/                       #  ├── existing — challenges (untouched structure;
├── osint/                     #  │   composes get image: ghcr.io/... swap in Phase 4)
├── rev/                       #  │
├── misc/                      # ─┘
├── infra/                     # NEW — runs on the Hetzner box
│   ├── docker-compose.prod.yml
│   ├── traefik/
│   │   ├── traefik.yml
│   │   └── dynamic/
│   ├── ctfd/
│   │   ├── config/
│   │   └── plugins/           # CTFd-Whale (glzjin fork), OAuth plugin
│   ├── litellm/
│   │   └── config.yml         # provider routing rules
│   ├── observability/
│   │   └── uptime-kuma/
│   ├── bootstrap.sh           # post-cloud-init: Docker, ctf user, repo clone
│   ├── deploy.sh              # docker compose pull && up -d
│   ├── scripts/
│   │   └── sync-fallback.py   # ~100-line REST-API fallback if ctfcli breaks
│   └── README.md
├── .ctf/
│   └── config                 # existing — flip to https://api.ctf.chron0.tech post-migration
├── .github/
│   └── workflows/             # NEW
│       ├── sync-ctfd.yml      # ctfcli sync + GHCR push + VPS deploy
│       ├── lint.yml           # gitleaks, yamllint, hadolint, markdownlint
│       └── test-solves.yml    # run every solution/solve.{py,go} headlessly
├── docs/                      # NEW — runbooks
│   ├── runbook-deploy.md
│   ├── runbook-restore.md
│   ├── runbook-incident.md
│   └── runbook-event-day.md
├── HOSTING_PLAN.md            # original (Mar 2026)
├── HOSTING_PLAN_V2.md         # second draft (Hetzner pivot)
├── HOSTING_PLAN_V3.md         # this doc — site-repo pivot
├── README.md                  # existing — update to reflect new architecture
├── LORE.md                    # existing
├── FULL_PLAN.txt              # existing
└── .gitignore                 # extend: infra/.env*, infra/secrets/, node_modules/, dist/
```

**Note: no `frontend/` directory.** That was in v2; dropped here in favour of the sibling site repo.

---

## 6 · LLM challenge architecture (unchanged from v2)

**LiteLLM** runs as a sidecar in `infra/docker-compose.prod.yml`, exposing `http://litellm:4000/v1/chat/completions` (OpenAI-compatible). Existing `llm/shared/` Python code points at this endpoint. Players supply `provider + model + key` from the SPA; those flow as headers to LiteLLM, which routes to the correct upstream (OpenAI, Anthropic, Gemini, OpenRouter).

**Security model — flag stays server-side.** Each LLM challenge container has the flag in `os.environ['FLAG']`, injected into the system prompt at request time. The player's key powers the LLM call but never sees the flag directly — only the LLM does, and prompt-injecting the LLM into leaking it is the puzzle. Player keys are **never logged, never persisted, never echoed in errors**.

**"Demo" via Framer Motion animation.** Each LLM challenge page has a "▶ See an example solve" button. Clicking it plays a hardcoded transcript:

1. Typewriter populates the input field with a successful prompt.
2. Brief pause.
3. Typewriter spits out the LLM's response, with the flag span highlighted via animated colour.
4. "▶ Replay" + "Try your own (BYO key)" CTAs appear.

Per-challenge transcripts in `data/llm-demos.ts`. Zero API calls, zero cost, zero abuse vector.

---

## 7 · Phased roadmap (revised — server is up)

Total estimated effort: **~40–60 hours** (down from v2's ~45–75 because Phase 1 is mostly done and the site repo gives a head start).

### ✅ Phase 1 — Foundations (done)

Server is provisioned in Ashburn. Cloud-init has run. SSH works.

Remaining bits to confirm:
1. ✅ Hetzner CPX21 in Ashburn, Ubuntu 24.04
2. ⬜ Hetzner Cloud Firewall created + attached: 22 (your home IP only), 80, 443
3. ⬜ Cloudflare DNS records: A `ctf` + wildcard `*.ctf` → Hetzner IP, A `api.ctf` → Hetzner IP
4. ⬜ Cloudflare DNS API token (Zone-scoped, `Zone:DNS:Edit` on `chron0.tech` only) — for Traefik DNS-01
5. ⬜ Cloudflare proxy: ON for `ctf` (and `scoreboard` if Option B); OFF for `api.ctf` and wildcard `*.ctf`
6. ⬜ GitHub Environments: `staging` and `production`, with `production` requiring you as reviewer
7. ⬜ Vercel: confirm scoreboard project access; you'll add the new domain in Phase 3

### Phase 2 — VPS bring-up (≈ 6–10 h)

1. SSH in, run `infra/bootstrap.sh`: install Docker + compose plugin, create `ctf` non-root user, clone the repo to `/opt/fantasy_ctf_challs`, set up `infra/secrets/` directory.
2. Bring up `infra/docker-compose.prod.yml`: Traefik, CTFd, Postgres 16, Redis 7, docker-socket-proxy, LiteLLM, Uptime Kuma. Empty config first.
3. Verify Traefik successfully requests the wildcard cert via Cloudflare DNS-01. **First milestone:** `https://api.ctf.chron0.tech` shows the CTFd setup wizard with a real Let's Encrypt cert.
4. Walk through CTFd setup. Set CORS env vars (`CORS_ORIGIN=https://ctf.chron0.tech`), session cookie domain to `.chron0.tech`, session cookie secure on.
5. Install **CTFd-Whale (glzjin fork)** plugin — leave disabled by default; enable per-challenge in Phase 4.
6. Install **CTFd OAuth plugin** — configure GitHub OAuth (create the GitHub OAuth App at `github.com/settings/applications/new`, callback URL `https://api.ctf.chron0.tech/redirect`). Test signup/login.
7. Take the first Hetzner snapshot.

### Phase 3 — Site repo migration (≈ 12–18 h)

This replaces v2's "Phase 3 frontend migration."

**3a. Site repo prep + Vercel domain config (≈ 1–2 h):**
1. **Do not rename the GitHub repo** — keep `ctfd-live-scoreboard`. Update `package.json` `name` to `chron0-ctf-scoreboard`, bump version to `1.0.0`.
2. Edit `api/[...path].ts`: env-var-ize `CTFD_BASE_URL`, append new entries to `ALLOWED_HOSTS` + `ALLOWED_ORIGINS` (keep existing ISSessions/Vercel-default entries during transition).
3. Edit `vercel.json` to add the redirect block for `scoreboard.chron0.tech` and `scoreboard.issessions.ca` → `ctf.chron0.tech/scoreboard`.
4. In Vercel project settings: add custom domain `ctf.chron0.tech` (CNAME `cname.vercel-dns.com`), keep `iss-ctfd-live-scoreboard.vercel.app` as the auto-generated default, attach `scoreboard.chron0.tech` (it'll 301 via vercel.json), keep `scoreboard.issessions.ca` until cutover then drop or 301.
5. Set Vercel env (Production scope): `CTFD_BASE_URL=https://api.ctf.chron0.tech`, `CTFD_API_TOKEN=<new admin token from new CTFd instance>`.
6. Smoke-test after deploy: `curl -I https://scoreboard.chron0.tech` returns 308/301 to `ctf.chron0.tech/scoreboard`. Same for `scoreboard.issessions.ca`. `https://ctf.chron0.tech/scoreboard` loads.

**3b. New routes + auth (≈ 4–6 h):**
1. Update `App.tsx` with the new routes; archive `SkillsSheridanPage` (move to `_archive/` or remove).
2. Build `LandingPage` — Tavern hero, "Enter the Quest" CTA, lore intro reusing existing background components.
3. Build `LoginCallbackPage` + `useAuth` hook + `lib/ctfdClient.ts` — OAuth flow, bearer minting, sessionStorage management.
4. Build `AuthGate` wrapper. Smoke-test login flow.

**3c. Challenge browsing + flag submission (≈ 5–8 h):**
1. Build `ChallengesPage` — wraps existing `ChallengesView`, adds status badges via `useSolves`.
2. Build `ChallengeDetailPage` — challenge metadata, file links, hints, `FlagSubmissionForm`.
3. Build `FlagSubmissionForm` — direct POST to `api.ctf.chron0.tech/api/v1/challenges/attempt` with bearer.
4. Smoke-test: submit a wrong flag, then a correct one; confirm scoreboard updates.

**3d. LLM challenge UX (≈ 3–4 h):**
1. Build `BYOKeyForm` — provider dropdown, key input, model selector. sessionStorage only.
2. Build `LLMDemoAnimation` — framer-motion typewriter replay. Hardcode 5 transcripts in `data/llm-demos.ts` (one per LLM challenge).
3. Wire challenge detail page to render BYO + animation when category is `llm`.

**3e. Solutions + about (≈ 2–3 h):**
1. Build `SolutionPage` — `useSolves` gate, render markdown writeup if solved, 403 page if not.
2. Migrate the `solution/SOLUTION.md` files from the monorepo into the site repo's `data/solutions/<slug>.md` (or fetch them from a `/solutions.json` static file generated at build time from the monorepo).
3. Build `AboutPage` — your portfolio context, links, ISSessions footer credit.

### Phase 4 — Challenge migration (≈ 6–10 h)

1. Update `.ctf/config` to point at `https://api.ctf.chron0.tech` and the new admin token.
2. **Rotate the old `issessionsctf.ctfd.io` admin token** — it's been shared in prior sessions.
3. `ctf challenge install` for each of the 22 challenges.
4. For each Dockerised challenge: edit `docker-compose.yml` to swap `build:` → `image: ghcr.io/jondmarien/fantasy-ctf-<name>:<sha>` and add Traefik labels for `<chal>.ctf.chron0.tech` routing.
5. For LLM challenges: rewire `llm/shared/` to call LiteLLM at `http://litellm:4000/v1` instead of Gemini directly.
6. Smoke-test each network challenge end-to-end against `<chal>.ctf.chron0.tech`.
7. Run a friend through 3 challenges as a real player.

### Phase 5 — CI/CD (≈ 5–8 h)

1. `.github/workflows/sync-ctfd.yml` — `dorny/paths-filter` → matrix build → GHCR push → `ctf challenge sync` → SSH deploy. See §8.
2. Two Environments wired: `staging` auto on push to `main`; `production` via `workflow_dispatch` with required reviewer.
3. `.github/workflows/lint.yml` — gitleaks, yamllint, hadolint, markdownlint.
4. `.github/workflows/test-solves.yml` — run every `solution/solve.py` headlessly, assert `FantasyCTF{...}` recovered. Catches drift between challenge code and intended solve.
5. Pin `ctfcli==0.1.7`. `infra/scripts/sync-fallback.py` (~100 lines) for if ctfcli breaks mid-event.

### Phase 6 — Hardening + observability + backups (≈ 4–8 h)

1. Per-container hardening on every challenge compose: `read_only: true`, `cap_drop: [ALL]`, `no-new-privileges`, `pids_limit`, `mem_limit`, `cpus`, `tmpfs` for `/tmp`.
2. Per-challenge bridge networks with `internal: true`. LLM containers on a separate bridge — egress restricted to `litellm` sidecar via `tinyproxy` allowlist if you ever expand beyond LiteLLM-mediated calls.
3. Block droplet metadata from challenge nets: `iptables -I DOCKER-USER -d 169.254.169.254 -j DROP`, persist via `iptables-persistent`.
4. Configure Uptime Kuma: HTTP probes for `ctf.`, `api.ctf.`, `scoreboard.` (if kept); TCP probes for socket challenges. Discord webhook.
5. (Optional) Hetzner Storage Box (~$3/mo, 1 TB) + restic weekly snapshot. Pair with daily Hetzner snapshots already enabled.
6. **Restore drill on a throwaway Hetzner instance.** Single most-skipped step.
7. CTFd-Whale settings: `WHALE_DOCKER_MAX_CONTAINERS=15`, per-container `mem_limit: 256m`. Whale only on stateful challenges (Lich oracle, Arcane, Prophecy, LLMs).

### Phase 7 — Soft launch + portfolio polish (≈ 4–6 h)

1. Beta with 5 trusted friends. 48 hours of real submissions to flush bugs.
2. Triage: scoring, OAuth UX, copy errors, mobile responsiveness.
3. Polish `/about` — explain the BYO-key architecture, the framer-motion demo idea, the security model. Recruiters skim this page.
4. Open `state: visible` on all 22 challenges. Push first public announcement.

---

## 8 · CI/CD pipeline

Two workflows, two repos.

### `fantasy_ctf_challs` — `.github/workflows/sync-ctfd.yml`

```yaml
name: sync-ctfd
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment: { type: choice, options: [staging, production] }

jobs:
  detect-changes:
    outputs: { matrix: ${{ steps.filter.outputs.changes }} }
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            crypto-scribe:  ['crypto/The-Scribes-Encoded-Scroll-Beginner/**']
            crypto-goblin:  ['crypto/The-Goblin-Messengers-Cipher-Easy/**']
            # ... one filter per challenge

  build-images:
    needs: detect-changes
    strategy: { matrix: { challenge: ${{ fromJSON(needs.detect-changes.outputs.matrix) }} } }
    if: hashFiles(format('{0}/Dockerfile', matrix.challenge)) != ''
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.challenge }}
          push: true
          tags: ghcr.io/jondmarien/fantasy-ctf-${{ matrix.challenge }}:${{ github.sha }}

  sync-metadata:
    needs: [detect-changes, build-images]
    environment: ${{ inputs.environment || 'staging' }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install ctfcli==0.1.7
      - run: |
          for c in ${{ join(fromJSON(needs.detect-changes.outputs.matrix), ' ') }}; do
            ctf challenge sync "$c"
          done
        env:
          CTF_URL:   ${{ secrets.CTFD_URL }}
          CTF_TOKEN: ${{ secrets.CTFD_TOKEN }}

  deploy-vps:
    needs: sync-metadata
    environment: ${{ inputs.environment || 'staging' }}
    steps:
      - uses: appleboy/ssh-action@v1
        with:
          host:     ${{ secrets.VPS_HOST }}
          username: ctf
          key:      ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/fantasy_ctf_challs && git pull
            docker compose pull && docker compose up -d --remove-orphans
```

### `fantasy-ctf-site` — handled by Vercel's git integration

Vercel auto-deploys on push. No GitHub Actions needed for the SPA itself. Optional `lint.yml` for type-check + ESLint on PRs:

```yaml
name: lint-site
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2          # <-- Bun, not Node
        with: { bun-version: 1.x }
      - run: bun install
      - run: bun run lint
      - run: bunx tsc -b --noEmit
```

Two non-obvious principles still hold:

1. **Metadata sync ≠ image deploy.** `ctfcli` updates challenge text/config in the CTFd DB. Container deploy is a separate SSH step. `ctf challenge deploy` is for managed/cloud CTFd, not a self-hosted VPS.
2. **`production` requires manual approval.** GitHub Environment with you as reviewer. Catches the 2am whoops.

---

## 9 · Security & isolation (unchanged from v2)

### Per-challenge container baseline

```yaml
read_only: true
user: "1001:1001"
cap_drop: [ALL]
security_opt:
  - no-new-privileges:true
  - apparmor=docker-default
pids_limit: 128
mem_limit: 256m
cpus: '0.5'
ulimits: { core: 0, nofile: 1024, nproc: 64, fsize: 1048576 }
tmpfs: ["/tmp:size=32m,mode=1777"]
networks: [chal_<name>]
```

### Network isolation

- One bridge per challenge, `internal: true`.
- LLM containers on a separate bridge — egress only to the `litellm` sidecar.
- Block droplet metadata: `iptables -I DOCKER-USER -d 169.254.169.254 -j DROP`.

### Whale

`WHALE_DOCKER_MAX_CONTAINERS=15`, per-container `mem_limit: 256m`. Apply Whale only to stateful challenges. Front the Docker socket with `tecnativa/docker-socket-proxy` (read + container ops only).

---

## 10 · Secrets

| Secret | Lives in | Why |
|---|---|---|
| CTFd `SECRET_KEY` | `infra/.env` on VPS, mode 0600 | Long-lived |
| CTFd admin/CI token | GitHub Environment secret `CTFD_TOKEN` | CI-only, rotate after each event |
| Postgres password | `infra/.env` on VPS | Stays on box |
| Cloudflare DNS API token | `infra/.env` on VPS, Zone:DNS:Edit | Single-purpose |
| GHCR | `GITHUB_TOKEN` | Same-repo push |
| VPS deploy SSH key | GitHub Environment secret `VPS_SSH_KEY` | `ctf` user, sudo only deploy script |
| Vercel public envs (`VITE_*`) | Vercel project envs | Browser-safe values only |
| Vercel server-side envs (`CTFD_API_TOKEN`, `CTFD_BASE_URL`) | Vercel project envs (server scope) | Used by `api/[...path].ts`; never exposed to client |
| OAuth client secrets (GitHub) | `infra/.env` on VPS, consumed by CTFd | Backend-only |
| Per-challenge flags | `infra/.env` on VPS, injected via compose `env_file` | **Never** in `ctfd_meta.json` for prod |
| Player API keys (BYO LLM) | **Never stored** | Header-only, in-flight |

`gitleaks` in CI catches accidents. **Action: rotate the `issessionsctf.ctfd.io` admin token in `.ctf/config`** during Phase 4.

---

## 11 · Backups + observability

**Backups:**
- **Hetzner Backups:** daily disk snapshot, 7-day retention, ~$1.50/mo.
- **Optional Hetzner Storage Box (1 TB, ~$3/mo):** weekly `restic` snapshot of Postgres + CTFd uploads + `infra/.env`. 8-week retention. Restore drill once before launch, then yearly.
- **Repo is the source of truth** for challenge code and metadata. Losing the runtime DB just means players re-register.

**Observability:**
- **Uptime Kuma** — HTTP probes for public hosts, TCP for socket challenges. Discord webhook.
- **Hetzner console graphs** — free CPU/RAM/disk graphs.
- **Logs:** `docker logs` + log rotation in `/etc/docker/daemon.json` (`"max-size": "10m", "max-file": "3"`). Skip Loki/Grafana — saves ~700 MB RAM.

---

## 12 · Cost estimate

| Item | Monthly | Notes |
|---|---|---|
| Hetzner CPX21 (Ashburn) | $7.55 | 3 vCPU AMD, 4 GB, 80 GB |
| Public IPv4 | $0.72 | IPv6 free |
| Hetzner Backups (20%) | ~$1.50 | Daily snapshot |
| Hetzner Storage Box (1 TB, optional) | $3 | Off-site weekly |
| Vercel Hobby | $0 | One project (`fantasy-ctf-site`) under free tier |
| Cloudflare DNS + free proxy | $0 | |
| GitHub Actions / GHCR | $0 | Public repo |
| LLM provider keys | $0 | BYO model |
| Domain `chron0.tech` | already owned | |
| **Total** | **~$10–13/mo** | ~$120–155/year |

---

## 13 · Risk register

| ID | Risk | L | I | Mitigation |
|---|---|---|---|---|
| R1 | Whale-spawned containers OOM the box | M | M | `WHALE_DOCKER_MAX_CONTAINERS=15`, `mem_limit: 256m`, Whale only on stateful |
| R2 | Public repo leaks live flag | M | M | gitleaks pre-commit + CI; flags via `infra/.env`; `state: hidden` until soft-launch |
| R3 | Container escape from challenge | L | H | `cap_drop: [ALL]`, `read_only`, no-new-privileges, AppArmor; metadata blocked |
| R4 | DDoS on the Hetzner box | L | M | Cloudflare proxy on SPA; Traefik rate-limit on `api.`; Hetzner DDoS protection (free) |
| R5 | Backup that doesn't restore | M | H | Mandatory restore drill in Phase 6 |
| R6 | CSRF / cookie misconfig leaks session | L | H | Same eTLD+1; bearer-token auth for SPA POSTs; Secure/HttpOnly/SameSite=Lax |
| R7 | `ctfcli` 0.1.x breaks during deploy | L | H | Pin `==0.1.7`; staging canary; hand-rolled REST fallback in `infra/scripts/` |
| R8 | CTFd plugin breaks on CTFd upgrade | M | M | Pin CTFd `image:` tag; staging upgrade; never upgrade in event windows |
| R9 | OAuth provider revokes app | L | M | Document failover to email-signup; have GitHub + Google both registered, only enable one |
| R10 | Player BYO key leaked via challenge container logs | L | H | Audit `llm/shared/` to confirm keys never logged; pen-test before launch |
| R11 | Vercel proxy `ALLOWED_HOSTS` outdated post-cutover | M | L | Update list during 3a; smoke-test after deploy; old hosts remain in list during transition |
| R12 | SkillsSheridan archive forgotten in routes | L | L | Phase 3b explicitly removes the route; lint passes will catch dead imports |
| R13 | Bun vs Node mismatch in CI | L | L | `oven-sh/setup-bun@v2` in `lint.yml`; document in `docs/runbook-deploy.md` |
| R14 | Redirect loop on legacy domain misconfig | L | M | Use Vercel `redirects` block with `has.host` predicate (not catch-all); test each legacy URL with curl `-L` after deploy |
| R15 | Solution writeups embedded in site repo go stale vs monorepo | M | L | Build-time fetch of `solution/SOLUTION.md` from monorepo via raw GitHub URL or git-submodule, NOT manual copy |

---

## 14 · Open decisions — all closed

| Question | Resolution |
|---|---|
| Registration model | OAuth via CTFd plugin (default GitHub) |
| Event windows vs always-on | Always-on portfolio site |
| Sibling scoreboard repo fate | **Repo name kept as `ctfd-live-scoreboard`** (no rename); `package.json` renamed to `chron0-ctf-scoreboard`; extended into full SPA; same Vercel project, new primary domain `ctf.chron0.tech` |
| Scoreboard URL strategy | `ctf.chron0.tech/scoreboard` is canonical; `scoreboard.chron0.tech` and `scoreboard.issessions.ca` both 301 to it (Vercel redirects) |
| Branding | ISSessions footer credit only; main framing is Jon's personal portfolio |
| Solution writeups | Session-bound at `/solutions/:slug` |
| Demo mode for LLM challs | Framer-motion animation; no live API calls |
| LLM providers | LiteLLM gateway: OpenAI + Anthropic + Gemini + OpenRouter |
| `ctf.chron0.tech` scope | Full custom UI with flag submission baked in |
| Sponsorship | None |
| Multi-CTF support | **Skills Sheridan archived; Fantasy is the only active theme**; multi-CTF code remains for future revival |
| Scoreboard URL | **Option A** — `scoreboard.issessions.ca` redirects to `ctf.chron0.tech/scoreboard` (post-cutover) |

---

## 15 · Verification findings (carried forward)

1. **You're on `feat/hosting`.** Correct branch.
2. **`.ctf/config` token is local-only** (`.ctf/` is gitignored) but has been shared in prior sessions — **rotate during Phase 4**.
3. **`ctfd-live-scoreboard` repo is much further along than v2 assumed.** It has Bun + Vite 7 + React 19.2, all modern deps, a hardened Vercel proxy (`api/[...path].ts`), and a working Fantasy theme. Migration is mostly additive, not from-scratch. Repo name is unchanged — only `package.json` `name` and the Vercel custom domains move.
4. **The proxy is read-only by design** (line 178: `if (request.method !== "GET") return 405`). Don't extend it for player POSTs — use direct calls to `api.ctf.chron0.tech`.
5. **`SkillsSheridanPage` exists** and is currently the default route. Archive it during Phase 3b.
6. **10 existing per-challenge `docker-compose.yml` files** in the monorepo — Phase 4 means *editing* these, not writing new ones.
7. **`.gitignore` extension needed in monorepo:** add `infra/.env*`, `infra/secrets/`, `node_modules/`, `dist/`. The site repo's gitignore already handles its own.
8. **Bun, not Node, on the Vercel side.** CI workflows that touch the site repo must use `oven-sh/setup-bun@v2`.

---

## 16 · Next steps (you are here)

Server's up, you can SSH in. Next concrete actions:

1. **Configure Hetzner Cloud Firewall** — create + attach with: SSH from your home IP only, 80 + 443 open. Skip per-challenge ports (Traefik handles routing on 443 with TCP routers + SNI).
2. **Cloudflare DNS records** — A `ctf.chron0.tech` → Hetzner IP, A `api.ctf.chron0.tech` → Hetzner IP, A wildcard `*.ctf.chron0.tech` → Hetzner IP. Proxy ON for `ctf`; OFF for `api.ctf` and the wildcard.
3. **Cloudflare DNS API token** — Zone-scoped (`Zone:DNS:Edit` on `chron0.tech` only). Save in your password manager; you'll paste this into `infra/.env` for Traefik.
4. **GitHub Environments** — create `staging` and `production`; add yourself as required reviewer on `production`.
5. **Start Phase 2** — once steps 1–4 are done, you can run `infra/bootstrap.sh` on the VPS and bring up the docker-compose stack.

The first real milestone: `https://api.ctf.chron0.tech` showing the CTFd setup wizard with a real Let's Encrypt cert. That's when the foundation is solid and you can start migrating challenges in.

I'd suggest tackling Phases 2–7 as 6 short-lived branches off `main` in the monorepo, plus 1–2 PRs in the site repo for the migration. Each PR self-reviewed, each merge keeps `main` deployable.

---

## Appendix A — Sources

Research backing platform survey, architecture, sizing, and CI/CD recommendations is in v1 of this doc; key links:

- CTFd: [releases](https://github.com/CTFd/CTFd/releases) · [REST API](https://docs.ctfd.io/tutorials/api/using-ctfd-api/) · [ctfcli](https://docs.ctfd.io/docs/management/ctfcli/overview/) · [dynamic scoring](https://docs.ctfd.io/docs/custom-challenges/dynamic-value/)
- Plugins: [glzjin/CTFd-Whale](https://github.com/glzjin/CTFd-Whale) · [CTFd OAuth plugin](https://github.com/tamuctf/CTFd-oauth)
- Frontend: [Vite](https://vitejs.dev) · [shadcn/ui](https://ui.shadcn.com) · [TanStack Query](https://tanstack.com/query) · [Framer Motion](https://www.framer.com/motion/) · [Tailwind v4](https://tailwindcss.com/blog/tailwindcss-v4) · [Bun](https://bun.sh)
- LiteLLM: [docs](https://docs.litellm.ai) · [GitHub](https://github.com/BerriAI/litellm)
- Hetzner: [Cloud pricing](https://www.hetzner.com/cloud) · [Cloud Firewalls](https://docs.hetzner.com/cloud/firewalls/overview) · [Storage Box](https://www.hetzner.com/storage/storage-box)
- Reverse proxy: [Traefik wildcard certs](https://blog.stonegarden.dev/articles/2023/12/traefik-wildcard-certificates/) · [Production Traefik](https://botmonster.com/posts/deploy-docker-compose-traefik-production/)
- Container hardening: [Container hardening 2026](https://hostperl.com/blog/production-container-security-best-practices-hardening-strategies-2026)

---

## Appendix B — Cloud-init (if you ever rebuild)

```yaml
#cloud-config
package_update: true
package_upgrade: true
packages: [ufw, fail2ban, ca-certificates, curl, gnupg]
runcmd:
  - ufw default deny incoming
  - ufw default allow outgoing
  - ufw allow 22/tcp
  - ufw allow 80/tcp
  - ufw allow 443/tcp
  - ufw --force enable
  - sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
  - sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
  - systemctl restart ssh
  - systemctl enable --now fail2ban
final_message: "Hardened bootstrap complete."
```

---

## Appendix C — Bootstrap script (Phase 2 starter)

`infra/bootstrap.sh` to be created during Phase 2. Sketch:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Run as root after first SSH.

# 1. Docker
curl -fsSL https://get.docker.com | sh

# 2. ctf user
useradd -m -s /bin/bash -G docker,sudo ctf
mkdir -p /home/ctf/.ssh
cp /root/.ssh/authorized_keys /home/ctf/.ssh/
chown -R ctf:ctf /home/ctf/.ssh
chmod 700 /home/ctf/.ssh
chmod 600 /home/ctf/.ssh/authorized_keys
echo "ctf ALL=(ALL) NOPASSWD: /opt/fantasy_ctf_challs/infra/deploy.sh" > /etc/sudoers.d/ctf-deploy

# 3. Repo
mkdir -p /opt
git clone https://github.com/jondmarien/fantasy_ctf_challs.git /opt/fantasy_ctf_challs
chown -R ctf:ctf /opt/fantasy_ctf_challs

# 4. Secrets dir
mkdir -p /opt/fantasy_ctf_challs/infra/secrets
chown ctf:ctf /opt/fantasy_ctf_challs/infra/secrets
chmod 700 /opt/fantasy_ctf_challs/infra/secrets

# 5. Docker log rotation
cat > /etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
EOF
systemctl restart docker

# 6. Block droplet metadata from challenge nets
iptables -I DOCKER-USER -d 169.254.169.254 -j DROP
apt-get install -y iptables-persistent
netfilter-persistent save

echo "Bootstrap complete. SSH back in as 'ctf'."
```

This is a sketch — refine in Phase 2 before running.
