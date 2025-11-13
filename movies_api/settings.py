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

# ---------------------------------------------------------
# Hosts (no scheme/port here)
# ---------------------------------------------------------
if DEBUG:
    # Development: keep things simple
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
else:
    # Production: require explicit hosts
    raw_hosts = env("DJANGO_ALLOWED_HOSTS", default="Coded.pythonanywhere.com")
    if not raw_hosts:
        raise ImproperlyConfigured(
            "DJANGO_ALLOWED_HOSTS must be set in production "
            "(comma-separated, e.g. 'example.com, www.example.com')."
        )

    ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]

# ---------------------------------------------------------
# CORS / CSRF
# ---------------------------------------------------------
# In dev you can choose to allow all origins via env, otherwise we parse explicit lists.
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

if not CORS_ALLOW_ALL_ORIGINS:
    # CORS_ALLOWED_ORIGINS must include scheme (http/https)
    raw_cors = env("DJANGO_CORS_ALLOWED_ORIGINS", default="Coded.pythonanywhere.com")
    if raw_cors:
        CORS_ALLOWED_ORIGINS = [
            o.strip() for o in raw_cors.split(",") if o.strip()
        ]
    elif DEBUG:
        # Sensible dev defaults if nothing provided
        CORS_ALLOWED_ORIGINS = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]
    else:
        # Prod + no CORS config = probably a misconfig
        raise ImproperlyConfigured(
            "DJANGO_CORS_ALLOWED_ORIGINS must be set in production "
            "when CORS_ALLOW_ALL_ORIGINS=False "
            "(comma-separated, e.g. 'https://app.example.com,https://admin.example.com')."
        )

# CSRF_TRUSTED_ORIGINS must also include scheme (http/https)
raw_csrf = env("DJANGO_CSRF_TRUSTED_ORIGINS", default="https://Coded.pythonanywhere.com")
if raw_csrf:
    CSRF_TRUSTED_ORIGINS = [
        o.strip() for o in raw_csrf.split(",") if o.strip()
    ]
elif DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
else:
    # In strict production setups you can require this,
    # or you can choose to default to an empty list instead of raising.
    raise ImproperlyConfigured(
        "DJANGO_CSRF_TRUSTED_ORIGINS must be set in production "
        "(comma-separated, including scheme, e.g. 'https://example.com')."
    )

# ---------------------------------------------------------
# Installed apps
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
    "films.apps.FilmsConfig",  
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

# --------------------------
# STATIC FILES
# --------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")] if (BASE_DIR / "static").exists() else []
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------
# MEDIA FILES (Optional)
# --------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")

# ---------------------------------------------------------
# DRF & Swagger
# ---------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 6,
}

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DEFAULT_INFO": "movies_api.urls.api_info",
}

# -----------------
# SECURITY BEST PRACTICES
# --------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
X_FRAME_OPTIONS = "DENY"

# --------------------------
# SWAGGER
# --------------------------
SWAGGER_USE_COMPAT_RENDERERS = False

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

# --------------------------
# CACHES
# --------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "movies-cache",
    }
}

SWAGGER_USE_COMPAT_RENDERERS = False
