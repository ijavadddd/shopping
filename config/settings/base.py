# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""

from pathlib import Path

import environ
from datetime import timedelta
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
import os
import json


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# shopping/
APPS_DIR = BASE_DIR / "shopping"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Asia/Tehran"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#languages
# from django.utils.translation import gettext_lazy as _
# LANGUAGES = [
#     ('en', _('English')),
#     ('fr-fr', _('French')),
#     ('pt-br', _('Portuguese')),
# ]
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "baton",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "crispy_bootstrap5",
    "allauth",
    "allauth.account",
    "allauth.mfa",
    "allauth.socialaccount",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "minio_storage",
    "mptt",
    "django_user_agents",
]

LOCAL_APPS = [
    "shopping.users",
    # Your stuff: custom apps go here
    "shopping.product",
    "shopping.order",
    "shopping.cart",
    "shopping.crm",
    "shopping.accounting",
    "shopping.dashboard",
    "baton.autodiscover",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "shopping.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "users:redirect"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # local
    "config.middleware_logs.RequestIDMiddleware",
    # third party
    "django.middleware.security.SecurityMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
    "request_logging.middleware.LoggingMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Collectfasta settings
# ------------------------------------------------------------------------------
COLLECTFASTA_STRATEGY = "collectfasta.strategies.filesystem.FileSystemStrategy"

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "shopping.users.context_processors.allauth_settings",
            ],
        },
    },
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Javad Ghasemi""", "ijavadd.dev@gmail.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
# https://cookiecutter-django.readthedocs.io/en/latest/settings.html#other-environment-settings
# Force the `admin` sign in process to go through the `django-allauth` workflow
DJANGO_ADMIN_FORCE_ALLAUTH = env.bool("DJANGO_ADMIN_FORCE_ALLAUTH", default=False)


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s] %(asctime)s - %(name)s: request_id: *%(request_id)s* duration: '%(duration)s', agent: '%(user_agent)s', ip: %(ip)s, %(message)s",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(duration)s %(user_agent)s %(ip)s, %(message)s",
        },
    },
    "filters": {
        "request_id": {"()": "config.log_config.RequestIDFilter"},
        "health_check": {
            "()": "config.log_config.HealthcheckFilter",
        },
        "redact_pii": {
            "()": "config.log_config.RedactPIIFilter",
        },
    },
    "handlers": {
        # --- Django handlers ---
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "django.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 2,
            "formatter": "json",
            "filters": ["request_id", "health_check", "redact_pii"],
        },
        "selector": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "selector.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 2,
            "formatter": "json",
            "filters": ["request_id", "redact_pii"],
        },
        "django_stream": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id", "health_check", "redact_pii"],
        },
        # --- Celery handlers ---
        "celery_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "celery.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
        },
        # --- General app handlers ---
        "app_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "json",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_file", "django_stream"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery_file"],
            "level": "INFO",
            "propagate": False,
        },
        "selector": {
            "handlers": ["selector", "django_stream"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["django_stream"],
        "level": "WARNING",
    },
}

REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")
REDIS_SSL = REDIS_URL.startswith("rediss://")


# django-allauth
# ------------------------------------------------------------------------------
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_LOGIN_METHODS = {"email"}
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# https://docs.allauth.org/en/latest/account/configuration.html
ACCOUNT_ADAPTER = "shopping.users.adapters.AccountAdapter"
# https://docs.allauth.org/en/latest/account/forms.html
ACCOUNT_FORMS = {"signup": "shopping.users.forms.UserSignupForm"}
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_ADAPTER = "shopping.users.adapters.SocialAccountAdapter"
# https://docs.allauth.org/en/latest/socialaccount/configuration.html
SOCIALACCOUNT_FORMS = {"signup": "shopping.users.forms.UserSocialSignupForm"}

# django-rest-framework
# -------------------------------------------------------------------------------
# django-rest-framework - https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# By Default swagger ui is available only to admin user(s). You can change permission classes to change that
# See more configuration options at https://drf-spectacular.readthedocs.io/en/latest/settings.html#settings
SPECTACULAR_SETTINGS = {
    "TITLE": "shopping API",
    "DESCRIPTION": "Documentation of API endpoints of shopping",
    "VERSION": "1.0.0",
    # "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
    "SCHEMA_PATH_PREFIX": "/api/",
}
# Your stuff...
# ------------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
}

# File Storage
# ------------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "minio_storage.storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# MinIO Credentials
MINIO_STORAGE_ENDPOINT = env(
    "MINIO_STORAGE_ENDPOINT", default="localhost:9000"
)  # Include protocol
MINIO_STORAGE_ACCESS_KEY = env("MINIO_STORAGE_ACCESS_KEY")
MINIO_STORAGE_SECRET_KEY = env("MINIO_STORAGE_SECRET_KEY")
MINIO_STORAGE_USE_HTTPS = env("MINIO_STORAGE_USE_HTTPS", default=False)

# Optional Metadata for Media Files
MINIO_STORAGE_MEDIA_OBJECT_METADATA = env(
    "MINIO_STORAGE_MEDIA_OBJECT_METADATA", default={}
)

# Buckets
MINIO_STORAGE_MEDIA_BUCKET_NAME = env(
    "MINIO_STORAGE_MEDIA_BUCKET_NAME", default="media"
)
MINIO_STORAGE_STATIC_BUCKET_NAME = env(
    "MINIO_STORAGE_STATIC_BUCKET_NAME", default="static"
)

# Backups (Optional)
MINIO_STORAGE_MEDIA_BACKUP_BUCKET = env("MINIO_STORAGE_MEDIA_BACKUP_BUCKET", default="")
MINIO_STORAGE_MEDIA_BACKUP_FORMAT = env("MINIO_STORAGE_MEDIA_BACKUP_FORMAT", default="")

# Auto-create buckets on startup
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env(
    "MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET", default=True
)
MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = True  # or env(...) if you prefer

# MinIO Storage Settings
MINIO_STORAGE_MEDIA_BUCKET = MINIO_STORAGE_MEDIA_BUCKET_NAME
MINIO_STORAGE_STATIC_BUCKET = MINIO_STORAGE_STATIC_BUCKET_NAME
MINIO_STORAGE_MEDIA_URL = f"{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_MEDIA_BUCKET_NAME}/"
MINIO_STORAGE_STATIC_URL = (
    f"{MINIO_STORAGE_ENDPOINT}/{MINIO_STORAGE_STATIC_BUCKET_NAME}/"
)
