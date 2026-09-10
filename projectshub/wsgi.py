import os
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectshub.settings')

from django.core.wsgi import get_wsgi_application
try:
    django_app = get_wsgi_application()
except Exception:
    import traceback
    sys.stderr.write(f"DJANGO INIT FAILED:\n{traceback.format_exc()}\n")
    raise

def application(environ, start_response):
    try:
        return django_app(environ, start_response)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        sys.stderr.write(f"DJANGO SERVERLESS CRASH:\n{tb}\n")
        start_response("500 Internal Server Error", [("Content-Type", "text/plain; charset=utf-8")])
        return [f"DJANGO CRASH TRACEBACK:\n\n{tb}".encode("utf-8")]

# Vercel serverless function entrypoint
app = application


