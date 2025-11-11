"""
Django settings for movies_api project.
"""

from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import environ

# -------------------------------------------------------------------
# Paths & env
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)

ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    environ.Env.read_env(str(ENV_PATH))

# -------------------------------------------------------------------
# Core settings
# -------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-secret-key")

# Do not let env accidentally return a string "False"/"True" — Env handles cast
DEBUG = env("DEBUG")

# Allow-all switch for emergency debugging only (turn off after testing!)
ALLOW_ALL_HOSTS_TEMP = env.bool("ALLOW_ALL_HOSTS_TEMP", default=False)

# Your real hosts (keep your live domain here!)
DEFAULT_ALLOWED_HOSTS = [
    "coded.pythonanywhere.com",
    "127.0.0.1",
    "localhost",
]

ALLOWED_HOSTS = ["*"] if ALLOW_ALL_HOSTS_TEMP else env.list(
    "ALLOWED_HOSTS",
    default=DEFAULT_ALLOWED_HOSTS,
)

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS is empty. Set ALLOWED_HOSTS env or enable ALLOW_ALL_HOSTS_TEMP=true only for debugging."
    )

# -------------------------------------------------------------------
# Applications
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # static files in prod
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

# -------------------------------------------------------------------
# Database
#   - SQLite for DEBUG/CI
#   - MySQL for production
# -------------------------------------------------------------------
if DEBUG or os.environ.get("CI") == "true":
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
            "OPTIONS": {
                # Enable “strict mode” to avoid silent truncation (fixes mysql.W002 warning)
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# I18N
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static files
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# DRF
# -------------------------------------------------------------------
if DEBUG:
    DEFAULT_RENDERERS = (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    )
else:
    DEFAULT_RENDERERS = ("rest_framework.renderers.JSONRenderer",)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERERS,
}

# -------------------------------------------------------------------
# Cache (file cache by default)
# -------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": str(BASE_DIR / "django_cache"),
        "TIMEOUT": 60 * 30,  # 30 minutes
    }
}

# -------------------------------------------------------------------
# Security (production)
# -------------------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# In CI, don't force HTTPS and allow Django test host
if os.environ.get("CI") == "true":
    SECURE_SSL_REDIRECT = False
    if "testserver" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS = list(set(ALLOWED_HOSTS + ["testserver"]))

# -------------------------------------------------------------------
# External APIs / misc
# -------------------------------------------------------------------
SWAPI_BASE_URL = env("SWAPI_BASE_URL", default="https://swapi.dev/api")

# -------------------------------------------------------------------
# CORS / CSRF
#   IMPORTANT: Schemes are required; never include a bare host here.
# -------------------------------------------------------------------
# Dev convenience: allow-all in DEBUG only (you can tighten later)
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
        "http://localhost",
        "http://127.0.0.1",
    ],
)

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
        "http://localhost",
        "http://127.0.0.1",
    ],
)

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
