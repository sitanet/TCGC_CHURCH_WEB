# THE CITYGATE CHURCH — DIGITAL PLATFORM

> **A premium, international-standard digital platform, content management system, and REST API for The CityGate Church.**

[![Django](https://img.shields.io/badge/Django-5.2+-092e20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15+-a30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sitanet/TCGC_CHURCH_WEB.git)

---

## 🏛 Project Overview

The CityGate Church digital platform is engineered from the ground up to provide an **international-standard visual and operational experience**. It combines a modern, editorial public website with a powerful custom administrative dashboard (bypassing generic templates and standard Django admin), robust REST API endpoints, and a role-based access control architecture for pastoral and ministry staff.

### Core Pillars:
1. **Editorial Luxury & Spiritual Modernism**: Custom design tokens, warm gold accents (`#C5A059`), deep obsidian/slate (`#0B131F`), warm ivory backgrounds (`#FAF8F5`), and refined typography.
2. **Custom Administrative Dashboard**: Built specifically for church operations (teachings, events, media, publications, streaming, and announcements) without relying on the default Django admin.
3. **Pluggable Architecture**: 14+ modular Django applications structured within an `apps/` namespace.
4. **DRF API Foundation (`/api/v1/`)**: Standardized pagination, unified search, live stream telemetry, and health check endpoints.
5. **Role-Based Access Control (RBAC)**: Custom `User` model with 7 granular staff and member permission levels.
6. **Enterprise Storage**: Modular upload partitioning designed to transition to AWS S3, Cloudflare R2, or MinIO.

---

## 📁 Repository Structure

```
church_web/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation & developer manual
├── manage.py                 # Django management command utility
├── requirements.txt          # Python dependencies
├── config/                   # Core configuration & settings package
│   ├── __init__.py
│   ├── asgi.py               # ASGI async server gateway
│   ├── wsgi.py               # WSGI production server gateway
│   ├── urls.py               # Root URL router & /api/v1/ patterns
│   └── settings/
│       ├── __init__.py
│       ├── base.py           # Shared settings & app definitions
│       ├── development.py    # Local development & PostgreSQL/SQLite toggle
│       └── production.py     # Production security & Cloud storage
├── apps/                     # Modular Django applications
│   ├── accounts/             # Custom User model, RBAC, profiles, auth views
│   ├── core/                 # Abstract models, validators, context processors
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
├── static/                   # Static design assets
│   ├── css/
│   │   ├── variables.css     # Design tokens (Spiritual luxury palette, fonts, spacing)
│   │   ├── reset.css         # Modern reset & baseline styles
│   │   ├── typography.css    # Serif display & sans body scale
│   │   ├── public.css        # Public website stylesheet
│   │   ├── dashboard.css     # Custom administrative portal stylesheet
│   │   └── components/       # Buttons, forms, cards, modals, alerts, badges, states
│   ├── js/
│   │   ├── core.js           # Toast notifications, modal controller, CSRF fetch client
│   │   ├── public.js         # Audio scrubbing, transcript scaler, search modal, drawer
│   │   └── dashboard.js      # Dashboard sidebar & action confirmations
│   └── img/                  # Logos and placeholder graphics
├── templates/                # Reusable Django template hierarchy
│   ├── base.html             # Public base layout
│   ├── components/           # Partials: header, footer, alerts, empty_state, modal
│   ├── website/              # Public pages: index, about, visit, contact
│   ├── accounts/             # Login, profile, password reset templates
│   ├── dashboard/            # Custom Admin portal base & overview
│   └── errors/               # 400, 403, 404, 500 error pages
└── media/                    # Partitioned local file uploads (in development)
```

---

## ⚙️ Environment Configuration

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

### Key Configuration Variables:

| Variable | Description | Default / Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Unique Django cryptographic secret key | *Change in production* |
| `DJANGO_DEBUG` | Enable debug mode (`False` in production) | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of valid domains | `thecitygatechurch.org,www.thecitygatechurch.org` |
| `DJANGO_SETTINGS_MODULE` | Active settings module | `config.settings.production` |
| `DB_ENGINE` | Database backend engine | `django.db.backends.postgresql` |
| `DB_NAME` | PostgreSQL database name | `tcgc_church_db` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `[SECURE_DB_PASSWORD]` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `CHURCH_NAME` | Official Church Name | `The CityGate Church` |
| `USE_S3_STORAGE` | Enable AWS S3 / Cloudflare R2 storage | `False` |

---

## 🛡️ Role-Based Access Control (RBAC)

The custom `accounts.User` model provides 7 distinct roles:

1. **`super_admin`**: Full platform oversight, configuration, and security settings.
2. **`admin`**: Platform operations, staff account provisioning, and general management.
3. **`pastor_staff`**: Sermon teachings, sermon series, confidential prayer requests, and pastoral contact inboxes.
4. **`content_manager`**: Editorial articles, announcements, news, and public page copy.
5. **`media_lead`**: Media asset bank, photo galleries, and live stream broadcast switches.
6. **`event_coordinator`**: Calendar management, conference setups, and attendee registrations.
7. **`member`**: Registered member / volunteer user.

---

## 🔒 Security & Hardening Architecture

1. **Confidentiality Isolation**: Pastoral prayer requests and contact messages are strictly restricted to `super_admin`, `admin`, and `pastor_staff` roles.
2. **File Upload Safety**: Strict whitelists for extensions (`.jpg`, `.png`, `.webp`, `.pdf`, `.docx`, `.mp3`, `.m4a`, `.mp4`), hard size limits ($5\text{MB}$ images, $30\text{MB}$ PDFs, $100\text{MB}$ audio, $500\text{MB}$ video), forbidden executable blocking (`.exe`, `.php`, `.sh`, `.py`, `.js`), and path traversal sanitization.
3. **Anti-Spam & Honeypot Defense**: Public contact, prayer request, newsletter, and event registration forms use hidden honeypots (`hp_website`) to silently drop automated spam bots.
4. **HTTPS & Cookie Security**: `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `CSRF_COOKIE_SECURE = True`, `SameSite = "Lax"`, `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`, and `HSTS` enabled.
5. **Atomic Telemetry Operations**: Resource download and sermon play counters use atomic `F("field") + 1` expressions to eliminate race conditions.
6. **Draft Content Isolation**: Public searches, teachings, events, articles, and XML sitemaps strictly filter on `PublishableStatus.PUBLISHED`.

---

## 🚀 Production Deployment Manual

### 1. System Requirements
- Ubuntu 22.04 LTS or Debian 12
- Python 3.11+
- PostgreSQL 15+
- Nginx
- Gunicorn

### 2. Nginx Reverse Proxy Configuration Template (`/etc/nginx/sites-available/citygate`)

```nginx
upstream citygate_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name thecitygatechurch.org www.thecitygatechurch.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name thecitygatechurch.org www.thecitygatechurch.org;

    ssl_certificate /etc/letsencrypt/live/thecitygatechurch.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thecitygatechurch.org/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;

    # Static Assets
    location /static/ {
        alias /var/www/citygate/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    # Media Uploads
    location /media/ {
        alias /var/www/citygate/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }

    # Application Gateway
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://citygate_app;
    }
}
```

### 3. Gunicorn Systemd Service Unit (`/etc/systemd/system/citygate.service`)

```ini
[Unit]
Description=Gunicorn instance to serve The CityGate Church Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/citygate
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/var/www/citygate/.venv/bin/gunicorn \
          --workers 4 \
          --bind 127.0.0.1:8000 \
          --timeout 60 \
          --access-logfile /var/log/citygate/gunicorn_access.log \
          --error-logfile /var/log/citygate/gunicorn_error.log \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

---

## 🗄️ Database Backup & Disaster Recovery

### Automated PostgreSQL Daily Backup Script (`/usr/local/bin/citygate_backup.sh`)

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/citygate"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# PostgreSQL Dump
pg_dump -U postgres -h localhost -d tcgc_church_db -F c -b -v -f "$BACKUP_DIR/tcgc_db_$TIMESTAMP.dump"

# Retain backups for 30 days
find $BACKUP_DIR -type f -name "*.dump" -mtime +30 -exec rm {} \;
```

### Database Restore Procedure

```bash
# 1. Terminate existing connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'tcgc_church_db';"

# 2. Re-create clean database
dropdb -U postgres tcgc_church_db
createdb -U postgres -O postgres tcgc_church_db

# 3. Restore from binary dump
pg_restore -U postgres -h localhost -d tcgc_church_db -v /var/backups/citygate/tcgc_db_2026XXXX_XXXXXX.dump
```

---

## 🧪 Automated Testing Suite

Run the full automated test suite (59 test cases covering web routes, CMS modules, RBAC, file safety, and anti-spam):

```powershell
python manage.py test apps.website.tests apps.dashboard.tests apps.accounts.tests apps.core.tests apps.core.tests_security
```

---

## 📄 License & Ownership

Proprietary property of **The CityGate Church**. All rights reserved.
