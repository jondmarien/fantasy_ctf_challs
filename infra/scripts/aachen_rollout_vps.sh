#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/fantasy_ctf_challs}"
BRANCH="${1:-feat/hosting}"

echo "[aachen-rollout] repo=${REPO_DIR} branch=${BRANCH}"

cd "${REPO_DIR}"
git fetch origin
git checkout "${BRANCH}"
git pull origin "${BRANCH}"

cd infra
docker compose -f docker-compose.prod.yml restart ctfd

echo "[aachen-rollout] waiting for CTFd startup..."
sleep 5

docker compose -f docker-compose.prod.yml ps ctfd
docker compose -f docker-compose.prod.yml exec -T ctfd curl -sf http://localhost:8000/healthcheck >/dev/null

echo "[aachen-rollout] complete"
