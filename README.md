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
│   ├── core/                 # Abstract models (SEO, Slugged, Publishable), context processors
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
│   │   ├── public.js         # Public interactions & sticky navigation
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
| `DJANGO_DEBUG` | Enable debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of valid hosts | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database backend engine | `django.db.backends.postgresql` |
| `DB_NAME` | PostgreSQL database name | `tcgc_church_db` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `USE_SQLITE` | Set to `True` for instant zero-dependency local testing | `False` |
| `CHURCH_NAME` | Official Church Name | `The CityGate Church` |
| `USE_S3_STORAGE` | Enable AWS S3 / Cloudflare R2 storage | `False` |

---

## 🚀 Quickstart & Development Setup

### 1. Create and Activate Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create an Administrator Account

```bash
python manage.py createsuperuser
```

### 5. Launch the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Public Website:** `http://127.0.0.1:8000/`
- **Staff Administration Portal:** `http://127.0.0.1:8000/dashboard/`
- **Staff Login:** `http://127.0.0.1:8000/accounts/login/`
- **REST API Root (v1):** `http://127.0.0.1:8000/api/v1/`
- **API Health Check:** `http://127.0.0.1:8000/api/v1/health/`

---

## 🛡️ Role-Based Access Control (RBAC)

The custom `accounts.User` model provides 7 distinct roles:

1. **`super_admin`**: Full platform oversight, configuration, and security settings.
2. **`admin`**: Platform operations, staff account provisioning, and general management.
3. **`pastor_staff`**: Sermon teachings, sermon series, scripture references, and devotional publication.
4. **`content_manager`**: Editorial articles, announcements, news, and public page copy.
5. **`media_lead`**: Media asset bank, photo galleries, and live stream broadcast switches.
6. **`event_coordinator`**: Calendar management, conference setups, and attendee registrations.
7. **`member`**: Registered member / volunteer user.

---

## 📡 REST API (v1) Endpoints Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/` | `GET` | API Root and documentation index |
| `/api/v1/health/` | `GET` | Service health status and version info |
| `/api/v1/auth/user/` | `GET` | Current authenticated user profile |
| `/api/v1/teachings/api/sermons/` | `GET` | Paginated list of published sermons |
| `/api/v1/teachings/api/series/` | `GET` | Sermon series index |
| `/api/v1/media/api/galleries/` | `GET` | Photo galleries and albums |
| `/api/v1/people/api/people/` | `GET` | Pastoral staff and leadership directory |
| `/api/v1/ministries/api/ministries/` | `GET` | Ministries and community groups |
| `/api/v1/events/api/events/` | `GET` | Church calendar and special services |
| `/api/v1/conferences/api/conferences/` | `GET` | Major annual conferences and summits |
| `/api/v1/publications/api/publications/` | `GET` | Downloadable study materials and PDFs |
| `/api/v1/articles/api/articles/` | `GET` | Editorial articles and blog posts |
| `/api/v1/announcements/api/announcements/`| `GET` | Active church announcements and alerts |
| `/api/v1/streaming/api/status/` | `GET` | Real-time live stream broadcast status |
| `/api/v1/search/api/query/?q=` | `GET` | Universal search across all content models |
| `/api/v1/analytics/api/record/play/` | `POST` | Telemetry endpoint for sermon audio plays |
| `/api/v1/analytics/api/record/download/` | `POST` | Telemetry endpoint for resource downloads |

---

## 🎨 UI/UX Design System Tokens

The custom CSS architecture is built around CSS custom properties defined in `static/css/variables.css`:

- **Slate Obsidian (`--color-slate-900: #0B131F`)**: Depth, reverence, and grounding.
- **Divine Gold (`--color-gold-500: #C5A059`)**: Heavenly light, royalty, and warm accents.
- **Warm Ivory (`--color-warm-bg: #FAF8F5`)**: Organic paper-like feel, comfortable reading contrast.
- **Typography**: `Cinzel` / `Playfair Display` serif headings paired with clean, accessible `Plus Jakarta Sans` body copy.

---

## 🔄 Git Repository

- **GitHub Remote:** `https://github.com/sitanet/TCGC_CHURCH_WEB.git`

```bash
git remote add origin https://github.com/sitanet/TCGC_CHURCH_WEB.git
git branch -M main
git add .
git commit -m "feat: initial foundation for The CityGate Church digital platform"
```

---

## 📄 License & Ownership

Proprietary property of **The CityGate Church**. All rights reserved.
