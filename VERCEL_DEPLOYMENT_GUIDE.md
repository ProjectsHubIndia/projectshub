# ProjectsHub — Vercel Deployment Guide

This guide explains how to deploy **ProjectsHub** to [Vercel](https://vercel.com) with WhiteNoise-compressed static assets and a persistent PostgreSQL database.

---

## What Has Been Configured For You

1. **`vercel.json`**: Configured `@vercel/python` serverless WSGI runtime and `@vercel/static-build` with `/static/` routing.
2. **`build_files.sh`**: Build script that installs dependencies, applies migrations, collects static files, and builds the compressor manifest. A failed migration or asset build fails the deployment.
3. **`requirements.txt`**: Added `whitenoise`, `dj-database-url`, `psycopg2-binary`, and `gunicorn`.
4. **`projectshub/wsgi.py`**: Exported `app = application` callable for Vercel's serverless runtime.
5. **`projectshub/settings.py`**:
   - Automated detection of Vercel environment (`IS_VERCEL`).
   - WhiteNoise static asset compression with 1-year immutable caching.
   - `CSRF_TRUSTED_ORIGINS` for `*.vercel.app` so all forms, modals, and API calls work smoothly.
   - PostgreSQL is supported through `DATABASE_URL`. SQLite is only a temporary, non-persistent fallback and must not be used for production data.
6. **`.vercelignore`**: Excludes temporary files, scrapers, and large local archives from the lambda package, keeping the function payload lightweight (~2-3 MB).
7. **`initial_data.json`**: A project data fixture; the deployment build does not load it automatically or reset database content.

---

## Method 1: Deploy via GitHub (Recommended)

### Step 1: Commit Reviewed Changes
The project is already a Git repository. Review the worktree and commit only the files intended for deployment; do not initialize a nested repository or stage every file indiscriminately.

```bash
git status --short
```

Use your normal reviewed-file staging and commit workflow before pushing.

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
   | `DATABASE_URL` | *(Required for production)* | Persistent PostgreSQL connection URL |
6. Click **"Deploy"**.

Vercel runs `build_files.sh`, which applies migrations to the configured database and collects static assets. It does not populate the database from `initial_data.json`. If seed content is needed, run the documented `seed_data` command deliberately and once against the configured database. Do not rely on the serverless SQLite fallback for data that must persist.

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

Vercel functions are stateless and serverless. The SQLite fallback is temporary and may be discarded between invocations or deployments; configure PostgreSQL before using the site for persistent admin edits or submissions:

1. Create a free PostgreSQL database at **[Neon.tech](https://neon.tech)** or **[Supabase.com](https://supabase.com)**.
2. Copy the connection string (e.g. `postgres://user:pass@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require`).
3. Add it as an environment variable in **Vercel Dashboard → Project Settings → Environment Variables**:
   - `DATABASE_URL = postgres://...`
4. Re-deploy. The build script applies migrations; initialize seed content explicitly if needed. Existing database records are not overwritten by deployment.
