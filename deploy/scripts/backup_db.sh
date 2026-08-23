#!/usr/bin/env bash
# ==============================================================================
# THE CITYGATE CHURCH — POSTGRESQL AUTOMATED BACKUP SCRIPT
# Performs compressed pg_dump, enforces 30-day retention, and optionally
# syncs off-site to DigitalOcean Spaces / S3.
# ==============================================================================

set -euo pipefail

# Configuration
BACKUP_DIR="/var/backups/citygate"
PROJECT_DIR="/var/www/thecitygatechurch"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/tcgc_backup_${TIMESTAMP}.dump.gz"

# Load DB environment if .env exists
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

DB_NAME="${DB_NAME:-tcgc_church_db}"
DB_USER="${DB_USER:-tcgc_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

mkdir -p "$BACKUP_DIR"

echo "[INFO] Starting database backup for '$DB_NAME' at $(date)..."

# Execute pg_dump with custom compressed archive format
PGPASSWORD="${DB_PASSWORD:-}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F c \
    -b \
    -v | gzip > "$BACKUP_FILE"

FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[SUCCESS] Backup created successfully: $BACKUP_FILE (Size: $FILE_SIZE)"

# Retain backups for 30 days locally (purge older dumps)
echo "[INFO] Pruning local backups older than 30 days..."
find "$BACKUP_DIR" -type f -name "tcgc_backup_*.dump.gz" -mtime +30 -exec rm {} \;

# Optional: Off-site sync to DigitalOcean Spaces / S3 if s3cmd or aws-cli is configured
if command -v s3cmd &> /dev/null && [ -n "${DO_SPACES_BUCKET:-}" ]; then
    echo "[INFO] Syncing backup to DigitalOcean Spaces: s3://${DO_SPACES_BUCKET}/backups/..."
    s3cmd put "$BACKUP_FILE" "s3://${DO_SPACES_BUCKET}/backups/"
    echo "[SUCCESS] Off-site backup complete."
fi

echo "[INFO] Backup procedure finished cleanly at $(date)."
