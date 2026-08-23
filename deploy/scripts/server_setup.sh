#!/usr/bin/env bash
# ==============================================================================
# THE CITYGATE CHURCH — DIGITALOCEAN UBUNTU SERVER PROVISIONING SCRIPT
# OS: Ubuntu 22.04 LTS or 24.04 LTS
# Target: DigitalOcean Droplet
# ==============================================================================

set -euo pipefail

echo "================================================================="
echo "  PROVISIONING THE CITYGATE CHURCH DIGITALOCEAN SERVER"
echo "================================================================="

# 1. Update system packages
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get upgrade -y

# 2. Install core runtime, build, and server packages
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    ufw \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    curl \
    htop \
    unzip

# 3. Create non-root deployment user
if id "deploy" &>/dev/null; then
    echo "[INFO] User 'deploy' already exists."
else
    echo "[INFO] Creating deployment user 'deploy'..."
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
    usermod -aG www-data deploy
fi

# 4. Setup Project Directory Structure
PROJECT_DIR="/var/www/thecitygatechurch"
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/staticfiles"
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p /var/log/gunicorn
mkdir -p /var/backups/citygate

chown -R deploy:www-data "$PROJECT_DIR"
chown -R deploy:www-data /var/log/gunicorn
chown -R deploy:www-data /var/backups/citygate
chmod -R 775 "$PROJECT_DIR/media"
chmod -R 775 "$PROJECT_DIR/staticfiles"
chmod -R 775 "$PROJECT_DIR/logs"

# 5. Configure UFW Firewall
echo "[INFO] Configuring UFW Firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
# Explicitly ensure PostgreSQL is NOT exposed to public internet
ufw deny 5432/tcp comment 'PostgreSQL Internal Only'
echo "y" | ufw enable

# 6. Setup PostgreSQL Database & User
DB_NAME="tcgc_church_db"
DB_USER="tcgc_user"
DB_PASS=$(openssl rand -base64 24)

echo "[INFO] Configuring PostgreSQL..."
sudo -u postgres psql -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$DB_USER') THEN CREATE USER $DB_USER WITH PASSWORD '$DB_PASS'; END IF; END \$\$;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"

echo "-----------------------------------------------------------------"
echo "  POSTGRESQL CREDENTIALS GENERATED (SAVE THESE IN YOUR .env):"
echo "  Database: $DB_NAME"
echo "  User:     $DB_USER"
echo "  Password: $DB_PASS"
echo "-----------------------------------------------------------------"

# 7. Configure Fail2Ban for SSH protection
systemctl enable fail2ban
systemctl start fail2ban

echo "================================================================="
echo "  SERVER PROVISIONING COMPLETE!"
echo "  Next steps:"
echo "  1. Switch to user 'deploy': sudo su - deploy"
echo "  2. Clone repository to $PROJECT_DIR"
echo "  3. Create $PROJECT_DIR/.env with production credentials"
echo "  4. Run deploy script: bash $PROJECT_DIR/deploy/scripts/deploy.sh"
echo "================================================================="
