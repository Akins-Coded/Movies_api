from pathlib import Path
import os
from django.core.exceptions import ImproperlyConfigured
import environ

# ---------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    environ.Env.read_env(str(ENV_PATH))

# ---------------------------------------------------------
# Core
# ---------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="change-this-in-prod")
DEBUG = env.bool("DEBUG", default=False)

# In production you must set ALLOWED_HOSTS via env
DEFAULT_ALLOWED_HOSTS = ["coded.pythonanywhere.com", "127.0.0.1", "localhost"]
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=DEFAULT_ALLOWED_HOSTS)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS cannot be empty in production.")

# ---------------------------------------------------------
# Installed apps (films is REQUIRED)
# ---------------------------------------------------------
INSTALLED_APPS = [
    # Django
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

    # Local
    "films.apps.FilmsConfig",   # <-- hard requirement
]

# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------
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
        "DIRS": [BASE_DIR / "templates"],
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

# ---------------------------------------------------------
# Database: MySQL in prod, SQLite if DEBUG
# ---------------------------------------------------------
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
            "NAME": env("MYSQL_DATABASE"),
            "USER": env("MYSQL_USER"),
            "PASSWORD": env("MYSQL_PASSWORD"),
            "HOST": env("MYSQL_HOST"),
            "PORT": env("MYSQL_PORT", default="3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

# ---------------------------------------------------------
# Password validation
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------
# Internationalization
# ---------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------
# DRF & Swagger
# ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer" if DEBUG else "rest_framework.renderers.JSONRenderer",
    ),
}
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DEFAULT_INFO": "movies_api.urls.api_info",
}

# ---------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=DEBUG)
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
        "http://127.0.0.1",
        "http://localhost",
    ],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://coded.pythonanywhere.com",
    ],
)

# Keep exact paths (avoid / to / redirects that can confuse PA /docs)
APPEND_SLASH = False

# ---------------------------------------------------------
# Security (hardened in production)
# ---------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------
# External API(s)
# ---------------------------------------------------------
SWAPI_BASE_URL = env("SWAPI_BASE_URL", default="https://swapi.dev/api")

# ---------------------------------------------------------
# Logging (simple console)
# ---------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": True},
        "django.request": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
