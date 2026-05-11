# FantasyCTF Challenges

FantasyCTF is a high-fantasy CTF challenge repository containing 22 challenges across crypto, programming, OSINT, reverse engineering, LLM security, and web/misc puzzle styles.

This repo is the challenge + infrastructure source of truth for the FantasyCTF deployment stack (`api.ctf.chron0.tech` and challenge subdomains under `*.ctf.chron0.tech`).

## Development Docs

Contributor and local development workflows are documented in [`DEVELOPMENT.md`](./DEVELOPMENT.md).

Use this README for project overview and challenge catalog, then switch to `DEVELOPMENT.md` for authoring, testing, and deployment workflows.

## What Is In This Repository

- 22 themed challenges with difficulty spread from Beginner to Mythic
- Player-facing artifacts in per-challenge `challenge/` directories
- Reference solves in per-challenge `solution/` directories
- CTFd metadata files (`ctfd_meta.json`) for challenge import
- Dockerized services for networked and LLM-backed challenges
- Production infra assets in `infra/` (Traefik, CTFd, Postgres, Redis, LiteLLM, uptime)
- Planning and operations documentation in `docs/plans/`

## Challenge Catalog

### Crypto

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 1 | The Scribe's Encoded Scroll | Beginner | Base64 + ROT13 | 100 |
| 2 | The Goblin Messenger's Cipher | Easy | Vigenere cipher | 250 |
| 3 | The Dragon's Sealed Proclamation | Medium | Weak RSA keygen | 400 |
| 4 | The Lich's Cursed Oracle | Hard | AES-CBC bit-flipping | 600 |
| 5 | The Void Oracle's Lattice | Expert | Wiener's attack (RSA) | 1000 |

### Programming

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 6 | The Guild Ledger | Beginner | CSV parsing + primality logic | 100 |
| 7 | The Runic Vault | Easy | XOR brute-force | 250 |
| 8 | The Dungeon Cartographer | Medium | Dijkstra shortest path | 400 |
| 9 | The Arcane Protocol | Hard | TCP + HMAC handshake | 600 |
| 10 | The Prophecy Engine | Expert | Black-box function reversal | 1000 |
| 11 | The Chronomancer's Gauntlet | Legendary | Timed algorithm gauntlet | 1500 |
| 12 | The Abyssal Architect | Mythic | Custom stack VM | 2000 |

### OSINT

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 13 | The Cartographer's Lost Map | Beginner | Reverse image + geolocation | 100 |
| 14 | The Herald's Forgotten Broadcast | Easy | Username + git history enumeration | 150 |
| 15 | The Spy's Cipher Journal | Medium | EXIF + Base64 + ROT13 | 200 |

### Reverse Engineering

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 16 | The Runecaster's Compiled Tome | Easy | Python bytecode decompilation | 250 |

### LLM Security

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 17 | The Enchanted Parrot | Beginner | Basic prompt injection | 50 |
| 18 | The Whispering Merchant | Easy | System prompt bypass | 100 |
| 19 | The Court Wizard's Familiar | Medium | Output filter bypass | 150 |
| 20 | The Oracle of Shadows | Hard | Input + output bypass chain | 200 |
| 21 | The Mindflayer's Sanctum | Expert | Multi-agent bypass | 250 |

### Wizards Games / Misc

| # | Challenge | Difficulty | Technique | Initial Points |
| --- | --------- | ---------- | --------- | -------------- |
| 22 | The Ogre's Audition | Hard | Web Speech API + source analysis | 600 |

## Repository Layout

```text
fantasy_ctf_challs/
├── crypto/                      # Crypto challenges
├── prog/                        # Programming challenges (+ consolidated advanced compose)
├── osint/                       # OSINT challenges
├── rev/                         # Reverse challenge(s)
├── llm/                         # LLM challenge set + shared runtime config
├── misc/                        # Additional themed challenges
├── infra/                       # Production deployment stack (Docker Compose, plugins, secrets templates)
├── docs/plans/                  # Architecture, hosting, and operational playbooks
├── LORE.md                      # Event narrative/lore source
└── README.md
```

Typical per-challenge structure:

- `README.md` for challenge narrative, prompt, and player-facing instructions
- `challenge/` for files given to players
- `solution/` for an internal reference solve
- `ctfd_meta.json` for CTFd import metadata
- optional `Dockerfile` and `docker-compose.yml` for hosted challenges

## Scoring Model

All challenges use dynamic scoring with shared floor/decay behavior.

| Difficulty | Initial | Minimum | Decay |
| ---------- | ------- | ------- | ----- |
| Beginner | 100 | 30 | 30 |
| Easy | 250 | 30 | 30 |
| Medium | 400 | 30 | 30 |
| Hard | 600 | 30 | 30 |
| Expert | 1000 | 30 | 30 |
| Legendary | 1500 | 30 | 30 |
| Mythic | 2000 | 30 | 30 |

## Flag Convention

All flags use:

```text
FantasyCTF{...}
```

Flag bodies use stylized substitutions for theme flavor (for example `e -> 3`, `o -> 0`, `a -> 4`).

## Deployment Model (High Level)

- Beginner/Easy/Medium challenges are primarily static artifacts imported into CTFd
- Networked challenges run as Dockerized services
- Advanced programming challenges are bundled via `prog/docker-compose.yml`
- LLM challenges are containerized FastAPI services routed through an internal LiteLLM layer
- Production infra is managed from `infra/docker-compose.prod.yml`

For operational runbooks and deploy commands, use:

- [`docs/plans/HOSTING_PLAN_V3.md`](./docs/plans/HOSTING_PLAN_V3.md)
- [`docs/plans/VPS_OPERATIONS.md`](./docs/plans/VPS_OPERATIONS.md)

## Companion Site Repository

The player-facing web app/scoreboard lives in the sibling repository:

- `J:/projects/personal-projects/ctfd-live-scoreboard`

This challenge repository owns challenge content and backend infra; the site repository owns the frontend experience and serverless proxy/webhook layer.

## License / Usage

Educational and portfolio use. Originally built for ISSessions Fantasy CTF.
