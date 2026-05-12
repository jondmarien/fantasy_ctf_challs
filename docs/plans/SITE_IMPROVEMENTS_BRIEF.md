# Site improvements — combined brief

**Audience:** Cursor.
**Companion docs:** `HOSTING_PLAN_V3.md` (architecture), `CURSOR_BRIEF.md` (Phase G is already done), `AACHEN_SCORING_BRIEF.md` (parallel scoring work).
**Working dir:** `J:\projects\personal-projects\ctfd-live-scoreboard` (the site repo). Branch off `main` as `feat/site-improvements`.

## Context

Phase G shipped. The site is live but is using the bare minimum of CTFd's API surface. Eight improvements queued, in dependency + value order. **Custom CTFd theme is explicitly deferred** — Jon will revisit after these land.

## What's in scope

| # | Phase | Effort | Needs auth? | Why it matters |
|---|---|---|---|---|
| 1 | Description fix | 5 min | no | Detail pages are missing description because the SPA falls back to list-endpoint data when unauthenticated |
| 2 | Manual-token auth | ~2 h | — | Unblocks every authenticated feature below (OAuth is parked until later) |
| 3 | Hints UI + unlock flow | ~3 h | yes | Biggest current UX gap — hints exist in CTFd but the SPA doesn't surface them |
| 4 | Per-challenge solves list | ~1 h | no | Social proof — "X adventurers have completed this quest" with timestamps |
| 5 | "My profile" badge in header | ~1 h | yes | Player score/solve count visible on every page, drives engagement |
| 6 | Player profile pages | ~3 h | no (read) | Clicking another player on the scoreboard shows their solve history |
| 7 | Notifications bar | ~1 h | no | Site-wide announcements at the top of every page |
| 8 | Awards / first-blood UI | ~2 h | mixed | Cosmetic but portfolio-strong — badges on player profiles, "first blood" notice on challenges |

**Total: ~13 hours.** Can be 1 PR per phase (recommended for review), or batched into 2–3 PRs.

## Sequence

Strict order until phase 3. Phases 4–8 can be done in any order or parallel.

```
1. Description fix ──► 2. Manual-token auth ──► 3. Hints UI
                                                    │
                            ┌───────────────────────┼────────────────────────┐
                            ▼                       ▼                        ▼
                  4. Per-chal solves    5. "My profile" badge      6. Player profile pages
                                                    │
                                                    ▼
                                          7. Notifications bar
                                                    │
                                                    ▼
                                          8. Awards / first-blood
```

---

# Phase 1 — Description fix (5 min)

**File:** `src/pages/ChallengeDetailPage.tsx`

The detail page is using `useChallengeCache` (list endpoint data, no description) when unauthenticated. Switch to always calling the **detail** endpoint `/v1/challenges/<id>`.

## Edit

Find the `useEffect` block that loads detail (currently around line 65–75). Replace with:

```tsx
useEffect(() => {
  if (!challengeId) return;
  setError(null);
  setDetail(null);
  // Always hit the detail endpoint — list endpoint omits description, connection_info, etc.
  // Use proxyGet for unauthenticated (Vercel proxy already allowlists /v1/challenges/<id>),
  // directGet for authenticated so solved_by_me + locked fields are accurate.
  const fetchPromise = isAuthenticated
    ? directGet<{ success: boolean; data: ChallengeDetail }>(`/challenges/${challengeId}`)
    : proxyGet<{ success: boolean; data: ChallengeDetail }>(`/v1/challenges/${challengeId}`);
  fetchPromise
    .then((j) => setDetail(j.data))
    .catch((e) => setError(e instanceof Error ? e.message : String(e)));
}, [challengeId, isAuthenticated]);
```

Make sure `proxyGet` is imported alongside `directGet` at the top of the file:

```tsx
import { directGet, proxyGet } from "@/lib/ctfdClient";
```

## Verify

```bash
bun run build
bun run dev
# Navigate to /challenges/the-enchanted-parrot — description should render
```

## Commit

```bash
git add src/pages/ChallengeDetailPage.tsx
git commit -m "site: fetch full challenge detail (description, hints, etc) via /v1/challenges/<id>"
```

PR → merge → Vercel deploys.

---

# Phase 2 — Manual-token auth (~2 h)

**Goal:** player registers + generates a CTFd token on `api.ctf.chron0.tech`, pastes it into the SPA's `/login`, SPA stores in sessionStorage, all authenticated calls use it. No OAuth required.

## Prerequisites — confirm CTFd allows self-registration

Check `https://api.ctf.chron0.tech/admin/config` (admin login required). Look for **Registration** setting — must be **enabled**. If disabled, flag to Jon to flip in admin UI before this phase.

## Files to edit

### `src/pages/LoginPage.tsx` (new)

```tsx
import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import TavernBackground from "@/components/background/TavernBackground";
import { setBearerToken, directGet, clearBearerToken } from "@/lib/ctfdClient";

const CTFD_BASE = import.meta.env.VITE_CTFD_DIRECT_BASE ?? "https://api.ctf.chron0.tech";

export default function LoginPage() {
  const [token, setToken] = useState("");
  const [validating, setValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const next = params.get("next") ?? "/challenges";

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = token.trim();
    if (!trimmed) return;
    setValidating(true);
    setError(null);
    setBearerToken(trimmed);
    try {
      const me = await directGet<{ success: boolean; data: { name: string } }>("/users/me");
      if (!me.success) throw new Error("token rejected by CTFd");
      // Success — token is valid, sessionStorage already set, redirect.
      navigate(next, { replace: true });
    } catch (e) {
      clearBearerToken();
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <TavernBackground />
      <div className="relative z-30 max-w-xl mx-auto px-6 py-12">
        <Link to="/" className="text-amber-400/60 hover:text-amber-300 font-medievalsharp text-sm">← Gates</Link>

        <motion.h1
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 font-quintessential text-3xl text-amber-100 text-center"
        >
          🗝️ Forge your sigil
        </motion.h1>

        <article className="mt-6 font-medievalsharp text-amber-200/80 space-y-3">
          <p>
            The Quest Hall recognises you by a personal access token. Follow these steps in another tab:
          </p>
          <ol className="list-decimal list-inside space-y-2">
            <li>Open <a className="text-amber-400 underline" target="_blank" rel="noopener" href={`${CTFD_BASE}/register`}>the Guild Roster ({"register an account"})</a> if you don't have one. Username + email + password — your real identity is up to you.</li>
            <li>Open <a className="text-amber-400 underline" target="_blank" rel="noopener" href={`${CTFD_BASE}/settings#tokens`}>your settings &rarr; tokens</a>.</li>
            <li>Click "Generate" — give it any description and an expiration date (1 year is fine).</li>
            <li>Copy the long string starting with <code className="bg-stone-900 px-1 rounded">ctfd_</code></li>
            <li>Paste it below.</li>
          </ol>
          <p className="text-sm text-amber-500/70">
            Your token stays in this browser tab only. Cleared when you close the tab. Never logged, never persisted, never shared.
          </p>
        </article>

        <form onSubmit={onSubmit} className="mt-8 space-y-3">
          <label className="block">
            <span className="block font-medievalsharp text-xs text-amber-400/70 uppercase tracking-wider mb-1">
              Token
            </span>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="ctfd_..."
              className="w-full px-4 py-2 rounded-lg border-2 border-amber-700/40 bg-stone-950/70 backdrop-blur-md font-mono text-sm text-amber-100 placeholder-amber-700/40 focus:outline-none focus:border-amber-500"
              autoComplete="off"
              spellCheck={false}
              disabled={validating}
            />
          </label>

          <button
            type="submit"
            disabled={validating || !token.trim()}
            className="w-full px-6 py-3 rounded-lg border-2 border-amber-600/60 bg-amber-900/30 backdrop-blur-md font-quintessential text-amber-100 hover:bg-amber-800/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {validating ? "Verifying…" : "⚔️ Take the oath"}
          </button>

          {error && (
            <p className="font-medievalsharp text-sm text-red-400/80">
              The Quest Giver did not recognise that sigil: {error}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
```

### `src/App.tsx` — add route

```tsx
import LoginPage from "@/pages/LoginPage";
// ...
<Route path="/login" element={<LoginPage />} />
// (Keep the existing /login/callback for future OAuth — they don't conflict)
```

### `src/hooks/useAuth.ts` — replace OAuth `login()` with token-flow redirect

Replace the existing `login()` and `completeOAuth()` with a single `login()` that pushes to the new `/login` page:

```tsx
const login = useCallback((returnTo: string = "/") => {
  navigate(`/login?next=${encodeURIComponent(returnTo)}`);
}, [navigate]);
// completeOAuth → remove, no longer used
```

Need `useNavigate` imported. Note: `useAuth` is a hook so it can use react-router hooks freely.

### `src/components/ui/AuthGate.tsx` — already exists, no changes

It already redirects to `loginUrl()` — which now goes to `/login` instead of OAuth. The change in `useAuth.login` is the only place this needs editing.

## Verify

1. `bun run build` passes
2. `bun run dev` → navigate to `/challenges` while logged out → "sign in" button → goes to `/login` with `?next=/challenges`
3. Open `https://api.ctf.chron0.tech/register` in another tab → make a test account
4. Generate a token at `/settings#tokens` → paste into `/login` → click "Take the oath"
5. Successful login → redirects back to `/challenges` → shows authenticated UI

## Edge cases to handle

- Invalid token → CTFd returns 401, the form's catch block surfaces it — already wired
- Expired token → same as above, just a different message
- Empty submit → button disabled while empty (already wired)

## Commit

```bash
git add src/pages/LoginPage.tsx src/App.tsx src/hooks/useAuth.ts
git commit -m "site: manual-token auth flow at /login (OAuth deferred)"
```

---

# Phase 3 — Hints UI + unlock flow (~3 h)

**Goal:** display hints on each challenge detail page with their cost. Player clicks "Unlock for 25 GP" → POST `/unlocks` → hint content is fetched + displayed → player's score decreases by the cost.

## CTFd API surface for hints

- `GET /api/v1/challenges/<id>/hints` — returns array of `{ id, cost }` for locked hints. Cost is in points. **No content** in the list response.
- `GET /api/v1/hints/<id>` — returns `{ id, cost, content }`. Only succeeds if the player has unlocked it (or is admin).
- `POST /api/v1/unlocks` body `{ target: <hint_id>, type: "hints" }` — unlocks the hint. CTFd deducts cost from player's score, then `GET /hints/<id>` works.

## Files

### `src/hooks/useHints.ts` (new)

```tsx
import { useCallback, useEffect, useState } from "react";
import { directGet, directPost, proxyGet } from "@/lib/ctfdClient";

export interface HintMeta {
  id: number;
  cost: number;
}

export interface UnlockedHint extends HintMeta {
  content: string;
}

interface UseHintsResult {
  hints: HintMeta[];
  unlocked: Record<number, string>;   // hint_id → content
  loading: boolean;
  unlocking: number | null;            // id of hint currently being unlocked
  error: string | null;
  unlock: (hintId: number) => Promise<void>;
}

export function useHints(challengeId: number, isAuthenticated: boolean): UseHintsResult {
  const [hints, setHints] = useState<HintMeta[]>([]);
  const [unlocked, setUnlocked] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [unlocking, setUnlocking] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const fetch = isAuthenticated ? directGet : proxyGet;
        const path = isAuthenticated
          ? `/challenges/${challengeId}/hints`
          : `/v1/challenges/${challengeId}/hints`;
        const j = await fetch<{ success: boolean; data: HintMeta[] }>(path);
        if (cancelled) return;
        setHints(j.data);
        // For each hint, if its content was previously unlocked, fetch it.
        if (isAuthenticated) {
          const contents: Record<number, string> = {};
          await Promise.all(
            j.data.map(async (h) => {
              try {
                const detail = await directGet<{ success: boolean; data: UnlockedHint }>(`/hints/${h.id}`);
                if (detail.success && detail.data.content) {
                  contents[h.id] = detail.data.content;
                }
              } catch {
                /* hint not unlocked yet — silent skip */
              }
            }),
          );
          if (!cancelled) setUnlocked(contents);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    if (challengeId) load();
    return () => { cancelled = true; };
  }, [challengeId, isAuthenticated]);

  const unlock = useCallback(async (hintId: number) => {
    setUnlocking(hintId);
    setError(null);
    try {
      await directPost<{ success: boolean }>("/unlocks", {
        target: hintId,
        type: "hints",
      });
      const detail = await directGet<{ success: boolean; data: UnlockedHint }>(`/hints/${hintId}`);
      if (detail.success) {
        setUnlocked((prev) => ({ ...prev, [hintId]: detail.data.content }));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setUnlocking(null);
    }
  }, []);

  return { hints, unlocked, loading, unlocking, error, unlock };
}
```

### `src/components/challenge/HintsPanel.tsx` (new)

```tsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useHints } from "@/hooks/useHints";
import { useAuth } from "@/hooks/useAuth";

export default function HintsPanel({ challengeId }: { challengeId: number }) {
  const { isAuthenticated, login } = useAuth();
  const { hints, unlocked, loading, unlocking, error, unlock } = useHints(challengeId, isAuthenticated);
  const [confirming, setConfirming] = useState<number | null>(null);

  if (loading) {
    return <p className="font-medievalsharp text-amber-500/60 italic">Consulting the oracle for hints…</p>;
  }

  if (hints.length === 0) {
    return null;   // no hints — don't render anything
  }

  return (
    <section className="mb-8">
      <h2 className="mb-3 font-quintessential text-xl text-amber-200">Whispered Hints</h2>
      <div className="space-y-3">
        {hints.map((h, i) => {
          const content = unlocked[h.id];
          const isUnlocked = !!content;
          const isUnlockingThis = unlocking === h.id;
          return (
            <motion.div
              key={h.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="p-4 rounded-lg border-2 border-amber-700/30 bg-stone-900/40 backdrop-blur-md"
            >
              <div className="flex items-baseline justify-between gap-3">
                <span className="font-quintessential text-amber-300">Hint {i + 1}</span>
                <span className="font-quintessential text-sm text-amber-400/80">
                  {h.cost > 0 ? `${h.cost} GP` : "free"}
                </span>
              </div>
              <AnimatePresence mode="wait">
                {isUnlocked ? (
                  <motion.div
                    key="unlocked"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-2"
                  >
                    <div
                      className="prose prose-invert max-w-none font-medievalsharp text-amber-200/80 [&_code]:text-amber-300 [&_code]:bg-stone-900/60 [&_code]:px-1 [&_code]:rounded"
                      dangerouslySetInnerHTML={{ __html: content }}
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    key="locked"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="mt-2"
                  >
                    {isAuthenticated ? (
                      confirming === h.id ? (
                        <div className="flex items-center gap-2">
                          <span className="font-medievalsharp text-sm text-amber-300/80">
                            Spend {h.cost} GP from your purse?
                          </span>
                          <button
                            onClick={async () => { setConfirming(null); await unlock(h.id); }}
                            disabled={isUnlockingThis}
                            className="px-3 py-1 rounded border border-amber-600/60 bg-amber-900/30 font-medievalsharp text-sm text-amber-100 hover:bg-amber-800/50 disabled:opacity-50"
                          >
                            {isUnlockingThis ? "Unlocking…" : "Yes"}
                          </button>
                          <button
                            onClick={() => setConfirming(null)}
                            className="px-3 py-1 rounded border border-amber-700/40 font-medievalsharp text-sm text-amber-400/80 hover:text-amber-300"
                          >
                            No
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setConfirming(h.id)}
                          className="px-4 py-1.5 rounded-lg border border-amber-700/40 bg-stone-900/50 font-medievalsharp text-sm text-amber-300 hover:bg-amber-900/30 hover:border-amber-600 transition"
                        >
                          🔓 Unlock for {h.cost} GP
                        </button>
                      )
                    ) : (
                      <button
                        onClick={() => login(window.location.pathname)}
                        className="px-4 py-1.5 rounded-lg border border-amber-700/40 bg-stone-900/50 font-medievalsharp text-sm text-amber-400/70 hover:text-amber-300"
                      >
                        Sign in to unlock hints
                      </button>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
        {error && <p className="font-medievalsharp text-sm text-red-400/80">Error: {error}</p>}
      </div>
    </section>
  );
}
```

### `src/pages/ChallengeDetailPage.tsx` — add the panel

After the "Provisions" (files) section, before the "Submit a Flag" section:

```tsx
import HintsPanel from "@/components/challenge/HintsPanel";
// ...
<HintsPanel challengeId={challengeId} />
```

## Verify

1. Open a challenge that has hints in CTFd admin (Lich has 2 hints — good test)
2. Logged out: see hints listed with "Sign in to unlock" buttons
3. Log in: see "Unlock for N GP" buttons; click → confirmation → unlocks → content shows
4. Refresh page: previously-unlocked hints still show their content (not just locked + cost)
5. Confirm score deducted in CTFd admin

## Commit

```bash
git add src/hooks/useHints.ts src/components/challenge/HintsPanel.tsx src/pages/ChallengeDetailPage.tsx
git commit -m "site: hints UI with unlock flow, framer-motion reveal animation"
```

---

# Phase 4 — Per-challenge solves list (~1 h)

**Goal:** under each challenge, show "N adventurers have completed this quest" with a small list of recent solvers + timestamps.

## API

`GET /api/v1/challenges/<id>/solves` — array of `{ account_id, name, date, account_url }`. Public, no auth needed. Allowlisted in the Vercel proxy.

## Files

### `src/hooks/useChallengeSolves.ts` (new)

```tsx
import { useEffect, useState } from "react";
import { proxyGet } from "@/lib/ctfdClient";

export interface ChallengeSolve {
  account_id: number;
  name: string;
  date: string;
  account_url: string;
}

export function useChallengeSolves(challengeId: number) {
  const [solves, setSolves] = useState<ChallengeSolve[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!challengeId) return;
    let cancelled = false;
    proxyGet<{ success: boolean; data: ChallengeSolve[] }>(`/v1/challenges/${challengeId}/solves`)
      .then((j) => { if (!cancelled) setSolves(j.data); })
      .catch(() => { /* silent — anonymous can sometimes get 403 if scoreboard hidden */ })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [challengeId]);

  return { solves, loading };
}
```

### `src/components/challenge/SolvesPanel.tsx` (new)

```tsx
import { useChallengeSolves } from "@/hooks/useChallengeSolves";
import { Link } from "react-router-dom";

export default function SolvesPanel({ challengeId }: { challengeId: number }) {
  const { solves, loading } = useChallengeSolves(challengeId);
  if (loading) return null;
  if (solves.length === 0) {
    return (
      <section className="mb-6 p-4 rounded-lg border border-amber-800/30 bg-stone-900/30">
        <p className="font-medievalsharp text-sm text-amber-500/60 italic">
          No adventurer has yet vanquished this quest.
        </p>
      </section>
    );
  }
  return (
    <section className="mb-6 p-4 rounded-lg border border-amber-800/30 bg-stone-900/30">
      <h3 className="font-quintessential text-base text-amber-200 mb-2">
        ⚔️ {solves.length} {solves.length === 1 ? "Victor" : "Victors"}
      </h3>
      <ul className="space-y-1 text-sm">
        {solves.slice(0, 10).map((s) => (
          <li key={s.account_id} className="flex justify-between text-amber-300/80 font-medievalsharp">
            <Link to={`/players/${s.account_id}`} className="hover:text-amber-100">{s.name}</Link>
            <span className="text-xs text-amber-500/60">{new Date(s.date).toLocaleString()}</span>
          </li>
        ))}
      </ul>
      {solves.length > 10 && (
        <p className="text-xs text-amber-500/60 font-medievalsharp mt-2">
          and {solves.length - 10} more…
        </p>
      )}
    </section>
  );
}
```

### `src/pages/ChallengeDetailPage.tsx` — add panel above hints

```tsx
import SolvesPanel from "@/components/challenge/SolvesPanel";
// ...
<SolvesPanel challengeId={challengeId} />
<HintsPanel challengeId={challengeId} />
```

> The `/players/<id>` route doesn't exist yet — Phase 6 adds it. For now, the link will 404 → caught by your existing `<Route path="*" element={<Navigate to="/" replace />} />`. Acceptable until Phase 6.

## Commit

```bash
git add src/hooks/useChallengeSolves.ts src/components/challenge/SolvesPanel.tsx src/pages/ChallengeDetailPage.tsx
git commit -m "site: per-challenge solves list with victor count + timestamps"
```

---

# Phase 5 — "My profile" badge in header (~1 h)

**Goal:** top-right corner of every page shows logged-in user's name + score + solve count. Sticky engagement signal.

## API

`GET /api/v1/users/me` — full current user info including `score`, name, etc. Authenticated.

## Files

### `src/hooks/useMe.ts` (new — extends current useAuth)

```tsx
import { useEffect, useState } from "react";
import { directGet, getBearerToken } from "@/lib/ctfdClient";

export interface MeStats {
  id: number;
  name: string;
  score: number;
  place: number | null;
  team_id: number | null;
}

export function useMe() {
  const [me, setMe] = useState<MeStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!getBearerToken()) {
      setLoading(false);
      return;
    }
    directGet<{ success: boolean; data: MeStats }>("/users/me")
      .then((j) => setMe(j.data))
      .catch(() => setMe(null))
      .finally(() => setLoading(false));
  }, []);

  return { me, loading };
}
```

### `src/components/ui/ProfileBadge.tsx` (new)

```tsx
import { useMe } from "@/hooks/useMe";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "react-router-dom";

export default function ProfileBadge() {
  const { isAuthenticated, login, logout } = useAuth();
  const { me } = useMe();

  if (!isAuthenticated || !me) {
    return (
      <button
        onClick={() => login(window.location.pathname)}
        className="font-medievalsharp text-sm text-amber-400/80 hover:text-amber-200 border border-amber-700/40 rounded-lg px-3 py-1 backdrop-blur-md bg-stone-950/50"
      >
        🗝️ Sign in
      </button>
    );
  }
  return (
    <div className="flex items-center gap-3 font-medievalsharp text-sm">
      <Link to={`/players/${me.id}`} className="text-amber-200 hover:text-amber-100">
        {me.name}
      </Link>
      <span className="text-amber-400 font-quintessential">{me.score} GP</span>
      {me.place && <span className="text-amber-500/70 text-xs">#{me.place}</span>}
      <button
        onClick={logout}
        className="text-amber-500/60 hover:text-amber-300 text-xs"
        title="Sign out"
      >
        ⎋
      </button>
    </div>
  );
}
```

### Mount in the global header

Find the existing `Header` component used on each page (likely `src/components/ui/Header.tsx`). Add `<ProfileBadge />` to the top-right:

```tsx
// In Header.tsx, inside the outer flex container:
<div className="absolute right-6 top-6 z-40">
  <ProfileBadge />
</div>
```

Or wherever fits the layout best. May need to add a header to pages that don't have one (LandingPage uses its own layout — add the badge there too).

## Commit

```bash
git add src/hooks/useMe.ts src/components/ui/ProfileBadge.tsx src/components/ui/Header.tsx src/pages/LandingPage.tsx
git commit -m "site: ProfileBadge in header showing score, place, and logout"
```

---

# Phase 6 — Player profile pages (~3 h)

**Goal:** `/players/<id>` route shows a player's profile — name, score, place, solve history.

## API

- `GET /api/v1/users/<id>` — public profile (name, score, country, place, affiliation)
- `GET /api/v1/users/<id>/solves` — public solve history
- The Vercel proxy already handles `/v1/users/<id>` via `USER_PATH_RE` (`^v1/users/(\d+)(/solves)?$`)

## Files

### `src/hooks/usePlayer.ts` (new)

```tsx
import { useEffect, useState } from "react";
import { proxyGet } from "@/lib/ctfdClient";

export interface PlayerProfile {
  id: number;
  name: string;
  score: number;
  place: number | null;
  team_id: number | null;
  affiliation: string | null;
  country: string | null;
}

export interface PlayerSolve {
  challenge_id: number;
  challenge: { name: string; category: string; value: number };
  date: string;
}

export function usePlayer(id: number) {
  const [profile, setProfile] = useState<PlayerProfile | null>(null);
  const [solves, setSolves] = useState<PlayerSolve[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    Promise.all([
      proxyGet<{ success: boolean; data: PlayerProfile }>(`/v1/users/${id}`),
      proxyGet<{ success: boolean; data: PlayerSolve[] }>(`/v1/users/${id}/solves`),
    ])
      .then(([p, s]) => {
        if (!cancelled) {
          setProfile(p.data);
          setSolves(s.data);
        }
      })
      .catch((e) => { if (!cancelled) setError(e instanceof Error ? e.message : String(e)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id]);

  return { profile, solves, loading, error };
}
```

### `src/pages/PlayerProfilePage.tsx` (new)

```tsx
import { Link, useParams } from "react-router-dom";
import TavernBackground from "@/components/background/TavernBackground";
import { usePlayer } from "@/hooks/usePlayer";

const CATEGORY_ICONS: Record<string, string> = {
  crypto: "🗝️", prog: "⚙️", llm: "🦜", osint: "🔭", rev: "📜", misc: "🌒",
};

export default function PlayerProfilePage() {
  const { id } = useParams<{ id: string }>();
  const playerId = Number(id);
  const { profile, solves, loading, error } = usePlayer(playerId);

  if (loading) {
    return <Shell><p className="font-medievalsharp text-amber-300/70">Consulting the oracle…</p></Shell>;
  }
  if (error || !profile) {
    return <Shell><p className="font-medievalsharp text-red-400/70">No adventurer found.</p></Shell>;
  }

  return (
    <Shell>
      <header className="mb-8">
        <h1 className="font-quintessential text-3xl text-amber-100">{profile.name}</h1>
        <div className="mt-2 flex gap-6 font-medievalsharp text-amber-300/80">
          <span><span className="text-amber-400 font-quintessential">{profile.score}</span> GP</span>
          {profile.place && <span>Rank <span className="text-amber-400 font-quintessential">#{profile.place}</span></span>}
          {profile.country && <span>{profile.country}</span>}
          {profile.affiliation && <span>{profile.affiliation}</span>}
        </div>
      </header>
      <section>
        <h2 className="font-quintessential text-xl text-amber-200 mb-3">Quest Log ({solves.length})</h2>
        {solves.length === 0 ? (
          <p className="font-medievalsharp text-amber-500/60 italic">No quests completed yet.</p>
        ) : (
          <ul className="space-y-2">
            {solves.map((s) => (
              <li key={`${s.challenge_id}-${s.date}`} className="flex items-baseline justify-between p-3 rounded-lg bg-stone-900/40 border border-amber-800/20">
                <div className="flex items-center gap-2">
                  <span>{CATEGORY_ICONS[s.challenge.category.toLowerCase()] ?? "•"}</span>
                  <Link to={`/challenges/${s.challenge.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}`} className="text-amber-200 font-medievalsharp hover:text-amber-100">
                    {s.challenge.name}
                  </Link>
                </div>
                <div className="flex gap-3 text-sm">
                  <span className="text-amber-400 font-quintessential">{s.challenge.value} GP</span>
                  <span className="text-amber-500/60 text-xs">{new Date(s.date).toLocaleDateString()}</span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </Shell>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <TavernBackground />
      <div className="relative z-30 max-w-3xl mx-auto px-6 py-12">
        <Link to="/scoreboard" className="text-amber-400/60 hover:text-amber-300 font-medievalsharp text-sm">← Scoreboard</Link>
        <div className="mt-4">{children}</div>
      </div>
    </div>
  );
}
```

### `src/App.tsx`

```tsx
import PlayerProfilePage from "@/pages/PlayerProfilePage";
// ...
<Route path="/players/:id" element={<PlayerProfilePage />} />
```

### Make scoreboard names linkable

In `src/components/ui/Scoreboard.tsx` (or wherever player rows are rendered), wrap player names in `<Link to={`/players/${player.teamId}`}>...</Link>`. Quick edit.

## Commit

```bash
git add src/hooks/usePlayer.ts src/pages/PlayerProfilePage.tsx src/App.tsx src/components/ui/Scoreboard.tsx
git commit -m "site: player profile pages with solve history at /players/:id"
```

---

# Phase 7 — Notifications bar (~1 h)

**Goal:** site-wide announcements bar at the top of every page. Auto-fetches from CTFd's notifications.

## API

`GET /api/v1/notifications` — array of `{ id, title, content, date, type }`. Public. Allowlisted in the Vercel proxy (or add to the allowlist if not — check `api/[...path].ts`).

## Files

### `src/hooks/useNotifications.ts` (new)

```tsx
import { useEffect, useState } from "react";
import { proxyGet } from "@/lib/ctfdClient";

export interface CtfdNotification {
  id: number;
  title: string;
  content: string;
  date: string;
  type: "toast" | "alert" | "background";
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<CtfdNotification[]>([]);
  useEffect(() => {
    let cancelled = false;
    proxyGet<{ success: boolean; data: CtfdNotification[] }>("/v1/notifications")
      .then((j) => { if (!cancelled) setNotifications(j.data); })
      .catch(() => { /* silent */ });
    return () => { cancelled = true; };
  }, []);
  return notifications;
}
```

### `src/components/ui/NotificationsBar.tsx` (new)

```tsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNotifications } from "@/hooks/useNotifications";

const DISMISSED_KEY = "dismissed_notifications";

function getDismissed(): Set<number> {
  try {
    return new Set(JSON.parse(sessionStorage.getItem(DISMISSED_KEY) ?? "[]"));
  } catch {
    return new Set();
  }
}

export default function NotificationsBar() {
  const all = useNotifications();
  const [dismissed, setDismissed] = useState(getDismissed());
  const visible = all.filter((n) => !dismissed.has(n.id));
  if (visible.length === 0) return null;

  const dismiss = (id: number) => {
    const next = new Set(dismissed);
    next.add(id);
    setDismissed(next);
    sessionStorage.setItem(DISMISSED_KEY, JSON.stringify(Array.from(next)));
  };

  return (
    <div className="sticky top-0 z-50 backdrop-blur-md bg-stone-950/80 border-b border-amber-700/40">
      <AnimatePresence>
        {visible.map((n) => (
          <motion.div
            key={n.id}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="max-w-5xl mx-auto px-4 py-2 flex items-center justify-between gap-3"
          >
            <div className="flex-1 font-medievalsharp text-sm text-amber-200/90">
              <strong className="text-amber-100">{n.title}</strong>
              {n.content && <span className="ml-2 text-amber-300/70">— {n.content}</span>}
            </div>
            <button
              onClick={() => dismiss(n.id)}
              className="font-medievalsharp text-amber-500/60 hover:text-amber-300 text-xs"
              aria-label="Dismiss"
            >
              ✕
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
```

### Mount at the top of `App.tsx`

```tsx
import NotificationsBar from "@/components/ui/NotificationsBar";
// ...
<BrowserRouter>
  <NotificationsBar />
  <Routes>...</Routes>
</BrowserRouter>
```

### Add `/v1/notifications` to the proxy allowlist if missing

Open `api/[...path].ts`, check `ALLOWED_PATHS`. If `/^v1\/notifications/` isn't there, add it:

```ts
const ALLOWED_PATHS = [
  // ... existing patterns
  /^v1\/notifications$/,
  /^v1\/notifications\/\d+$/,
];
```

## Commit

```bash
git add src/hooks/useNotifications.ts src/components/ui/NotificationsBar.tsx src/App.tsx api/[...path].ts
git commit -m "site: notifications bar with per-session dismiss"
```

---

# Phase 8 — Awards / first-blood UI (~2 h)

**Goal:** display awards (CTFd's award system, used for first-blood and custom badges) on player profile pages + a "First Blood" indicator on per-challenge solves.

## Setup in CTFd (admin side)

Awards in CTFd come in two ways:
- **Manual awards** — admin grants via UI (e.g. "First Blood" badge).
- **Plugin-driven** — `ctfd-first-blood` plugin or similar auto-awards on first solve. Jon would need to install this if he wants automatic first-blood.

For this phase: **build the display logic, even if no awards exist yet.** They'll just render empty until Jon configures CTFd to grant them.

## API

- `GET /api/v1/awards` — all awards (admin probably needed; might be public depending on config)
- `GET /api/v1/users/<id>/awards` — public for a specific user
- A solve is "first blood" if it's the first in `GET /v1/challenges/<id>/solves` — derive client-side

## Files

### `src/hooks/usePlayerAwards.ts` (new)

```tsx
import { useEffect, useState } from "react";
import { proxyGet } from "@/lib/ctfdClient";

export interface Award {
  id: number;
  name: string;
  description: string;
  category: string;
  date: string;
  value: number;
  icon: string | null;
}

export function usePlayerAwards(userId: number) {
  const [awards, setAwards] = useState<Award[]>([]);
  useEffect(() => {
    if (!userId) return;
    let cancelled = false;
    proxyGet<{ success: boolean; data: Award[] }>(`/v1/users/${userId}/awards`)
      .then((j) => { if (!cancelled) setAwards(j.data); })
      .catch(() => { /* silent */ });
    return () => { cancelled = true; };
  }, [userId]);
  return awards;
}
```

### Update `PlayerProfilePage.tsx` to render awards

Add above the Quest Log section:

```tsx
import { usePlayerAwards } from "@/hooks/usePlayerAwards";
// inside the component:
const awards = usePlayerAwards(playerId);
// in JSX:
{awards.length > 0 && (
  <section className="mb-6">
    <h2 className="font-quintessential text-xl text-amber-200 mb-3">Honours ({awards.length})</h2>
    <div className="flex flex-wrap gap-2">
      {awards.map((a) => (
        <div key={a.id} className="px-3 py-1.5 rounded-lg border border-amber-600/60 bg-amber-900/30 backdrop-blur-md">
          <span className="font-quintessential text-sm text-amber-100">{a.name}</span>
          {a.description && <span className="ml-2 font-medievalsharp text-xs text-amber-300/70">— {a.description}</span>}
        </div>
      ))}
    </div>
  </section>
)}
```

### First-blood indicator on SolvesPanel

In `src/components/challenge/SolvesPanel.tsx`, mark the first entry:

```tsx
{solves.slice(0, 10).map((s, i) => (
  <li key={s.account_id} className="flex justify-between text-amber-300/80 font-medievalsharp">
    <Link to={`/players/${s.account_id}`} className="hover:text-amber-100">
      {i === 0 && <span title="First Blood" className="mr-1">🩸</span>}{s.name}
    </Link>
    <span className="text-xs text-amber-500/60">{new Date(s.date).toLocaleString()}</span>
  </li>
))}
```

### Add `/v1/awards` and `/v1/users/<id>/awards` to proxy allowlist

In `api/[...path].ts` `ALLOWED_PATHS`:

```ts
/^v1\/users\/\d+\/awards$/,
/^v1\/awards$/,
```

## Commit

```bash
git add src/hooks/usePlayerAwards.ts src/pages/PlayerProfilePage.tsx src/components/challenge/SolvesPanel.tsx api/[...path].ts
git commit -m "site: awards display on profiles + first-blood indicator on solves"
```

---

# Verification checklist (cumulative, after all phases)

Run through these on the deployed site after each PR merges. Don't batch — catch regressions phase-by-phase.

- [ ] Phase 1: `/challenges/the-enchanted-parrot` shows description, files, connection_info
- [ ] Phase 2: `/login` accepts a valid CTFd token, rejects invalid, persists across reload (sessionStorage)
- [ ] Phase 3: Lich challenge shows 2 hints, locked → confirm prompt → unlock → content reveals → score deducted
- [ ] Phase 4: Each challenge with solves shows "N Victors" + recent names
- [ ] Phase 5: Header right-side shows your name + score; sign out works; signed-out shows "Sign in"
- [ ] Phase 6: Click a scoreboard name → profile page with solve history; refresh works
- [ ] Phase 7: Post a notification in CTFd admin → appears as a sticky bar; X dismisses it; new tab still shows it (per-session)
- [ ] Phase 8: Create a manual award in CTFd admin → appears on the player's profile; first solver on a challenge shows 🩸

## Across all phases

- [ ] `bun run build` passes after every PR
- [ ] No null-byte corruption in modified files (`for f in $(git diff --name-only); do LC_ALL=C grep -c $'\0' "$f"; done`)
- [ ] Vercel deployment URL matches the merged commit SHA
- [ ] Mobile responsive — check `/challenges/<slug>` on a phone-width viewport

---

# Out of scope (deferred)

- **Custom CTFd theme** at `api.ctf.chron0.tech` — Jon will revisit after these eight phases land. That's a separate ~12–20h project.
- **OAuth re-enable** (GitHub or Discord) — Jon parked this. Manual-token auth (Phase 2) covers the gap.
- **First-blood automation** — Phase 8 displays awards if they exist, but doesn't auto-grant. Requires a CTFd plugin like `ctfd-first-blood`. Add later if Jon wants automated awards.
- **Markdown rendering for hints/descriptions** — currently uses `dangerouslySetInnerHTML` because CTFd returns HTML-rendered markdown. If switching to client-side markdown for some reason, add `marked` + `dompurify`.
- **Pagination** for scoreboard / solves — fine until you have 1000+ users.

---

# What Cursor must NOT do

- ❌ Try to re-enable OAuth — parked deliberately. Manual-token flow only.
- ❌ Break the existing FantasyCtfPage (scoreboard at `/scoreboard`) — leave its rendering untouched
- ❌ Modify the Vercel proxy's read-only constraint — `api/[...path].ts` rejects non-GET, keep that
- ❌ Skip the per-phase build verification
- ❌ Commit files with null bytes — strip with `tr -d '\0'` before commit if any sneak in
- ❌ Touch the monorepo (`fantasy_ctf_challs`) — that's a separate repo
