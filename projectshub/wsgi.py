import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectshub.settings')
application = get_wsgi_application()

# Vercel serverless function entrypoint
app = application
