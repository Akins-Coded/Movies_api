"""
Django settings for movies_api project.
Production- and CI-friendly.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import environ

# -----------------------------------------------------
# Core / env
# -----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Read .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    env.read_env(ENV_PATH)

DEBUG = env("DEBUG")  # default False per Env config

# IMPORTANT: never use the fallback key in production
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-secret-key")
if not DEBUG and SECRET_KEY == "insecure-secret-key":
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must be set in production (e.g. via env)."
 # Hosts — include your live domain(s). Temporary wildcard can be enabled via env.
ALLOWED_HOSTS = (
    ["*"]  # TEMP ONLY: use for debugging host issues
    if env.bool("ALLOW_ALL_HOSTS_TEMP", default=False)
    else env.list(
        "ALLOWED_HOSTS",
        default=[
            "coded.pythonanywhere.com",  # live domain
            "127.0.0.1",
            "localhost",
        ],
    )
)


# CSRF (scheme required)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
        "http://localhost",
        "http://127.0.0.1",
    ],
)

# -----------------------------------------------------
# Apps
# -----------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "rest_framework",
    "drf_yasg",
    "corsheaders",
    # Local apps
    "films.apps.FilmsConfig",
]

# -----------------------------------------------------
# Middleware (CORS early; WhiteNoise enabled)
# -----------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "movies_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "movies_api.wsgi.application"

# -----------------------------------------------------
# Database
#   - SQLite in DEBUG or CI
#   - MySQL in production, with strict mode and persistent connections
# -----------------------------------------------------
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("MYSQL_DATABASE", default="movies_db"),
            "USER": env("MYSQL_USER", default="root"),
            "PASSWORD": env("MYSQL_PASSWORD", default=""),
            "HOST": env("MYSQL_HOST", default="127.0.0.1"),
            "PORT": env("MYSQL_PORT", default="3306"),
            "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),  # keep-alives
            "OPTIONS": {
                # enable strict mode to avoid silent truncation, etc.
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# Use SQLite automatically in CI (e.g., GitHub Actions)
if os.environ.get("CI") == "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

# -----------------------------------------------------
# Password validation
# -----------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -----------------------------------------------------
# I18N / TZ
# -----------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------------------------------
# Static files (Django 5: use STORAGES instead of STATICFILES_STORAGE)
# -----------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# -----------------------------------------------------
# DRF
# -----------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        )
        if DEBUG
        else ("rest_framework.renderers.JSONRenderer",)
    ),
}

# -----------------------------------------------------
# Cache (override via env in real prod if needed)
# -----------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(BASE_DIR / "django_cache"),
        "TIMEOUT": 60 * 30,  # 30 minutes
    }
}

# -----------------------------------------------------
# Security hardening for production
#   (these apply only when DEBUG=False)
# -----------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # modern cookie defaults
    SESSION_COOKIE_SAMESITE = "Lax"
    CSRF_COOKIE_SAMESITE = "Lax"

    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True  # harmless on modern Django, kept for proxies
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# CI override: avoid HTTPS redirect loops with Django test client (http://testserver)
if os.environ.get("CI") == "true":
    SECURE_SSL_REDIRECT = False
    # Avoid DisallowedHost if DEBUG is False in CI
    if "testserver" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append("testserver")

# -----------------------------------------------------
# CORS
#   - Use explicit allowed origins with schemes (no trailing slash).
#   - Prefer a tight list in production.
# -----------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
        "http://localhost",
        "http://127.0.0.1",
    ],
)

# -----------------------------------------------------
# API integrations
# -----------------------------------------------------
SWAPI_BASE_URL = env("SWAPI_BASE_URL", default="https://swapi.dev/api")

# Don't auto-append slashes; DRF router defines its own slash behavior
APPEND_SLASH = False

# -----------------------------------------------------
# Logging (send warnings/errors to console; useful on PA and GHA)
# -----------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
