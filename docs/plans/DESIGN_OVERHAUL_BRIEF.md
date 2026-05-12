# Design overhaul — scoreboard polish + CTFd theme build

**Audience:** Cursor (or Claude Code). Two work tracks, shared design system.
**Companion docs:** `SITE_IMPROVEMENTS_BRIEF.md` (functional improvements landing in parallel), `HOSTING_PLAN_V3.md` (architecture).
**Skills to invoke before executing (in order):** `anthropic-skills:impeccable` (already loaded into Jon's session; load on yours too), `anthropic-skills:huashu-design` (for hi-fi prototyping when shaping a page), `anthropic-skills:design-taste-frontend` (for the senior-UI craft pass), `anthropic-skills:redesign-existing-projects` (for Track A audit).

---

## 0 · Preflight (do not skip)

Impeccable requires PRODUCT.md and DESIGN.md before any design work. Neither exists in either repo yet. **Phase 0 creates them**. Both repos need these files because impeccable's `load-context.mjs` looks at each working tree.

You'll write two new files in **each** repo (`fantasy_ctf_challs` and `ctfd-live-scoreboard`). Identical content where it overlaps; track-specific sections per repo.

### `PRODUCT.md` (in both repos)

```markdown
# Product

## Register
brand

## Users

The site has three distinct audiences, in descending order of frequency:

1. **Tech recruiters** browsing Jon's portfolio. Mid-30s, half technical, on
   14" laptops, in office light. They scan headers and screenshots. They have
   ~90 seconds before they bounce or click another tab. Most have never heard
   of a CTF before — but they recognise polish.

2. **Cybersecurity students and CTF players** who find the site via Discord,
   GitHub, or LinkedIn. Mid-20s, deeply technical, comfortable reading source.
   They will dig into the about page, the challenge difficulty curve, and the
   GitHub repo. They form opinions about technical taste from code.

3. **Future-Jon** referencing the site to remember design decisions. The site
   should be self-documenting: someone editing a component six months from now
   should understand the system from the code.

## Product purpose

A permanent, personal-portfolio host for the 22 ISSessions Fantasy 2026 CTF
challenges Jon designed. The CTF works (challenges solvable, scores tracked),
but more importantly the *site* signals: this person can ship taste-driven
work, not just hack things together.

## Strategic principles

1. **The aesthetic is earnest, not ironic.** It's a high-fantasy CTF because
   that's the original ISSessions theme — not because fantasy is trendy. No
   memes, no winks. The tavern is real, the quest log is real, the parchment
   is real. Sincerity is the point.

2. **Discipline over decoration.** Fantasy themes get bad fast when every
   element tries to be ornate. Typography carries hierarchy; the chrome stays
   restrained. Particle effects exist only where they earn the cost.

3. **Editorial pacing on the long-form pages** (About, Landing). The site
   reads like a book opening, not a SaaS landing page. Generous whitespace,
   one idea per scroll-screen.

4. **Functional dignity on the interactive pages** (Challenges, Scoreboard,
   Submit). The tavern aesthetic stops at the door of the workshop — once
   you're solving, the chrome disappears, the focus is the work.

5. **No SaaS reflexes.** No 3-up feature card grids. No gradient-text headlines.
   No "Built by 〈logos〉" sections. No call-out boxes with side-stripe borders.

## Anti-references

- Generic "medieval" templates with parchment + amber + drop-caps + caligraphic
  flourishes everywhere. Visual diabetes.
- D&D-Beyond-style heavy texture overlays.
- CTFTime.org's bare-utility aesthetic — function but no presence.
- Stripe's pristine cleanliness — wrong register, the site isn't fintech.
- Any dark-mode SaaS dashboard. Slack-cobalt, GitHub-grey, Linear-purple.

## Tone

Quiet earnestness with occasional dry wit. Headlines speak as a narrator,
not as a marketer. "The Quest Giver Awaits" is fine. "Welcome to the
Ultimate AI-Powered CTF Experience" is the opposite of what we want.

Microcopy uses the worldbuilding consistently: gold pieces (GP) for points,
quests for challenges, adventurers for users, scrying for scoreboard polls.
Don't break the wall mid-sentence — never "submit a flag (i.e., the solution
string)". Use "speak the password" or similar in-world phrasing, and let the
form's placeholder hint at the format.
```

### `DESIGN.md` (in both repos)

```markdown
# Design system

## Color (OKLCH-first)

The current scoreboard CSS uses sRGB hex — convert all of these to OKLCH and
remove the hex literals. The palette below is the canonical source.

### Tavern (primary surface)

| Token | OKLCH | Approx hex | Use |
|---|---|---|---|
| `--tavern-pitch` | `oklch(0.12 0.015 60)` | ~#0d0805 | Page background. Tinted toward warm hue 60° (amber). |
| `--tavern-ink` | `oklch(0.18 0.020 60)` | ~#1a120a | Card / section backgrounds. |
| `--tavern-stone` | `oklch(0.28 0.025 60)` | ~#2e2218 | Raised surfaces, modal backgrounds. |
| `--tavern-leather` | `oklch(0.42 0.080 50)` | ~#5a3e26 | Borders, dividers, low-emphasis accents. |
| `--tavern-fire` | `oklch(0.72 0.18 55)` | ~#e0a168 | Primary action color (warmer than amber-gold). |
| `--tavern-gold` | `oklch(0.86 0.16 95)` | ~#e8c860 | Hero accents, scores, "earned" feel. **≤10% of any surface.** |
| `--tavern-parchment` | `oklch(0.92 0.04 80)` | ~#ebdbb8 | Body text on dark surfaces. |

### Functional

| Token | OKLCH | Use |
|---|---|---|
| `--success` | `oklch(0.68 0.16 145)` | Solved, correct flag, healthy status. Muted forest green, not Slack-green. |
| `--warning` | `oklch(0.74 0.16 70)` | Hint cost prompts, time-limited indicators. |
| `--danger` | `oklch(0.62 0.20 25)` | Wrong flag, rate-limit hits, errors. Russet, not fire-engine red. |
| `--info` | `oklch(0.78 0.10 240)` | Hint-revealed content, neutral notifications. Cool slate. |

### Forbidden colours

- `#000`, `#fff`, `#000000`, `#ffffff` — every neutral must tint toward hue 60° (warm) by 0.01–0.02 chroma.
- Pure red `oklch(0.6 0.25 30)` and pure blue `oklch(0.5 0.2 250)` — too saturated for the warmer palette.
- Anything with chroma > 0.18 at lightness > 0.7 — looks garish at light end.

### Color strategy declaration

This palette is **Committed** (per `impeccable` register taxonomy): one
saturated color (`--tavern-fire`/`--tavern-gold` in concert) carries
30–60% of the visual identity. Other accents are intentionally absent.
This is NOT "Restrained" — embrace the warmth.

## Typography

### Families

| Token | Family | Use |
|---|---|---|
| `--font-display` | `"Cormorant Garamond", "Quintessential", serif` | Page titles, hero headlines, major section headers |
| `--font-body` | `"Crimson Pro", "EB Garamond", Georgia, serif` | Body text — replaces MedievalSharp for readability at small sizes |
| `--font-flavor` | `"MedievalSharp", cursive` | Ornamental only — quest names, decorative captions. Not body. |
| `--font-mono` | `"JetBrains Mono", "Fira Code", monospace` | Code, flags, API keys, terminal output |

**Drop** `Rajdhani` and `Inter` from `src/index.css` — they were Skills-Sheridan baggage, no longer used now that page is archived.

**Add** `Cormorant Garamond` and `Crimson Pro` to the Google Fonts import line. Both are exquisite serifs that read as "literary" rather than "fantasy template."

### Scale

Use a 1.333 ratio (perfect fourth) — generous editorial pacing.

| Token | Size | Use |
|---|---|---|
| `text-xs` | 0.75rem | Captions, eyebrows, footer text |
| `text-sm` | 0.875rem | Microcopy, metadata, table rows |
| `text-base` | 1rem (16px) | Body text minimum |
| `text-lg` | 1.125rem | Larger body, important paragraphs |
| `text-xl` | 1.5rem | H4 / subsection headings |
| `text-2xl` | 2rem | H3 / section headings |
| `text-3xl` | 2.66rem | H2 / page subtitle |
| `text-4xl` | 3.5rem | H1 — only on landing-style pages |
| `text-5xl` | 4.65rem | Hero only, rare |

Body line-length: **clamp(45ch, 65ch, 75ch)** — wider than dashboard UI, narrower than full-width landings.

### Weight

Body 400, emphasis 600, never 700 for body. Headlines 400 italic (the Cormorant Italic is the workhorse), 600 only for emphasis-on-emphasis.

## Spacing rhythm

Vary; don't apply uniform padding everywhere. Reach for:

- `space-y-2` (0.5rem) inside dense data rows
- `space-y-4` (1rem) between paragraphs
- `space-y-8` (2rem) between subsections
- `space-y-16` (4rem) between major sections on landing-style pages
- `space-y-24` (6rem) between top-level page regions (hero → body → footer)

Section pacing on landing/about pages: aim for one "screen of attention" per
section. ~85vh per screen, varying vertical rhythm to break monotony.

## Layout

- **No nested cards.** A challenge tile is a card. A hint inside a challenge
  is NOT a card — it's a section with a border-top divider and indent.
- **No `<div>`-wrapped containers as default.** If a section doesn't need a
  visible frame, don't give it one.
- **No 3-up feature card grids.** Lists are vertical with hierarchy unless
  the data is genuinely tabular.
- Max content width: 65rem (`max-w-5xl` in Tailwind v4). Wider than typical
  but the tavern background can breathe.

## Motion

- Exponential ease-out only: `cubic-bezier(0.16, 1, 0.3, 1)` (a.k.a.
  `ease-out-expo`) or `cubic-bezier(0.22, 1, 0.36, 1)` (`ease-out-quart`).
- No bounces, no elastics, no spring overshoots.
- Don't animate layout properties (`width`, `height`, `top`, `left`). Use
  `transform` and `opacity`.
- Default transition duration: 200ms for hover state, 400ms for page-level
  reveal, 800ms for storyline-pacing (animated text reveals).
- Particle effects (Fireflies, Aurora) stay subtle — opacity ≤0.35, density
  ≤30 particles. Audit current values in `TavernBackground.tsx` and ratchet
  down if exceeded.

## Absolute bans (audit existing code for these)

These violate `impeccable`'s shared design laws. Every occurrence must be
rewritten:

- **Side-stripe borders** (`border-l-4 border-amber-500` decorating a card).
  Rewrite with full borders, leading icons, or background tints.
- **Gradient text** (`bg-gradient-to-r ... text-transparent bg-clip-text`).
  Use solid `text-tavern-gold` and emphasis through weight/size.
- **Glassmorphism as default** (`backdrop-blur-xl bg-white/10`). Currently
  used on many cards in the scoreboard — audit and reduce. Glass is fine on
  the hero tavern background, NOT on every card.
- **Hero-metric template** (Big Number / Small Label / 3 supporting stats).
  Don't introduce this anywhere.
- **Identical card grids** — confirm `ChallengesPage` doesn't render 22
  visually-identical tiles. Vary by category, difficulty, or solve status.
- **Modal-first interactions.** If a flow could be inline or progressive,
  do that instead.

## Copy bans

- No em dashes (`—`). Use commas, colons, semicolons, periods, parentheses.
- No restated headings ("Welcome to the Welcome page").
- Every word earns its place. Cursor: audit microcopy as you go.

## Site-specific

### `ctf.chron0.tech` (Track A — React/Vite SPA)

Long-form pages (Landing, About): editorial pacing, generous spacing, serif
display. Interactive pages (Challenges, Submit, Scoreboard): tighter, more
chrome, functional dignity.

### `api.ctf.chron0.tech` (Track B — CTFd Jinja theme)

Lives "behind the workshop door." Players who get this far are technical and
care about function. Use the same tokens but lean tighter — closer to
"functional dignity" register than "editorial pacing." Admin pages stay
core-theme until forced otherwise (CTFd theme loader blocks `admin/*` overrides
from non-admin themes anyway).
```

After creating these files in both repos, **commit them on separate branches** — they're foundational, every later commit references them.

---

## Track A — Scoreboard repo audit + polish

**Working dir:** `J:\projects\personal-projects\ctfd-live-scoreboard`.
**Branch:** `feat/design-overhaul` off `main`.
**Skill to invoke:** `anthropic-skills:redesign-existing-projects` (for the audit), then `anthropic-skills:impeccable` `polish` sub-command on each phase.

**Audit findings from inspection of `src/index.css` and component tree:**

1. **Color palette is hex, not OKLCH.** `#110a00`, `#2a1a0a`, `#8b4513`, `#ffd700`, `#ff8c42`, `#e8d5b0` in `@theme` block. Migrate per the DESIGN.md tokens.
2. **`Rajdhani` and `Inter` fonts in the Google Fonts import** — leftover from archived Skills Sheridan theme. Remove.
3. **Body font is `MedievalSharp` for all body text** — readable at large sizes, terrible at 14px. Replace with `Crimson Pro` for body, keep MedievalSharp for ornamental moments only.
4. **No DESIGN.md / PRODUCT.md.** Phase 0 fixes this.
5. **Heavy backdrop-blur usage** — needs an audit pass to remove glassmorphism-as-default.
6. **Body background is solid `#110a00`** but the body element is styled in `index.css` with that exact hex — replace with OKLCH variable.
7. **Custom scrollbar** uses `rgba(139, 69, 19, X)` (the brown amber) — works, but convert to OKLCH for consistency.

### A.1 — Token migration (Cursor: `impeccable polish src/index.css`)

Rewrite `src/index.css` with the DESIGN.md OKLCH palette. Concrete diff:

```css
/* Replace the @theme block with: */
@theme {
  /* Tavern surface palette */
  --color-tavern-pitch:     oklch(0.12 0.015 60);
  --color-tavern-ink:       oklch(0.18 0.020 60);
  --color-tavern-stone:     oklch(0.28 0.025 60);
  --color-tavern-leather:   oklch(0.42 0.080 50);
  --color-tavern-fire:      oklch(0.72 0.180 55);
  --color-tavern-gold:      oklch(0.86 0.160 95);
  --color-tavern-parchment: oklch(0.92 0.040 80);

  /* Functional */
  --color-success: oklch(0.68 0.16 145);
  --color-warning: oklch(0.74 0.16 70);
  --color-danger:  oklch(0.62 0.20 25);
  --color-info:    oklch(0.78 0.10 240);

  /* Typography stacks */
  --font-display: "Cormorant Garamond", "Quintessential", Georgia, serif;
  --font-body:    "Crimson Pro", "EB Garamond", Georgia, serif;
  --font-flavor:  "MedievalSharp", cursive;
  --font-mono:    "JetBrains Mono", "Fira Code", monospace;
}

/* Replace the Google Fonts @import with: */
@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=MedievalSharp&family=JetBrains+Mono:wght@400;600&display=swap");
@import "tailwindcss";

/* Replace utility font classes — DELETE old ones, ADD: */
@utility font-display { font-family: var(--font-display); }
@utility font-body { font-family: var(--font-body); }
@utility font-flavor { font-family: var(--font-flavor); }
@utility font-mono { font-family: var(--font-mono); }

/* Update body styles: */
body {
  margin: 0;
  padding: 0;
  background: var(--color-tavern-pitch);
  color: var(--color-tavern-parchment);
  font-family: var(--font-body);
  font-size: 1rem;
  line-height: 1.65;
  overflow-x: hidden;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Update scrollbar: */
::-webkit-scrollbar-track   { background: var(--color-tavern-ink); }
::-webkit-scrollbar-thumb   { background: color-mix(in oklch, var(--color-tavern-leather) 60%, transparent); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--color-tavern-leather); }
```

### A.2 — Class rename pass

The codebase uses `font-quintessential` and `font-medievalsharp` everywhere. With the rename:

- `font-quintessential` → `font-display` (Cormorant headlines)
- For *ornamental* moments (quest titles in modals, hero subtitle decoration): `font-flavor` (MedievalSharp)
- For body text: rely on body default (Crimson Pro), no class needed

**Cursor's mechanical pass:**

```bash
cd J:\projects\personal-projects\ctfd-live-scoreboard

# Replace font-quintessential with font-display globally
grep -rl 'font-quintessential' src/ | xargs sed -i 's/font-quintessential/font-display/g'

# font-medievalsharp on BODY text should become unset (body default Crimson Pro)
# This needs case-by-case judgment — DO NOT mass-replace. Use semantic review:
# - In a quest/category label or ornamental caption: keep as font-flavor
# - In paragraph/description text: remove the class (body default applies)
```

After the global rename, **manually review every `font-flavor` (formerly `font-medievalsharp`)** usage and decide: keep for ornament, or remove because it's body text. This is the audit pass where impeccable's `critique` shines — invoke it.

### A.3 — Hex color replacement

```bash
# Find all hex colors:
grep -rEn '#[0-9a-fA-F]{3,8}\b' src/ | grep -v node_modules
```

Replace each with the OKLCH token. Most hex colors live in `src/contexts/ThemeContext.tsx` (the big FANTASY_THEME object). That file is huge — go section by section:

- `bg-stone-950/X` → `bg-tavern-pitch/X` where X is opacity
- `border-amber-X` → `border-tavern-leather` or `border-tavern-fire` depending on emphasis
- `text-amber-X` → `text-tavern-fire` (primary actions), `text-tavern-gold` (hero accents), `text-tavern-parchment` (body)
- The `rgba(255, 165, 0, 0.06)` boxshadow → `color-mix(in oklch, var(--color-tavern-fire) 6%, transparent)`

### A.4 — Glassmorphism audit

```bash
grep -rn 'backdrop-blur' src/
```

For each match, ask: "is this card the hero of a page, OR is it a generic content surface?" If hero (e.g., the landing CTA card, a single primary card on a page): keep glass. If generic content (every challenge tile, every panel, every hint card): replace with `bg-tavern-ink/85` (opaque enough to be a surface).

Rule of thumb: at most 2–3 glass surfaces visible at once on any given page.

### A.5 — Card / nesting audit (per impeccable shared laws)

```bash
grep -rn 'rounded-lg.*border.*bg-' src/
```

Look for cards-inside-cards. Common offenders:
- A challenge detail page wrapping the whole thing in a card, then having Hints inside another card, then the form inside another card.

**Rewrite** by removing the outer card and using border-top dividers or wider spacing to separate sections. Sections need not all be cards.

### A.6 — Header / nav consolidation

`src/components/ui/Header.tsx` exists. `ProfileBadge.tsx` exists (from SITE_IMPROVEMENTS phase 5). `NotificationsBar.tsx` exists (phase 7). They need to compose into a single coherent global header.

**Goal layout** (Cursor: prototype with `huashu-design` skill first if uncertain):

```
┌──────────────────────────────────────────────────────────────┐
│  [Notifications bar — only when active, full-width]          │
├──────────────────────────────────────────────────────────────┤
│  [Logo / wordmark — "FantasyCTF"]    [Nav: Quests · Scoreboard · About]    [ProfileBadge / Sign in]  │
├──────────────────────────────────────────────────────────────┤
│  [Page content]                                              │
└──────────────────────────────────────────────────────────────┘
```

- Logo: `font-display` serif, italic, 1.5rem. Just "FantasyCTF" or a glyph (a sealed scroll? a tavern lantern?).
- Nav: 3 items max in the persistent nav. Footer carries the rest.
- ProfileBadge: existing component, but verify it uses new tokens.

Audit `Header.tsx` and consolidate. The existing Header currently includes hero-style content (banner image + h1) which **belongs on the landing page only**, not in a global header. Split: keep an `Header` that's the global nav, move the hero banner into `LandingPage.tsx` only.

### A.7 — Landing page editorial pass

`src/pages/LandingPage.tsx` is currently a single-section hero with two CTAs. **Expand into a proper editorial landing**:

Structure:

1. **Hero** (current content, tightened) — 100vh
2. **The Quests** — preview 3 challenge categories with one line each. No card grid; vertical hierarchy with serif numerals.
3. **What's hiding in the LLM challenges** — a paragraph about the BYO-key architecture. Worth ~500 words for the technical audience.
4. **Behind the curtain** — link to the GitHub repo with a 2-sentence pitch.
5. **About Jon** — one paragraph, link to `/about`.
6. **Footer** — copyright, ISSessions credit, social links.

Each section: ~80vh. Generous space between. Animations on scroll (use existing `AnimatedContent` component but verify motion curves match the new spec — `cubic-bezier(0.16, 1, 0.3, 1)` ease-out-expo).

### A.8 — Challenge detail page polish

`src/pages/ChallengeDetailPage.tsx` shows description, files, hints, BYO-key (for LLM), and flag submission. **Audit**: is the order right? Is anything redundant?

Recommended order (top to bottom):
1. Title + value + category badge (compact)
2. Solves panel (small, sidebar-ish — "12 victors, latest: foo, 3h ago")
3. Description (the prose)
4. Provisions / files (if any)
5. LLM panels (if LLM): BYOKeyForm, then LLMUsageInstructions, then LLMDemoAnimation
6. Hints (with unlock flow)
7. Submit flag (sticky bottom on mobile, inline on desktop)

Decisions worth invoking `impeccable critique` on:
- Should solves be a sidebar (desktop) and a collapsed section (mobile)?
- Should the submit form be sticky?
- Should the demo animation be expand-to-show rather than always-visible?

### A.9 — Accessibility + responsive audit

After the design changes land, run `anthropic-skills:web-design-guidelines` `audit` on:
- Color contrast (every text-on-surface pair must meet WCAG AA 4.5:1 for body, 3:1 for large)
- Keyboard navigation (every interactive element reachable via Tab, focus visible)
- Mobile breakpoints (test 375px, 768px, 1024px, 1440px)

OKLCH palette above is designed to pass — `--tavern-parchment` on `--tavern-pitch` is ~10:1 contrast — but verify after the token migration.

### A.10 — Phase verification

After each of A.1–A.9, `bun run build`, `bunx tsc -b --noEmit`, `bun run lint`. Visual review on `bun run dev`. Commit per phase.

```bash
git commit -m "design: A.1 OKLCH palette + Cormorant/Crimson Pro typography"
git commit -m "design: A.2-A.3 font class rename, hex→token replacement"
git commit -m "design: A.4 glassmorphism audit, reduce to hero usage only"
git commit -m "design: A.5 collapse nested cards, use dividers"
git commit -m "design: A.6 unified global header, hero moves to landing only"
git commit -m "design: A.7 editorial landing page with 5 sections"
git commit -m "design: A.8 challenge detail page layout refactor"
git commit -m "design: A.9 a11y + responsive audit fixes"
```

PR per phase or batched, your call.

---

## Track B — CTFd theme build (`api.ctf.chron0.tech`)

**Working dir:** new repo, call it `fantasy-ctfd-theme` — clone of `CTFd/core-theme`, separate from both existing repos.
**Skill to invoke:** `anthropic-skills:huashu-design` for prototyping each Jinja template's hi-fi version before writing, then `anthropic-skills:design-taste-frontend` for the implementation pass.

### B.0 — Provisioning

```bash
git clone https://github.com/CTFd/core-theme fantasy-ctfd-theme
cd fantasy-ctfd-theme
rm -rf .git
git init
git remote add origin https://github.com/jondmarien/fantasy-ctfd-theme.git
git add -A
git commit -m "chore: initial fork from CTFd/core-theme"
git branch -M main
git push -u origin main
git checkout -b feat/initial-fantasy-styling
```

Update `package.json` `name` to `fantasy-ctfd-theme`, `version` to `0.1.0`. Drop the original README; write a 3-paragraph one introducing the theme.

Copy `PRODUCT.md` and `DESIGN.md` from the scoreboard repo. They apply.

### B.1 — Stack + dev workflow

Inherited from core-theme:
- Bootstrap 5.3.x
- Alpine.js 3.x
- Vite 5.x (build only — `vite build --watch`, NOT a dev server)
- SCSS for styling

**Local dev workflow:**

```bash
yarn install
yarn dev    # vite build --watch — rebuilds on save; no HMR
```

To preview against a real CTFd instance, you have two options:

A. **Bind-mount** the theme dir into a local Docker CTFd:
   ```yaml
   ctfd:
     image: ctfd/ctfd:3.8.1
     volumes:
       - ./fantasy-ctfd-theme:/opt/CTFd/CTFd/themes/fantasy:ro
   ```
   Then in the local CTFd admin, switch theme to `fantasy`. Reload page to see changes.

B. **Rsync to the production VPS** after each rebuild. Slower iteration but tests against real data:
   ```bash
   yarn build && rsync -avz ./ ctf@<HETZNER_IP>:/opt/fantasy_ctf_challs/infra/ctfd/themes/fantasy/
   ```

Option A is the only sane dev loop. Use B for staging/sanity-check.

### B.2 — Token wiring

CTFd themes use SCSS. The DESIGN.md tokens need to land in `assets/scss/_tokens.scss`:

```scss
// assets/scss/_tokens.scss
:root {
  // Tavern surface palette
  --tavern-pitch:     oklch(0.12 0.015 60);
  --tavern-ink:       oklch(0.18 0.020 60);
  --tavern-stone:     oklch(0.28 0.025 60);
  --tavern-leather:   oklch(0.42 0.080 50);
  --tavern-fire:      oklch(0.72 0.180 55);
  --tavern-gold:      oklch(0.86 0.160 95);
  --tavern-parchment: oklch(0.92 0.040 80);

  // Functional
  --success: oklch(0.68 0.16 145);
  --warning: oklch(0.74 0.16 70);
  --danger:  oklch(0.62 0.20 25);
  --info:    oklch(0.78 0.10 240);

  // Type stacks
  --font-display: "Cormorant Garamond", "Quintessential", Georgia, serif;
  --font-body:    "Crimson Pro", "EB Garamond", Georgia, serif;
  --font-flavor:  "MedievalSharp", cursive;
  --font-mono:    "JetBrains Mono", monospace;
}

// Bootstrap variable overrides (Bootstrap reads SCSS variables, not CSS vars)
$primary:   #e0a168;
$secondary: #e8c860;
$dark:      #1a120a;
$body-bg:   #0d0805;
$body-color: #ebdbb8;
$font-family-base: var(--font-body);
$font-family-monospace: var(--font-mono);
$enable-shadows: false;
$enable-gradients: false;
```

In `assets/scss/main.scss`:

```scss
@import "tokens";
// Then the existing Bootstrap imports
@import "bootstrap/scss/bootstrap";
// Then component overrides
@import "components/navbar";
@import "components/challenges";
@import "components/scoreboard";
@import "components/forms";
```

### B.3 — Templates to touch (priority order)

CTFd has `THEME_FALLBACK=true` by default — untouched templates fall back to `core`. Start with the most-seen pages and let everything else inherit core until you get to it.

| Priority | Template | Why first |
|---|---|---|
| 1 | `base.html` | Every page extends it. Fonts, navbar, footer, body bg. |
| 2 | `challenges.html` | Most-seen page once logged in. |
| 3 | `challenge.html` | Single-challenge modal (the actual play surface). |
| 4 | `scoreboard.html` | Most-shared link. |
| 5 | `login.html`, `register.html`, `confirm.html`, `reset_password.html` | First impression for new visitors. |
| 6 | `users/private.html`, `users/public.html`, `users/users.html` | Profile + roster. |
| 7 | `settings.html` | Lower frequency. |
| 8 | `teams/*.html` | Only if you enable team mode (currently single-user — these can stay core-theme forever). |
| 9 | `page.html` | For admin-authored pages. Style minimally. |

Don't touch `admin/*` — CTFd's theme loader blocks non-admin themes from rendering admin templates, and the CTFd admin UI is not part of the user-facing experience anyway.

### B.4 — Each template's hi-fi shape

For each template in the priority list, **before writing Jinja**, prototype the hi-fi target using `huashu-design`. The prototype is an HTML file in a `mockups/` directory that gets committed but never deployed — purely a design artifact for shape review.

Example workflow:

```bash
mkdir -p mockups
# Invoke huashu-design skill, target: "design the CTFd challenges listing page,
# with the existing core-theme functionality, restyled per DESIGN.md tokens"
# It produces mockups/challenges.html — a static HTML file you can open in a browser.
# Review with Jon. Iterate. Confirm shape.
# Then translate to templates/challenges.html (real Jinja).
```

**Why the mockup step:** going straight from "core's Jinja" to "fantasy Jinja" without shape review tends to produce something that compiles but doesn't have intent. Mockups force the design decision before the engineering decision.

For each template, the mockup should reach:
- Header (matching site navbar pattern)
- Page-specific layout (e.g., challenge tiles in a vertical category-grouped list, not a 3-up grid)
- Footer
- Mobile responsive (verify at 375px)

### B.5 — Specific design decisions per template

#### `base.html`

- Navbar: brand on left ("FantasyCTF" wordmark in display serif italic), nav items center ("Quests" / "Scoreboard" / "About"), profile/login on right.
- Footer: simple — copyright, "originally designed for ISSessions Fantasy 2026 CTF", links to scoreboard repo + monorepo on GitHub.
- Body background: `--tavern-pitch`. No background image at this level — challenge subdomains and the scoreboard SPA carry the visual texture; CTFd stays calmer.
- Notifications/flashes: render as inline alerts with full borders (not side-stripes), tinted by `--success`/`--danger`/`--info`.

#### `challenges.html`

The core-theme renders this with a Bootstrap card grid. **Rewrite as a category-grouped vertical list**:

```
🗝️  Crypto                    5 quests · 1 conquered
  ┌──────────────────────────────────────────────────────────────┐
  │ The Scribe's Encoded Scroll        Beginner   100 GP   ✓ done│
  │ The Goblin Messenger's Cipher      Easy       150 GP         │
  │ ...                                                          │
  └──────────────────────────────────────────────────────────────┘

⚙️  Programming                 7 quests · 0 conquered
  ┌──────────────────────────────────────────────────────────────┐
  │ ...                                                          │
  └──────────────────────────────────────────────────────────────┘
```

Type hierarchy carries everything. Solved status: a small `✓` glyph in `--success`, not a giant green checkmark. Hidden challenges: shown grayed-out with `🔒` glyph, name visible, points value hidden.

#### `challenge.html`

This renders the *modal* contents. Tighter layout — players are focused on solving, not browsing.

Order:
1. Title + value + category badge
2. Description (rendered HTML, large)
3. Files / connection_info (if any)
4. Hints panel (collapsed by default, click to expand)
5. Solve count / first blood (small footer)
6. Flag submission form (inline)

No nested cards. Sections separated by horizontal rules (`<hr>` styled with tavern-leather color, full width).

#### `scoreboard.html`

Core-theme has a Chart.js graph + a sortable table. Keep both but restyle:

- Graph: muted colors, `--tavern-fire` and `--tavern-gold` as the two primary series. No bright multi-color rainbow.
- Table: serif body, monospace for scores, hover row gets a `--tavern-stone` background.
- Top 3 entries: subtle visual weight (slightly larger font, italic) without medals or trophy icons.

#### `login.html` / `register.html` / `confirm.html` / `reset_password.html`

Editorial single-column forms, ~480px max-width, centered.

- Form labels in `--font-display` italic
- Inputs: dark surface (`--tavern-ink`), `--tavern-leather` border, focus state changes border to `--tavern-fire`
- Submit button: `--tavern-fire` background, `--tavern-pitch` text, weight 600
- Helper text below inputs: small, `--tavern-parchment` at 0.6 opacity

#### `users/*.html`

Mirror the SPA's PlayerProfilePage layout: header with name + score + place, then "Quest Log" (solve history). No tabs — single scrollable column.

### B.6 — JS / behavior

Most of the JS in core-theme handles the challenge modal (Alpine.js component). **Don't touch the JS unless behavior changes are intended.** Styling alone gets you 95% of the way.

If you do customize behavior (e.g., adding a "copy connection_info to clipboard" button), keep the changes in `assets/js/components/` and reference from the templates.

### B.7 — Build + deploy

Local:

```bash
yarn build         # produces static/manifest.json + hashed assets
```

Deploy to VPS:

```bash
# After committing the theme repo + pushing to GitHub:
ssh ctf@<HETZNER_IP>

# Clone into CTFd themes directory:
cd /opt/fantasy_ctf_challs/infra/ctfd/themes
git clone https://github.com/jondmarien/fantasy-ctfd-theme fantasy

# CTFd container picks it up automatically because the bind-mount sees the
# new directory. No CTFd restart needed (theme loader scans on each request).

# Admin Panel → Config → Theme → select "fantasy" → save.
```

For updates after the first install:

```bash
ssh ctf@<HETZNER_IP>
cd /opt/fantasy_ctf_challs/infra/ctfd/themes/fantasy
git pull origin main
# That's it — the static/ build is committed (via .gitignore exception).
```

Decision: **commit `static/` to the repo.** Yes, it bloats history, but it means the VPS doesn't need Node/Yarn. The alternative — building on the VPS — adds 200MB of node_modules and a build step every deploy. Not worth it for a personal site.

Add to `.gitignore`:

```
node_modules/
.DS_Store
```

Explicitly NOT in `.gitignore`:

```
static/        # committed for deploy simplicity
```

### B.8 — CSRF + flag submission gotchas

CTFd's flag submission goes through `CTFd.pages.challenge.submitChallenge(id, value)` which adds the CSRF nonce automatically. Don't write your own `fetch()` calls without going through this — they'll 403.

If your theme's challenge modal embeds the submit form, use the existing form macro:

```jinja
{% from "macros/forms.html" import form_nonce %}
<form id="challenge-submit">
  {{ form_nonce() }}
  <input type="text" name="submission" />
  <button type="submit">⚔️ Strike</button>
</form>
```

The Alpine component handles wiring `submitChallenge` to the form submit event.

### B.9 — Theme verification

After install:

- [ ] Page loads at `https://api.ctf.chron0.tech/challenges` with fantasy styling
- [ ] All challenges visible, categories grouped, solve status displayed
- [ ] Click a challenge: modal opens, description renders, flag form submits and returns correct/incorrect
- [ ] Login / register flows work end-to-end
- [ ] Scoreboard renders chart + table
- [ ] No console errors
- [ ] Mobile: usable at 375px width
- [ ] WCAG AA contrast on all text-on-surface pairs
- [ ] Switching theme back to `core` in admin → site immediately reverts (no broken state, fallback works)

---

## Verification across both tracks

**Visual cohesion test:** screenshot both `ctf.chron0.tech/challenges` and `api.ctf.chron0.tech/challenges` side-by-side. Same palette? Same type? Same spacing rhythm? Same "this feels intentional" signal? If they look like two different products, the design system isn't actually shared.

**Slop test:** open both sites incognito on a fresh laptop. Ask a friend who's never seen them: "describe the aesthetic in one sentence." If the answer is "high fantasy CTF" — pass. If the answer is "looks like a Tailwind template" or "feels AI-generated" — fail. Iterate until pass.

**Recruiter test:** send the live URL to a non-technical friend. They have 60 seconds. Ask afterwards: "what does this person do?" The answer should be specific (cybersecurity, designed these challenges, built the site) rather than vague (something tech).

---

## Out of scope

- **CTFd admin UI restyling** — theme loader blocks non-admin themes from rendering `admin/*`. Skipped.
- **Theme switcher / dark mode toggle** — the design is intentionally one-mode (Tavern dark). No light variant.
- **Internationalization** — English only.
- **Email template customization** — CTFd uses separate email templates outside the theme. If you want to brand registration emails, that's a CTFd config setting + email template file, not part of this brief.

---

## Order of execution

```
Phase 0 (both repos): PRODUCT.md + DESIGN.md — commit on day 1
   │
   ├─► Track A.1 token migration ─► A.2 fonts ─► A.3 hex replace
   │   │
   │   └─► A.4 glass audit ─► A.5 card nesting ─► A.6 header
   │       │
   │       └─► A.7 landing editorial ─► A.8 challenge detail ─► A.9 a11y audit
   │
   └─► Track B.0 fork core-theme ─► B.1 dev workflow ─► B.2 token wiring
       │
       └─► B.3 base.html ─► challenges.html ─► challenge.html ─► scoreboard ─► auth
           │
           └─► B.7 deploy to VPS ─► B.9 verification
```

Tracks A and B can be parallel after Phase 0. A is ~12h of polish work. B is ~16h of theme build. Total: ~28–30h Cursor work. Realistic calendar: 2–3 weekends.

---

## What Cursor must NOT do

- ❌ Use hex literals — every color goes through OKLCH tokens
- ❌ Use `#000` or `#fff` anywhere
- ❌ Animate layout properties (width, height, top, left) — use transform + opacity
- ❌ Introduce side-stripe borders, gradient text, glassmorphism-as-default, hero-metric templates, identical card grids
- ❌ Use em dashes in copy — comma, colon, semicolon, period, parenthesis
- ❌ Skip the mockup step for CTFd templates in Track B — shape before engineering
- ❌ Build on the VPS — local build, commit `static/`, deploy via git pull
- ❌ Restyle CTFd admin pages — theme loader blocks it anyway
- ❌ Commit files with null bytes (the recurring corruption issue) — strip with `tr -d '\0'` before commit
- ❌ Skip phase verification — each phase ships only after `bun run build` + visual review
- ❌ Pile changes — one phase per PR, reviewed independently. Easier to roll back a single change than to unwind a megacommit
