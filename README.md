# 🚀 ProjectsHub — AI Projects, Workshops & Enterprise Services Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%20LTS-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tests](https://img.shields.io/badge/Tests-21%20Passed-success.svg)](#testing--verification)
[![License](https://img.shields.io/badge/License-Proprietary-orange.svg)](#)

> **From Ideas to AI-Powered Products**  
> ProjectsHub is a production-ready, full-stack Django platform bridging academic engineering and enterprise innovation. It provides students and engineers with real-world AI/ML blueprints, source code, and hands-on bootcamps, while delivering custom AI development, intelligent workflow automation, and systems integration for businesses.

---

## 📑 Table of Contents

- [Platform Overview](#-platform-overview)
- [Key Features](#-key-features)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Directory Structure](#-directory-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
- [URL Routing & API Reference](#-url-routing--api-reference)
  - [Public Pages](#public-pages)
  - [Interactive Form Endpoints](#interactive-form-endpoints)
  - [REST / JSON APIs](#rest--json-apis)
  - [SEO & Legal](#seo--legal)
- [Custom Admin & Lead Management](#-custom-admin--lead-management)
- [Management Commands & Auditing Suite](#-management-commands--auditing-suite)
- [Testing & Verification](#-testing--verification)
- [Deployment & Production Readiness](#-deployment--production-readiness)

---

## 🌟 Platform Overview

ProjectsHub serves two primary ecosystems:

1. **Students, Researchers & Engineers**:
   - Access verified, end-to-end AI/ML and full-stack project blueprints with architecture diagrams, phase timelines, tech stack breakdowns, and source code.
   - Structured 3-Day AI Bootcamp with day-by-day lesson roadmaps and instant seat enrollment.
   - Curated directory of free and freemium AI development tools.
   - Interactive AI Roadmap visual guide for continuous learning.

2. **Startups & Enterprises**:
   - High-impact AI Development (custom LLMs, computer vision, predictive modeling).
   - Intelligent AI Automation (RAG workflows, CRM integrations, document processing).
   - Systems Integration (enterprise API orchestrations, vector databases, cloud pipelines).
   - Case studies with quantitative ROI benchmarks and technical implementation details.

---

## ✨ Key Features

- **Dynamic CMS & Site Configuration**: Manage site settings, hero copy, social links, stats, and multi-tier navigation menus directly from the Django admin.
- **Rich Project Showcase**: Dynamic filtering by category and technology, featured highlights, system architecture diagrams, and chronological build phases.
- **3-Day Workshop Engine**: Day-specific curriculum pages, syllabus breakdowns, prerequisite checklists, and automated enrollment capture.
- **Lead Capture & Lightweight CRM**: Form triage for general contact inquiries, gated project downloads, AI project ideas, and workshop applicants.
- **Integrated Anti-Bot Protection**: Cryptographically signed dynamic math CAPTCHA (`/api/captcha/`) ensuring clean lead acquisition without third-party tracking scripts.
- **SEO & Search Dominance**: Fully dynamic `sitemap.xml`, customizable `robots.txt`, HTML sitemap, structured JSON-LD schemas, and OpenGraph/Twitter card tags.
- **Dynamic 301/302 Redirect Engine**: Database-backed URL redirect manager with active toggle and HTTP status code selection.
- **Production Hardened**: Pre-configured security headers (nosniff, referrer-policy, permissions-policy), GZip compression, local-memory caching, and cPanel/Passenger WSGI compatibility.

---

## 🛠 Architecture & Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Backend Framework** | Django 4.2 LTS (Python 3.10+) | MVT architecture, ORM, custom middleware |
| **Database** | SQLite3 (Development) / PostgreSQL (Production) | Automatic failover via `DATABASE_URL` |
| **Frontend Styling** | Vanilla CSS3 + Modern Design System | Glassmorphism, CSS variables, dark/light themes, animations |
| **Client-side Interactivity** | Vanilla JavaScript (ES6+) | Dynamic modals, AJAX forms, chatbot widget, tabbed filters |
| **Caching** | Django LocMemCache | Low-latency in-memory caching |
| **WSGI / Hosting** | WSGI / Passenger | `passenger_wsgi.py` for cPanel / Apache / Nginx |

---

## 📂 Directory Structure

```plaintext
projectsHub/
│
├── core/                           # Primary application module
│   ├── management/commands/        # Custom CLI commands (seeding, SEO, audits)
│   ├── migrations/                 # Database schema migrations
│   ├── tests/                      # Automated test suite (21 unit & view tests)
│   ├── admin.py                    # Advanced admin dashboard, inlines & CSV exports
│   ├── context_processors.py       # Global site settings, metrics & telemetry
│   ├── middleware.py               # Security headers & dynamic redirect engine
│   ├── models.py                   # 30+ relational models (Projects, CRM, Blogs, etc.)
│   ├── urls.py                     # Route declarations for core views and APIs
│   └── views.py                    # Page controllers, form handlers & JSON endpoints
│
├── projectshub/                    # Django project configuration
│   ├── settings.py                 # Core settings, database switch & middleware stack
│   ├── urls.py                     # Root URL router & media/static fallbacks
│   └── wsgi.py                     # Standard WSGI entrypoint
│
├── static/                         # Static assets
│   ├── css/                        # Modular stylesheets (blog, roadmap, project, etc.)
│   ├── js/                         # Client scripts (ai-chatbot.js, idea-modal.js, etc.)
│   └── images/                     # Static diagrams, badges, and brand assets
│
├── templates/                      # HTML5 Django templates
│   ├── admin/                      # Custom admin dashboard & telemetry templates
│   ├── components/                 # Reusable UI partials (navbar, footer, modals)
│   └── core/                       # 25+ responsive view templates (index, blog, etc.)
│
├── media/                          # User-uploaded content (project images, logos)
├── passenger_wsgi.py               # Passenger deployment hook for cPanel/Apache
├── requirements.txt                # Python package dependencies
├── manage.py                       # Django CLI management utility
└── README.md                       # Platform documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10** or higher
- **pip** (Python package manager)
- **Virtualenv** (recommended)

### Installation & Setup

1. **Clone the repository and enter directory**:
   ```bash
   cd projectsHub
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Populate initial data (Projects, Tools, Blogs, Services, FAQs)**:
   ```bash
   python manage.py seed_data
   ```

6. **Create an administrative superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the local development server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to view the site, or [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) for the control dashboard.

---

## 🗺 URL Routing & API Reference

### Public Pages

| URL Pattern | View Name | Description |
|---|---|---|
| `/` | `index` | Landing page with featured projects, tools, services, and stats |
| `/projects/` | `projects` | Full searchable and filterable project catalog |
| `/projects/<slug>/` | `project_detail_slug` | Detailed project case breakdown with diagrams and timeline |
| `/workshop/` | `workshop` | 3-Day AI Bootcamp overview and curriculum |
| `/workshop/<id>/day/<day>/` | `workshop_day_detail` | Day-specific syllabus, hands-on goals, and prerequisites |
| `/tools/` | `tools` | Curated AI tools directory with category filters |
| `/ai-roadmap/` | `ai_roadmap` | Interactive step-by-step AI learning & implementation roadmap |
| `/services/ai-development/` | `ai_development` | Custom AI modeling & deep learning services |
| `/services/ai-automation/` | `ai_automation` | Intelligent workflow & business process automation |
| `/services/ai-integration/` | `ai_integration` | Enterprise systems integration & LLM pipeline orchestration |
| `/case-studies/` | `case_studies` | Client success stories with quantitative performance metrics |
| `/industries/` | `industries` | Vertical-specific AI solutions (Healthcare, Finance, E-commerce) |
| `/blog/` | `blog` | Engineering and AI industry articles |
| `/blog/<slug>/` | `blog_detail` | Blog article view with code snippets and author bio |

### Interactive Form Endpoints

All form endpoints accept POST requests, enforce CSRF validation, log client IP, and support dynamic CAPTCHA validation:

| Endpoint | Method | Purpose | Captured Model |
|---|---|---|---|
| `/contact/` | `POST` | General inquiries and partnership requests | `ContactInquiry` / `ContactMessage` |
| `/gate/` | `POST` | Gated project lead capture (source code downloads) | `ProjectGateLead` |
| `/idea/` | `POST` | Custom AI project submission modal | `IdeaSubmission` |
| `/enroll/` | `POST` | Student workshop registration | `WorkshopEnrollment` |

### REST / JSON APIs

| Endpoint | Method | Description |
|---|---|---|
| `/api/captcha/` | `GET` | Generates a signed, single-use dynamic math challenge |
| `/api/projects/` | `GET` | Filtered list of projects by category or search term |
| `/api/pricing/` | `GET` | Pricing plans and feature checklists |
| `/api/workshops/` | `GET` | Active workshops and day breakdown payloads |
| `/api/blog/` | `GET` | Paginated blog posts filtered by tag or category |

### SEO & Legal

| Endpoint | View Name | Description |
|---|---|---|
| `/robots.txt` | `robots_txt` | Search engine crawl rules referencing the sitemap |
| `/sitemap.xml` | `sitemap_xml` | Dynamic XML sitemap covering all active pages and slugs |
| `/sitemap/` | `html_sitemap` | User-facing HTML sitemap with hierarchical links |
| `/terms/` | `terms` | Terms of Service |
| `/privacy/` | `privacy` | Privacy Policy |
| `/refund/` | `refund` | Refund & Cancellation Policy |

---

## 📊 Custom Admin & Lead Management

The Django Admin (`/admin/`) has been heavily tailored for business operations:

- **Executive KPI Dashboard**: Instant aggregation of active projects, leads, ideas, enrollments, published blogs, and live server telemetry (Python version, Django version, active DB engine, cache status).
- **Badge Counters in Navigation**: Real-time count badges beside every model in the admin navigation sidebar.
- **One-Click CSV Exports**: Export contact inquiries, project gate leads, and workshop enrollments directly to CSV for CRM ingestion.
- **Inline Editors**: Manage project images, architectural diagrams, chronological phases, and service features directly inside their parent model's page.
- **Direct Filtering & Search**: Filter leads by status (`new`, `contacted`, `converted`, `spam`), date ranges, or keyword searches.

---

## 🧰 Management Commands & Auditing Suite

The project includes specialized management commands located in `core/management/commands/`:

```bash
# Seed initial rich demo data (projects, categories, tools, services, FAQs, etc.)
python manage.py seed_data

# Bulk import projects from structured definitions
python manage.py import_projects

# Run an automated link audit across all internal and external anchors
python manage.py audit_links

# Audit content quality, word counts, and header hierarchy
python manage.py audit_content

# Check for missing, broken, or unoptimized image references
python manage.py audit_images

# Generate a complete CSV SEO audit report
python manage.py generate_seo_report
```

---

## 🧪 Testing & Verification

The codebase includes an automated test suite verifying views, form handling, model constraints, and security headers:

```bash
# Run all unit and integration tests
python manage.py test

# Verify Django configuration and system checks
python manage.py check

# Verify Python syntax across the entire tree
python -m compileall -q .
```

All 21 core tests run in isolated temporary databases with full coverage across public views and API endpoints.

---

## 🌐 Deployment & Production Readiness

### Production Environment Variables

For production deployment (e.g., Docker, AWS, Render, DigitalOcean, or cPanel), configure the following environment variables:

```bash
DATABASE_URL=postgres://user:password@hostname:5432/dbname
DJANGO_SECRET_KEY=your-strong-production-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Static & Media Handling
In production, collect static assets:
```bash
python manage.py collectstatic --noinput
```

### cPanel / Shared Hosting (Passenger WSGI)
The repository includes `passenger_wsgi.py` pre-configured to bind with `projectshub.wsgi`. The `projectshub/urls.py` router also includes fallback serving for `/media/` and `/static/` to ensure uploaded project diagrams and images render properly under Passenger WSGI without extra web server rewrites.

---

## 📄 License & Credits

Developed and maintained by the **ProjectsHub Team**.  
All rights reserved © 2025–2026.
