"""
Django settings for AI ProjectsHub.
Production-ready configuration optimized for Vercel & local development.
"""
from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from django.core.exceptions import ImproperlyConfigured

# Detect production environment
IS_VERCEL = os.environ.get('VERCEL') == '1' or 'VERCEL' in os.environ
IS_PRODUCTION = (
    IS_VERCEL or
    any(k in os.environ for k in ('RAILWAY_ENVIRONMENT', 'RAILWAY_STATIC_URL', 'RENDER', 'DYNO', 'HEROKU')) or
    os.environ.get('ENVIRONMENT', '').lower() == 'production'
)

# Debug: Defaults to False in production, True for local development
DEBUG_DEFAULT = 'False' if IS_PRODUCTION else 'True'
DEBUG = os.environ.get('DEBUG', DEBUG_DEFAULT).lower() in ('true', '1', 'yes')

# Security: Secret key from environment variable (fails fast in production if unset)
raw_secret = os.environ.get('DJANGO_SECRET_KEY', '').strip() or os.environ.get('SECRET_KEY', '').strip()
if not raw_secret:
    import sys
    if 'test' in sys.argv:
        SECRET_KEY = 'django-insecure-test-suite-key-for-local-testing-only'
    elif IS_PRODUCTION:
        raise ImproperlyConfigured("SECRET_KEY environment variable is required in production environments.")
    elif not DEBUG:
        raise ImproperlyConfigured("SECRET_KEY environment variable is required when DEBUG is False.")
    else:
        import secrets
        SECRET_KEY = 'django-insecure-dev-' + secrets.token_urlsafe(40)
else:
    SECRET_KEY = raw_secret

# Allowed Hosts: Explicit domains in production, platform wildcards, and local dev
BASE_ALLOWED_HOSTS = [
    'projectshub.co.in',
    'www.projectshub.co.in',
    '.projectshub.co.in',
    'projectshub-production.up.railway.app',
    '.railway.app',
    '.up.railway.app',
    '.vercel.app',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'testserver',
]

raw_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '').strip()
if raw_allowed_hosts == '*':
    ALLOWED_HOSTS = ['*']
elif raw_allowed_hosts:
    cleaned_hosts = [
        h.replace('https://', '').replace('http://', '').split('/')[0].strip()
        for h in raw_allowed_hosts.split(',') if h.strip()
    ]
    for bh in BASE_ALLOWED_HOSTS:
        if bh not in cleaned_hosts:
            cleaned_hosts.append(bh)
    ALLOWED_HOSTS = cleaned_hosts
else:
    ALLOWED_HOSTS = list(BASE_ALLOWED_HOSTS)

# Automatically include platform-provided domains if present in environment
for env_key in ('VERCEL_URL', 'VERCEL_BRANCH_URL', 'VERCEL_PROJECT_PRODUCTION_URL', 'RAILWAY_PUBLIC_DOMAIN', 'RAILWAY_STATIC_URL', 'RAILWAY_TCP_PROXY_DOMAIN', 'SITE_DOMAIN'):
    val = os.environ.get(env_key, '').strip()
    if val:
        clean_val = val.replace('https://', '').replace('http://', '').split('/')[0]
        if clean_val and '*' not in ALLOWED_HOSTS and clean_val not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(clean_val)

# CSRF Trusted Origins: Specific domains, platform subdomains, and local dev
CSRF_TRUSTED_ORIGINS = [
    'https://projectshub.co.in',
    'https://www.projectshub.co.in',
    'https://projectshub-production.up.railway.app',
    'https://*.railway.app',
    'https://*.up.railway.app',
    'https://*.vercel.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1:8080',
    'http://localhost:8080',
]
extra_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
if extra_origins:
    CSRF_TRUSTED_ORIGINS.extend([o.strip() for o in extra_origins.split(',') if o.strip()])

for env_key in ('VERCEL_URL', 'VERCEL_BRANCH_URL', 'VERCEL_PROJECT_PRODUCTION_URL', 'RAILWAY_PUBLIC_DOMAIN'):
    val = os.environ.get(env_key, '').strip()
    if val:
        clean_domain = val.replace('https://', '').replace('http://', '').split('/')[0]
        clean_origin = f'https://{clean_domain}'
        if clean_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(clean_origin)

# Reverse proxy SSL header for Vercel & Railway
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Base site domain / URL configuration (empty by default to enable full dynamic auto-detection)
SITE_URL = os.environ.get('SITE_URL', '').rstrip('/')
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'projectshub.co.in')

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True' if IS_PRODUCTION else 'False').lower() in ('true', '1', 'yes')
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
    'core.middleware.RedirectMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'projectshub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'projectshub.wsgi.application'

# Database: PostgreSQL in production if DATABASE_URL or POSTGRES_URL is set, SQLite fallback
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')
if DATABASE_URL and DATABASE_URL.startswith('postgres'):
    try:
        import dj_database_url
        is_internal = any(h in DATABASE_URL for h in ['railway.internal', 'localhost', '127.0.0.1'])
        use_ssl = not is_internal and os.environ.get('DB_SSL_REQUIRE', 'true').lower() in ('true', '1', 'yes')
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=use_ssl
            )
        }
    except Exception:
        from urllib.parse import urlparse
        url = urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': url.path[1:],
                'USER': url.username,
                'PASSWORD': url.password,
                'HOST': url.hostname,
                'PORT': url.port or 5432,
            }
        }
else:
    # If on Vercel without PostgreSQL, use a writable temporary sqlite database
    if IS_VERCEL:
        import shutil
        import tempfile
        tmp_dir = Path(tempfile.gettempdir())
        tmp_db = tmp_dir / 'db.sqlite3'
        local_db = BASE_DIR / 'db.sqlite3'
        if (not tmp_db.exists() or tmp_db.stat().st_size == 0) and local_db.exists():
            try:
                tmp_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(local_db), str(tmp_db))
            except Exception:
                pass
        db_path = tmp_db if tmp_db.exists() else local_db
    else:
        db_path = BASE_DIR / 'db.sqlite3'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(db_path),
        }
    }

AUTHENTICATION_BACKENDS = [
    'core.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# Static Files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage: serves compressed static assets with high-performance caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media Files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'projectshub-cache',
    }
}

# Email Notification Configuration (Graceful dev fallback to console backend)
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'support@projectshub.co.in')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

