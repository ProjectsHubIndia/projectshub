#!/bin/bash
# Vercel Build Script for ProjectsHub Django App
echo "=== Building ProjectsHub for Vercel Deployment ==="

# Create and activate virtual environment to avoid PEP 668 externally-managed-environment
if python3 -m venv .venv 2>/dev/null; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    python3 -m pip install --break-system-packages -r requirements.txt || python3 -m pip install -r requirements.txt
fi

# Run migrations if database is accessible
python3 manage.py migrate --noinput || true

# Load seeded data into database
python3 manage.py loaddata initial_data.json || true

# Collect static files into staticfiles directory
python3 manage.py collectstatic --noinput --clear

# Copy media assets into staticfiles for direct CDN serving
if [ -d "media" ]; then
    mkdir -p staticfiles/media
    cp -rn media/* staticfiles/media/ 2>/dev/null || cp -r media/* staticfiles/media/ || true
fi

echo "=== Build finished successfully ==="
