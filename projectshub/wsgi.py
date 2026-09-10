import os
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectshub.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel serverless function entrypoint
app = application


