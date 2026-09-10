import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectshub.settings')
application = get_wsgi_application()

# Ensure database is initialized in Vercel serverless runtime when using SQLite fallback
if os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ:
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url.startswith('postgres'):
        ready_flag = Path('/tmp/.db_ready')
        if not ready_flag.exists():
            try:
                from django.core.management import call_command
                call_command('migrate', interactive=False, verbosity=0)
                fixture_path = Path(__file__).resolve().parent.parent / 'initial_data.json'
                if fixture_path.exists():
                    call_command('loaddata', str(fixture_path), interactive=False, verbosity=0)
                ready_flag.touch()
            except Exception as e:
                import logging
                logging.getLogger('django').warning(f'Serverless SQLite setup: {e}')

# Vercel serverless function entrypoint
app = application

