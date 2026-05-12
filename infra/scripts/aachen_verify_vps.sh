#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/fantasy_ctf_challs}"
PLUGIN_DIR="${REPO_DIR}/infra/ctfd/plugins/dynamic_challenges_aachen"

echo "[aachen-verify] repo=${REPO_DIR}"

if [[ ! -d "${PLUGIN_DIR}" ]]; then
  echo "[aachen-verify] missing plugin directory: ${PLUGIN_DIR}" >&2
  exit 1
fi

cd "${REPO_DIR}/infra"

echo "[aachen-verify] checking registration log line..."
if ! docker compose -f docker-compose.prod.yml logs ctfd --tail=300 2>&1 | grep -q "dynamic_challenges_aachen"; then
  echo "[aachen-verify] registration log not found in recent ctfd logs" >&2
  exit 1
fi

echo "[aachen-verify] checking runtime decay registry..."
docker compose -f docker-compose.prod.yml exec -T ctfd python - <<'PY'
from CTFd.plugins.dynamic_challenges.decay import DECAY_FUNCTIONS

if "aachen" not in DECAY_FUNCTIONS:
    raise SystemExit("aachen not registered in DECAY_FUNCTIONS")

print("Registered decay functions:", sorted(DECAY_FUNCTIONS.keys()))
print("aachen function:", DECAY_FUNCTIONS["aachen"])
PY

echo "[aachen-verify] complete"
