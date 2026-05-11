# FantasyCTF Development Guide

This document covers day-to-day contributor workflows for `fantasy_ctf_challs`.

For project overview and challenge catalog, use [`README.md`](./README.md).

## Prerequisites

- Git
- Docker + Docker Compose plugin
- Python 3.10+ (3.12 recommended for parity with containerized challenge services)

Optional but useful:

- `nc`/`ncat` for TCP challenge smoke tests
- `jq` for inspecting JSON outputs

## Quick Start

1. Clone and enter the repository.
2. Choose one challenge you want to work on.
3. Run either static validation (file/solver checks) or the Dockerized service for that challenge.

```bash
git clone https://github.com/jondmarien/fantasy_ctf_challs.git
cd fantasy_ctf_challs
```

## Repository Conventions

Each challenge directory should keep this structure:

- `README.md` (player-facing prompt and context)
- `challenge/` (files given to players; no real flags)
- `solution/` (internal solve scripts/writeups)
- `ctfd_meta.json` (CTFd import metadata)
- optional `Dockerfile` + `docker-compose.yml` for hosted services

## Working on Static Challenges

Static challenges are usually Beginner/Easy/Medium style content.

Typical local validation loop:

1. Update challenge files in `challenge/`.
2. Run or adjust the solver in `solution/`.
3. Ensure `ctfd_meta.json` still matches names/category/points/flag pattern.

If your solver needs dependencies, install them in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On PowerShell: .venv\Scripts\Activate.ps1
pip install sympy pwntools pycryptodome requests
```

## Working on Dockerized Network Challenges

For challenge folders that include `docker-compose.yml`:

```bash
cd "<category>/<challenge-folder>"
docker compose up --build -d
docker compose logs -f
```

Then test connectivity with solver scripts or a socket client, and tear down:

```bash
docker compose down
```

### Flag Safety Rule

- Keep real flags out of source files.
- Inject via environment variables in compose or runtime secrets.
- Placeholder flags in local files are acceptable for development only.

## Advanced Programming Bundle

`prog/` includes a consolidated advanced server (`prog/server.py`) that hosts:

- Chronomancer's Gauntlet
- Abyssal Architect

Run it with:

```bash
cd prog
docker compose up --build -d
```

The bundled service exposes a single menu-driven TCP endpoint and uses:

- `FLAG_CHRONOMANCER`
- `FLAG_ARCHITECT`

## LLM Challenge Development

LLM challenge services live under `llm/`.

Per current config, challenges call an internal LiteLLM base URL and expect challenge-local environment configuration.

Start one challenge:

```bash
cd llm/The-Enchanted-Parrot-Beginner
docker compose up --build -d
```

Note:

- `llm/.env.example` currently documents player-provided API key behavior.
- Production orchestration and LiteLLM wiring are managed through the infra stack and deployment playbooks, not per-challenge local docker compose alone.

## Infra + Production Operations

Operational infrastructure work belongs in:

- `infra/` for deployment assets
- `docs/plans/HOSTING_PLAN_V3.md`
- `docs/plans/VPS_OPERATIONS.md`
- `docs/plans/EXECUTION_PLAYBOOK.md`

Use those docs for:

- Traefik/CTFd/Postgres/Redis/LiteLLM stack actions
- VPS bootstrap and secrets handling
- plugin installation and ops runbooks
- backup/restore procedures

## Documentation Update Checklist

When editing or adding a challenge, update:

1. challenge `README.md`
2. `solution/` artifacts
3. `ctfd_meta.json`
4. root `README.md` challenge catalog if the public set changed
5. relevant infra/docs plan files if deployment behavior changed

## Common Pitfalls

- Port collisions when running multiple compose projects locally
- stale containers from previous challenge runs (`docker ps -a`)
- accidentally committing sensitive values in compose/env files
- mismatch between challenge name in folder, `README.md`, and `ctfd_meta.json`

## Suggested Verification Before PR

- Solver works from a clean state
- Dockerized challenge starts and responds
- `ctfd_meta.json` remains valid JSON
- Any changed docs still match actual ports/env vars/paths
