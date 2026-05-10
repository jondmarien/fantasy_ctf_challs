#!/usr/bin/env bash
# CTFd production backup — runs as root via cron
# Dumps Postgres, archives CTFd uploads, snapshots both into restic

SECRETS_DIR=/opt/fantasy_ctf_challs/infra/secrets
STAGING=/var/backups/ctf-prod
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Load restic env
. "$SECRETS_DIR/restic.env"
export RESTIC_REPOSITORY RESTIC_PASSWORD

mkdir -p "$STAGING"

echo "[$(date)] Starting backup..."

# 1. Postgres dump
echo "[$(date)] Dumping Postgres..."
docker exec infra-db-1 pg_dump -U ctfd ctfd \
  | gzip > "$STAGING/ctfd-$TIMESTAMP.sql.gz"

# 2. CTFd uploads volume
echo "[$(date)] Archiving uploads volume..."
docker run --rm \
  -v infra_ctfd_uploads:/data:ro \
  -v "$STAGING":/backup \
  alpine tar -czf "/backup/uploads-$TIMESTAMP.tar.gz" -C /data .

# 3. Restic snapshot
echo "[$(date)] Running restic backup..."
restic backup "$STAGING"

# 4. Prune local staging files older than 2 days
find "$STAGING" -name "*.sql.gz" -o -name "*.tar.gz" \
  | xargs -r ls -t \
  | tail -n +7 \
  | xargs -r rm -f

# 5. Forget old restic snapshots — keep 7 daily, 4 weekly
restic forget --prune \
  --keep-daily 7 \
  --keep-weekly 4

echo "[$(date)] Backup complete."
