#!/bin/bash
# Vercel Build Script for ProjectsHub Django App
echo "=== Building ProjectsHub for Vercel Deployment ==="

# Install dependencies
python3 -m pip install -r requirements.txt

# Run migrations if database is accessible
python3 manage.py migrate --noinput || true

# Load seeded data into database
python3 manage.py loaddata initial_data.json || true

# Collect static files into staticfiles directory
python3 manage.py collectstatic --noinput --clear

echo "=== Build finished successfully ==="
