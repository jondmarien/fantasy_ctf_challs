# FantasyCTF Challenges

A collection of 20 Capture The Flag challenges with a high-fantasy theme, designed for [ISSessions](https://issessions.ca/) FantasyCTF. Covers **Cryptography**, **Programming**, **OSINT**, **Reverse Engineering**, **LLM Security**, and **The Wizards Games** across multiple difficulty tiers.

## Challenge Overview

### Crypto

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 1 | The Scribe's Encoded Scroll | Beginner | Base64 + ROT13 | 100 |
| 2 | The Goblin Messenger's Cipher | Easy | Vigenère cipher | 250 |
| 3 | The Dragon's Sealed Proclamation | Medium | Weak RSA (deterministic keygen) | 400 |
| 4 | The Lich's Cursed Oracle | Hard | AES-CBC bit-flipping | 600 |
| 5 | The Void Oracle's Lattice | Expert | Wiener's attack on RSA | 1000 |

### Programming

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 6 | The Guild Ledger | Beginner | CSV parsing + prime check | 100 |
| 7 | The Runic Vault | Easy | XOR brute-force (4-char key) | 250 |
| 8 | The Dungeon Cartographer | Medium | Dijkstra's shortest path | 400 |
| 9 | The Arcane Protocol | Hard | TCP + HMAC-SHA256 handshake | 600 |
| 10 | The Prophecy Engine | Expert | Black-box function reversal | 1000 |

### OSINT

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 11 | The Cartographer's Lost Map | Beginner | Reverse image search + geolocation | 100 |
| 12 | The Herald's Forgotten Broadcast | Easy | Username enumeration + git history | 150 |
| 13 | The Spy's Cipher Journal | Medium | EXIF metadata + Base64 + ROT13 | 200 |

### Reverse Engineering

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 14 | The Runecaster's Compiled Tome | Easy | Python bytecode decompilation | 250 |

### LLM Security

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 15 | The Enchanted Parrot | Beginner | Basic prompt injection | 50 |
| 16 | The Whispering Merchant | Easy | System prompt bypass | 100 |
| 17 | The Court Wizard's Familiar | Medium | Output filter bypass | 150 |
| 18 | The Oracle of Shadows | Hard | Input + output filter bypass | 200 |
| 19 | The Mindflayer's Sanctum | Expert | Multi-agent LLM bypass | 250 |

### The Wizards Games

| # | Challenge | Difficulty | Technique | Points |
|---|-----------|------------|-----------|--------|
| 20 | The Ogre's Audition | Hard | Web Speech API + source analysis | 600 |

## Folder Structure

```tree
fantasy_ctf_challs/
├── crypto/
│   ├── The-Scribes-Encoded-Scroll-Beginner/
│   ├── The-Goblin-Messengers-Cipher-Easy/
│   ├── The-Dragons-Sealed-Proclamation-Medium/
│   ├── The-Lichs-Cursed-Oracle-Hard/
│   └── The-Void-Oracles-Lattice-Expert/
├── osint/
│   ├── The-Cartographers-Lost-Map-Beginner/
│   ├── The-Heralds-Forgotten-Broadcast-Easy/
│   └── The-Spys-Cipher-Journal-Medium/
├── prog/
│   ├── The-Guild-Ledger-Beginner/
│   ├── The-Runic-Vault-Easy/
│   ├── The-Dungeon-Cartographer-Medium/
│   ├── The-Arcane-Protocol-Hard/
│   └── The-Prophecy-Engine-Expert/
├── rev/
│   └── The-Runecasters-Compiled-Tome-Easy/
├── llm/
│   ├── shared/                              (Gemini client, filters, rate limiter)
│   ├── The-Enchanted-Parrot-Beginner/
│   ├── The-Whispering-Merchant-Easy/
│   ├── The-Court-Wizards-Familiar-Medium/
│   ├── The-Oracle-of-Shadows-Hard/
│   └── The-Mindflayers-Sanctum-Expert/
└── misc/
    └── The-Ogres-Audition-Hard/
```

Each challenge folder contains:

- **`README.md`** — Lore, task description, given files, flag format
- **`challenge/`** — Player-facing files (no flags)
- **`solution/`** — Working solve script that recovers the flag
- **`ctfd_meta.json`** — CTFd import metadata (name, category, scoring, hints, flags)
- **`Dockerfile`** + **`docker-compose.yml`** — For network challenges (Hard/Expert) and all LLM challenges

## Scoring

All challenges use **dynamic scoring** — points decrease as more teams solve them.

| Difficulty | Initial | Minimum | Decay |
|------------|---------|---------|-------|
| Beginner | 100 | 30 | 30 |
| Easy | 250 | 30 | 30 |
| Medium | 400 | 30 | 30 |
| Hard | 600 | 30 | 30 |
| Expert | 1000 | 30 | 30 |

## Flag Format

All flags follow the format:

```bash
FantasyCTF{...}
```

Flag contents use partial l33t speak (e.g., `e→3`, `o→0`, `a→4`) for flavor.

## Deployment

### Static challenges (Beginner, Easy, Medium)

Upload the files from `challenge/` to CTFd. Import metadata from `ctfd_meta.json`.

### Network challenges (Hard, Expert)

```bash
cd crypto/The-Lichs-Cursed-Oracle-Hard
docker compose up -d
```

The flag is injected via the `FLAG` environment variable in `docker-compose.yml` — it is **not** hardcoded in the challenge source files.

### LLM challenges (all difficulties)

1. Copy `llm/.env.example` to `llm/.env` and paste your Gemini API key from [aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)
2. Run any challenge:

```bash
cd llm/The-Enchanted-Parrot-Beginner
docker compose up -d
```

LLM challenges use **Google Gemini 2.5 Flash** via the `google-genai` SDK. Each runs a FastAPI server in Docker with the flag injected via environment variable.

## Dependencies

Solve scripts may require:

- **Python 3.10+**
- **sympy** — RSA challenges
- **pwntools** — Network challenge solvers
- **pycryptodome** — AES/CBC challenge
- **requests** — LLM challenge solvers
- **uncompyle6** or **pycdc** — Rev challenge (Python bytecode decompilation)

Install with:

```bash
pip install sympy pwntools pycryptodome requests
```

## License

For educational use only. Built for ISSessions FantasyCTF.
