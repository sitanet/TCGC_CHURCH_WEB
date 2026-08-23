# THE CITYGATE CHURCH — DIGITAL PLATFORM

> **A premium, international-standard digital platform, content management system, and REST API for The CityGate Church.**

[![Django](https://img.shields.io/badge/Django-5.2+-092e20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15+-a30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-Droplet%20Ready-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)](https://www.digitalocean.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sitanet/TCGC_CHURCH_WEB.git)

---

## 🏛 Project Overview

The CityGate Church digital platform is engineered from the ground up to provide an **international-standard visual and operational experience**. It combines a modern, editorial public website with a powerful custom administrative dashboard (bypassing generic templates and standard Django admin), robust REST API endpoints, and a role-based access control architecture for pastoral and ministry staff.

### Core Architecture:
- **Web Frontend**: High-contrast editorial spiritual design tokens, responsive typography, HTML5 audio player with scrubber/speed controls, dynamic drawer navigation, and accessible keyboard focus.
- **Custom Administrative Dashboard**: 10 functional CMS modules across 25+ templates with dedicated role-based access control.
- **REST API (v1)**: Modular endpoints with standard pagination, universal search, live stream telemetry, and health check.
- **Database**: PostgreSQL with connection pooling (`CONN_MAX_AGE=600`).
- **Production Stack**: Nginx $\rightarrow$ Gunicorn $\rightarrow$ Django WSGI $\rightarrow$ PostgreSQL on an Ubuntu DigitalOcean Droplet.

---

## 📁 Repository Structure

```
church_web/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation & deployment manual
├── manage.py                 # Django management command utility
├── requirements.txt          # Production Python dependencies
├── config/                   # Core configuration & settings package
│   ├── __init__.py
│   ├── asgi.py               # ASGI async server gateway
│   ├── wsgi.py               # WSGI production server gateway
│   ├── urls.py               # Root URL router & /api/v1/ patterns
│   └── settings/
│       ├── __init__.py
│       ├── base.py           # Shared base settings & app definitions
│       ├── development.py    # Local development settings
│       └── production.py     # Hardened production settings (SSL, HSTS, Spaces, Logs)
├── deploy/                   # Production Deployment Assets
│   ├── nginx/
│   │   └── thecitygatechurch.conf # Production Nginx reverse proxy configuration
│   ├── systemd/
│   │   └── gunicorn.service  # Systemd daemon configuration
│   └── scripts/
│       ├── server_setup.sh   # Automated Ubuntu Droplet provisioning
│       ├── deploy.sh         # Release update automation script
│       ├── backup_db.sh      # Automated daily compressed pg_dump script
│       └── restore_db.sh     # Disaster recovery restore utility
├── apps/                     # Modular Django applications
│   ├── accounts/             # Custom User model, RBAC, profiles, auth views
│   ├── core/                 # Abstract models, validators, context processors, security tests
│   ├── dashboard/            # Custom Administrative Dashboard portal
│   ├── teachings/            # Sermons, sermon series, scripture references, media
│   ├── media_library/        # Central photo galleries, digital assets, document store
│   ├── people/               # Pastoral team, council members, department leaders
│   ├── ministries/           # Ministries, departments, volunteer registration
│   ├── events/               # Church calendar, special services, registrations
│   ├── conferences/          # Annual conventions, summits, session schedules
│   ├── publications/         # Devotionals, study guides, bulletins, PDF downloads
│   ├── articles/             # Editorial thought leadership, blog, categories
│   ├── announcements/        # Top notification banners, urgent alerts
│   ├── streaming/            # Live broadcast status, YouTube/RTMP channels
│   ├── search/               # Universal search across all content models
│   ├── analytics/            # Telemetry for page views, audio listens, downloads
│   └── website/              # Public-facing views (Home, About, Visit, Contact)
├── static/                   # Static design assets (CSS, JS, Fonts, Images)
├── templates/                # Reusable Django template hierarchy
└── media/                    # Local media uploads (when not using DO Spaces)
```

---

## 🌊 DigitalOcean Droplet Sizing & Resource Plan

### Recommended Production Configuration:
- **Baseline Tier (Launch / Moderate Traffic)**:
  - **Droplet Type**: Basic / Regular Intel or AMD Droplet
  - **Specs**: **2 vCPU / 2GB RAM / 50GB NVMe SSD** (\$12–\$18/month)
  - **Suitable For**: Django + Gunicorn (4 workers), PostgreSQL local instance, Nginx, SSL, static files, and moderate daily media caching.
- **Growth Tier (High Traffic / Large Event Broadcasts)**:
  - **Specs**: **4 vCPU / 8GB RAM / 160GB NVMe SSD** (\$48/month)
  - **When Required**: Concurrent Sunday live broadcast traffic exceeds 2,500 simultaneous visitors or database exceeds 20GB.
- **Media Storage Architecture Recommendation**:
  - **DigitalOcean Spaces (Object Storage)** (\$5/month for 250GB + CDN bandwidth) is **strongly recommended** for production media storage. Storing large audio sermons, videos, and PDF devotionals in Spaces keeps the Droplet root filesystem lean, decoupled, and simple to back up.

---

## 🚀 DigitalOcean Droplet Step-by-Step Deployment Manual

### 1. Droplet Creation & Initial SSH Access
1. Create an Ubuntu 22.04 LTS (or 24.04 LTS) Droplet in the DigitalOcean control panel.
2. Select your SSH key during creation (never use root passwords).
3. Connect via terminal:
   ```bash
   ssh root@<DROPLET_PUBLIC_IP>
   ```

---

### 2. Automated Server Provisioning
We provide an automated provisioning script in `deploy/scripts/server_setup.sh`:

```bash
# Clone the repository to temporary location or download setup script
git clone https://github.com/sitanet/TCGC_CHURCH_WEB.git /tmp/tcgc_init
bash /tmp/tcgc_init/deploy/scripts/server_setup.sh
```

**What this configures automatically:**
- System updates & security packages (`fail2ban`, `ufw`, `certbot`).
- Python 3.11+, `pip`, `venv`, `libpq-dev`, `postgresql`, `nginx`.
- Deployment user `deploy` and `/var/www/thecitygatechurch` directory structure.
- UFW Firewall: Open **22 (SSH)**, **80 (HTTP)**, **443 (HTTPS)**; blocks public access to **5432 (PostgreSQL)**.
- PostgreSQL database `tcgc_church_db` and user `tcgc_user` with a secure random password.

---

### 3. Deploy Application Code & Configure Environment
1. Switch to the non-root `deploy` user:
   ```bash
   sudo su - deploy
   ```
2. Clone the repository into `/var/www/thecitygatechurch`:
   ```bash
   git clone https://github.com/sitanet/TCGC_CHURCH_WEB.git /var/www/thecitygatechurch
   cd /var/www/thecitygatechurch
   ```
3. Create the production `.env` file:
   ```bash
   cp .env.example .env
   nano .env
   ```
   *Fill in `DJANGO_SECRET_KEY`, `DB_PASSWORD`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and SMTP credentials.*

---

### 4. Setup Python Environment & Run Database Migrations
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create the initial Super Administrator
python manage.py createsuperuser
```

---

### 5. Configure Gunicorn Systemd Daemon
1. Copy the systemd service unit:
   ```bash
   sudo cp /var/www/thecitygatechurch/deploy/systemd/gunicorn.service /etc/systemd/system/gunicorn.service
   ```
2. Enable and start Gunicorn:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable gunicorn
   sudo systemctl start gunicorn
   sudo systemctl status gunicorn
   ```

---

### 6. Configure Nginx Reverse Proxy
1. Copy the Nginx site configuration:
   ```bash
   sudo cp /var/www/thecitygatechurch/deploy/nginx/thecitygatechurch.conf /etc/nginx/sites-available/thecitygatechurch.conf
   sudo ln -s /etc/nginx/sites-available/thecitygatechurch.conf /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   ```
2. Test Nginx syntax:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

### 7. DigitalOcean DNS Records
In the DigitalOcean Networking $\rightarrow$ Domains dashboard:
- **A Record**: `@` $\rightarrow$ `<DROPLET_PUBLIC_IP>` (TTL: 300)
- **A Record**: `www` $\rightarrow$ `<DROPLET_PUBLIC_IP>` (TTL: 300)

---

### 8. Obtain Let's Encrypt SSL/TLS Certificate
Once DNS propagates to the Droplet IP:
```bash
sudo certbot --nginx -d thecitygatechurch.org -d www.thecitygatechurch.org
```
- Select automatic HTTP $\rightarrow$ HTTPS redirection.
- Test renewal timer:
  ```bash
  sudo certbot renew --dry-run
  ```

---

## 🗄️ PostgreSQL Backup Strategy & Disaster Recovery

### Automated Daily Backup via Cron
Add the backup job to `crontab -e`:
```bash
# Run PostgreSQL backup daily at 2:00 AM UTC
0 2 * * * /bin/bash /var/www/thecitygatechurch/deploy/scripts/backup_db.sh >> /var/log/citygate/backup.log 2>&1
```

### Manual Backup Command:
```bash
bash /var/www/thecitygatechurch/deploy/scripts/backup_db.sh
```

### Full Disaster Recovery Restore:
```bash
bash /var/www/thecitygatechurch/deploy/scripts/restore_db.sh /var/backups/citygate/tcgc_backup_YYYYMMDD_HHMMSS.dump.gz
```

---

## 🔄 Deployment Update & Release Procedure

To deploy updates to production safely without downtime:

```bash
sudo su - deploy
cd /var/www/thecitygatechurch
bash deploy/scripts/deploy.sh
```

**Script Workflow:**
1. `git pull origin main`
2. Activate `.venv` & `pip install -r requirements.txt`
3. `python manage.py migrate --noinput`
4. `python manage.py collectstatic --noinput`
5. `python manage.py check --deploy`
6. `sudo systemctl restart gunicorn`
7. Verify service status

---

## 📊 System Monitoring & Useful Commands

| Action | Command |
|---|---|
| **CPU & Memory** | `htop` or `free -m` |
| **Disk Space** | `df -h` |
| **Gunicorn Logs** | `sudo journalctl -u gunicorn -f -n 50` |
| **Nginx Access Logs** | `sudo tail -f /var/log/nginx/citygate_access.log` |
| **Nginx Error Logs** | `sudo tail -f /var/log/nginx/citygate_error.log` |
| **Application Security Logs** | `tail -f /var/www/thecitygatechurch/logs/security.log` |
| **Restart Gunicorn** | `sudo systemctl restart gunicorn` |
| **Reload Nginx** | `sudo systemctl reload nginx` |

---

## 🧪 Automated Test Suite

Run all 59 unit, integration, and security tests:

```powershell
python manage.py test apps.website.tests apps.dashboard.tests apps.accounts.tests apps.core.tests apps.core.tests_security
```

---

## 📄 License & Ownership

Proprietary property of **The CityGate Church**. All rights reserved.
