# Infrastructure

Infrastructure assets for the FantasyCTF VPS deployment live in this directory.
These files are intended for Hetzner-hosted Docker Compose operations.

Secrets are never committed to git. Runtime secrets belong on the VPS only
under `infra/secrets/` (for example `infra/secrets/.env.prod`).
