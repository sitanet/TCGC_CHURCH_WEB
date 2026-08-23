#!/usr/bin/env bash
# ==============================================================================
# THE CITYGATE CHURCH — PRODUCTION DEPLOY & RELEASE SCRIPT
# Executes on the DigitalOcean Droplet under user 'deploy'
# ==============================================================================

set -euo pipefail

PROJECT_DIR="/var/www/thecitygatechurch"
VENV_DIR="$PROJECT_DIR/.venv"

echo "================================================================="
echo "  STARTING CITYGATE CHURCH PRODUCTION RELEASE DEPLOYMENT"
echo "  Timestamp: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
echo "================================================================="

cd "$PROJECT_DIR"

# 1. Fetch latest code from Git
echo "[STEP 1/7] Pulling latest updates from git repository..."
git fetch origin main
git checkout main
git pull origin main

# 2. Setup / Update Virtual Environment
echo "[STEP 2/7] Checking Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

# 3. Install/Update Dependencies
echo "[STEP 3/7] Installing production requirements..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 4. Database Migrations
echo "[STEP 4/7] Applying PostgreSQL database migrations..."
python manage.py migrate --noinput

# 5. Collect Static Files
echo "[STEP 5/7] Collecting static assets..."
python manage.py collectstatic --noinput

# 6. Django Production Health & Integrity Check
echo "[STEP 6/7] Running Django deployment validation check..."
python manage.py check --deploy

# 7. Reload Gunicorn & Nginx
echo "[STEP 7/7] Reloading Gunicorn and Nginx..."
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl reload nginx

echo "================================================================="
echo "  DEPLOYMENT SUCCEEDED!"
echo "  Service Status:"
sudo systemctl status gunicorn --no-pager --lines=5
echo "================================================================="
