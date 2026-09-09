# ProjectsHub — Vercel Deployment Guide

This guide explains how to deploy **ProjectsHub** to [Vercel](https://vercel.com) with high performance, WhiteNoise compressed static assets, and automated database loading.

---

## What Has Been Configured For You

1. **`vercel.json`**: Configured `@vercel/python` serverless WSGI runtime and `@vercel/static-build` with `/static/` routing.
2. **`build_files.sh`**: Automated build script that installs dependencies, runs migrations, auto-populates `initial_data.json` (460 objects), and runs `collectstatic`.
3. **`requirements.txt`**: Added `whitenoise`, `dj-database-url`, `psycopg2-binary`, and `gunicorn`.
4. **`projectshub/wsgi.py`**: Exported `app = application` callable for Vercel's serverless runtime.
5. **`projectshub/settings.py`**:
   - Automated detection of Vercel environment (`IS_VERCEL`).
   - WhiteNoise static asset compression with 1-year immutable caching.
   - `CSRF_TRUSTED_ORIGINS` for `*.vercel.app` so all forms, modals, and API calls work smoothly.
   - Dual database support: PostgreSQL (Neon / Supabase / Vercel Postgres) or writable serverless SQLite in `/tmp/db.sqlite3`.
6. **`.vercelignore`**: Excludes temporary files, scrapers, and large local archives from the lambda package, keeping the function payload lightweight (~2-3 MB).
7. **`initial_data.json`**: Complete database fixture containing all 10 projects, categories, navigation items, FAQs, and site settings.

---

## Method 1: Deploy via GitHub (Recommended)

### Step 1: Initialize Git and Commit
In your terminal (inside the `projectsHub` project directory):

```bash
git init
git add .
git commit -m "Configure ProjectsHub for Vercel deployment with WhiteNoise and initial data"
```

### Step 2: Push to GitHub
Create a new repository on [GitHub](https://github.com/new), then run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 3: Import into Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository and click **"Import"**.
4. In **Project Settings**:
   - **Framework Preset**: Leave as *Other* (or Django).
   - **Root Directory**: `./` (current directory).
5. **Environment Variables** (expand section):
   | Key | Value | Description |
   |---|---|---|
   | `SECRET_KEY` | *(A long random string)* | Django security key |
   | `DEBUG` | `False` | Production mode |
   | `DATABASE_URL` | *(Optional - Neon/Supabase)* | PostgreSQL connection URL |
6. Click **"Deploy"**.

Vercel will run `build_files.sh`, collect all static files, initialize the database, and launch your site with a live `*.vercel.app` URL in under 2 minutes!

---

## Method 2: Deploy via Vercel CLI (Instant)

If you have the Vercel CLI installed:

```bash
# 1. Install Vercel CLI globally (if not already installed)
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy to preview
vercel

# 4. Deploy to production
vercel --prod
```

---

## Database Best Practice for Vercel (PostgreSQL)

Vercel functions are stateless and serverless. While your project includes an automatic writable SQLite fallback in `/tmp/db.sqlite3`, a free managed PostgreSQL database is recommended for persistent admin edits and submissions:

1. Create a free PostgreSQL database at **[Neon.tech](https://neon.tech)** or **[Supabase.com](https://supabase.com)**.
2. Copy the connection string (e.g. `postgres://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require`).
3. Add it as an environment variable in **Vercel Dashboard → Project Settings → Environment Variables**:
   - `DATABASE_URL = postgres://...`
4. Re-deploy. The build script will automatically run migrations and populate all project data!
