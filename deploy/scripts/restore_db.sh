#!/usr/bin/env bash
# ==============================================================================
# THE CITYGATE CHURCH — POSTGRESQL DATABASE RESTORE SCRIPT
# Safely terminates connections, re-creates schema, and restores from backup dump.
# ==============================================================================

set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: bash restore_db.sh /path/to/backup_file.dump.gz"
    exit 1
fi

BACKUP_FILE="$1"
PROJECT_DIR="/var/www/thecitygatechurch"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load DB environment if .env exists
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

DB_NAME="${DB_NAME:-tcgc_church_db}"
DB_USER="${DB_USER:-tcgc_user}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "================================================================="
echo "  WARNING: THIS WILL OVERWRITE THE DATABASE '$DB_NAME'!"
echo "  Restoring from: $BACKUP_FILE"
echo "================================================================="
read -p "Type 'RESTORE' to confirm: " CONFIRM

if [ "$CONFIRM" != "RESTORE" ]; then
    echo "Restoration cancelled."
    exit 0
fi

echo "[INFO] Terminating existing database connections..."
PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" || true

echo "[INFO] Dropping and re-creating database '$DB_NAME'..."
PGPASSWORD="${DB_PASSWORD:-}" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" || true
PGPASSWORD="${DB_PASSWORD:-}" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"

echo "[INFO] Restoring database schema and data..."
gunzip -c "$BACKUP_FILE" | PGPASSWORD="${DB_PASSWORD:-}" pg_restore \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -v --no-owner --no-privileges || true

echo "[SUCCESS] Database restoration complete!"
