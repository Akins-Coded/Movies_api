"""
Django settings for movies_api project.
"""

from pathlib import Path
import os

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

# Read .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    env.read_env(ENV_PATH)

# Core
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-secret-key")
DEBUG = env("DEBUG")  # default False per Env config
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])

# Apps
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

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise for static files in production/deployment
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

# Database configuration
if DEBUG:
    # Local development: SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Production: MySQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("MYSQL_DATABASE", default="movies_db"),
            "USER": env("MYSQL_USER", default="root"),
            "PASSWORD": env("MYSQL_PASSWORD", default=""),
            "HOST": env("MYSQL_HOST", default="127.0.0.1"),
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
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# enabling compressed and cached static files storage with WhiteNoise
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# DRF
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        # Keep browsable API in DEBUG only
        (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        )
        if DEBUG
        else ("rest_framework.renderers.JSONRenderer",)
    ),
}

# Caching (file-based by default; override in prod)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(BASE_DIR / "django_cache"),
        "TIMEOUT": 60 * 30,  # 30 minutes
    }
}

# Security hardening for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# SWAPI base URL
SWAPI_BASE_URL = env("SWAPI_BASE_URL", default="https://swapi.dev/api")

# CORS (relaxed by default for local dev)
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=True)
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "http://localhost",
        "http://127.0.0.1",
        "https://coded.pythonanywhere.com",
        "coded.pythonanywhere.com",
    ],
)

APPEND_SLASH = False