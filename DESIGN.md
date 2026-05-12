# Design system

## Color (OKLCH-first)

The current scoreboard CSS uses sRGB hex. Convert all of these to OKLCH and
remove the hex literals. The palette below is the canonical source.

### Tavern (primary surface)

| Token | OKLCH | Approx hex | Use |
|---|---|---|---|
| `--tavern-pitch` | `oklch(0.12 0.015 60)` | ~#0d0805 | Page background. Tinted toward warm hue 60 deg (amber). |
| `--tavern-ink` | `oklch(0.18 0.020 60)` | ~#1a120a | Card / section backgrounds. |
| `--tavern-stone` | `oklch(0.28 0.025 60)` | ~#2e2218 | Raised surfaces, modal backgrounds. |
| `--tavern-leather` | `oklch(0.42 0.080 50)` | ~#5a3e26 | Borders, dividers, low-emphasis accents. |
| `--tavern-fire` | `oklch(0.72 0.18 55)` | ~#e0a168 | Primary action color (warmer than amber-gold). |
| `--tavern-gold` | `oklch(0.86 0.16 95)` | ~#e8c860 | Hero accents, scores, earned feel. **<=10% of any surface.** |
| `--tavern-parchment` | `oklch(0.92 0.04 80)` | ~#ebdbb8 | Body text on dark surfaces. |

### Functional

| Token | OKLCH | Use |
|---|---|---|
| `--success` | `oklch(0.68 0.16 145)` | Solved, correct flag, healthy status. Muted forest green, not Slack-green. |
| `--warning` | `oklch(0.74 0.16 70)` | Hint cost prompts, time-limited indicators. |
| `--danger` | `oklch(0.62 0.20 25)` | Wrong flag, rate-limit hits, errors. Russet, not fire-engine red. |
| `--info` | `oklch(0.78 0.10 240)` | Hint-revealed content, neutral notifications. Cool slate. |

### Forbidden colours

- `#000`, `#fff`, `#000000`, `#ffffff`. Every neutral must tint toward hue 60 deg (warm) by 0.01 to 0.02 chroma.
- Pure red `oklch(0.6 0.25 30)` and pure blue `oklch(0.5 0.2 250)`, too saturated for the warmer palette.
- Anything with chroma > 0.18 at lightness > 0.7, looks garish at the light end.

### Color strategy declaration

This palette is **Committed** (per impeccable register taxonomy): one
saturated color (`--tavern-fire`/`--tavern-gold` in concert) carries
30 to 60% of the visual identity. Other accents are intentionally absent.
This is NOT Restrained, embrace the warmth.

## Typography

### Families

| Token | Family | Use |
|---|---|---|
| `--font-display` | `"Cormorant Garamond", "Quintessential", serif` | Page titles, hero headlines, major section headers |
| `--font-body` | `"Crimson Pro", "EB Garamond", Georgia, serif` | Body text, replaces MedievalSharp for readability at small sizes |
| `--font-flavor` | `"MedievalSharp", cursive` | Ornamental only, quest names, decorative captions. Not body. |
| `--font-mono` | `"JetBrains Mono", "Fira Code", monospace` | Code, flags, API keys, terminal output |

Drop `Rajdhani` and `Inter` from `src/index.css`, they were Skills-Sheridan
baggage and are no longer used now that page is archived.

Add `Cormorant Garamond` and `Crimson Pro` to the Google Fonts import line.
Both are literary serifs rather than fantasy template defaults.

### Scale

Use a 1.333 ratio (perfect fourth) for editorial pacing.

| Token | Size | Use |
|---|---|---|
| text-xs | 0.75rem | Captions, eyebrows, footer text |
| text-sm | 0.875rem | Microcopy, metadata, table rows |
| text-base | 1rem (16px) | Body text minimum |
| text-lg | 1.125rem | Larger body, important paragraphs |
| text-xl | 1.5rem | H4 / subsection headings |
| text-2xl | 2rem | H3 / section headings |
| text-3xl | 2.66rem | H2 / page subtitle |
| text-4xl | 3.5rem | H1, only on landing-style pages |
| text-5xl | 4.65rem | Hero only, rare |

Body line-length: clamp(45ch, 65ch, 75ch).

### Weight

Body 400, emphasis 600, never 700 for body. Headlines 400 italic
(Cormorant Italic is the workhorse), 600 only for emphasis-on-emphasis.

## Spacing rhythm

Vary, don't apply uniform padding everywhere.

- `space-y-2` (0.5rem) inside dense data rows
- `space-y-4` (1rem) between paragraphs
- `space-y-8` (2rem) between subsections
- `space-y-16` (4rem) between major sections on landing-style pages
- `space-y-24` (6rem) between top-level page regions (hero -> body -> footer)

Section pacing on landing/about pages: aim for one screen of attention per
section, around 85vh per screen with varied vertical rhythm.

## Layout

- No nested cards. A challenge tile is a card. A hint inside a challenge is a
  section with divider and indent, not another card.
- No container wrappers as default. If a section doesn't need a visible frame,
  don't give it one.
- No 3-up feature card grids. Lists stay vertical unless data is tabular.
- Max content width: 65rem (`max-w-5xl`).

## Motion

- Exponential ease-out only: `cubic-bezier(0.16, 1, 0.3, 1)` or
  `cubic-bezier(0.22, 1, 0.36, 1)`.
- No bounces, no elastics, no spring overshoots.
- Don't animate layout properties (`width`, `height`, `top`, `left`), use
  `transform` and `opacity`.
- Default transition duration: 200ms for hover, 400ms for page-level reveal,
  800ms for storyline-pacing text reveals.
- Particle effects (Fireflies, Aurora) stay subtle. opacity <=0.35, density
  <=30 particles.

## Absolute bans (audit existing code for these)

- Side-stripe borders (`border-l-*` accents on cards). Use full borders,
  leading icons, or background tints.
- Gradient text (`bg-gradient-*` + `bg-clip-text`). Use solid `text-tavern-gold`.
- Glassmorphism as default (`backdrop-blur` on generic cards).
- Hero-metric template (Big Number / Small Label / supporting stats).
- Identical card grids.
- Modal-first interactions where inline/progressive can work.

## Copy bans

- No em dashes. Use commas, colons, semicolons, periods, parentheses.
- No restated headings.
- Every word earns its place.

## Site-specific

### `ctf.chron0.tech` (Track A, React/Vite SPA)

Long-form pages (Landing, About): editorial pacing, generous spacing, serif
display. Interactive pages (Challenges, Submit, Scoreboard): tighter, more
chrome, functional dignity.

### `api.ctf.chron0.tech` (Track B, CTFd Jinja theme)

Lives behind the workshop door. Players are technical and care about function.
Use the same tokens but tighter than landing/editorial surfaces. Admin pages
stay core-theme unless forced otherwise.
