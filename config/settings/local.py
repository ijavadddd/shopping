# ruff: noqa: E501
from .base import *  # noqa: F403
from .base import INSTALLED_APPS
from .base import MIDDLEWARE
from .base import env
import os
from rich.logging import RichHandler


# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="VUAc8S6nG45zeWDoot8xQnrqI07Q0UAjIxAxre7F26sogY0KPnVjeuVgF5xD4ZQN",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]  # noqa: S104

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    },
}

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "silk.middleware.SilkyMiddleware",
]
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": [
        "debug_toolbar.panels.redirects.RedirectsPanel",
        # Disable profiling panel due to an issue with Python 3.12:
        # https://github.com/jazzband/django-debug-toolbar/issues/1875
        "debug_toolbar.panels.profiling.ProfilingPanel",
    ],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += [
    "django_extensions",
    "silk",
]

# Your stuff...
# ------------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

LOCAL_LOG_DIR = os.path.join(LOG_DIR, "local")
os.makedirs(LOCAL_LOG_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {
            "format": "[%(levelname)s] %(asctime)s - %(name)s: request_id: *%(request_id)s* duration: '%(duration)s', agent: '%(user_agent)s', ip: %(ip)s, %(message)s",
        },
    },
    "filters": {
        "request_id": {"()": "config.log_config.RequestIDFilter"},
        "health_check": {"()": "config.log_config.HealthcheckFilter"},
        "redact_pii": {"()": "config.log_config.RedactPIIFilter"},
    },
    "handlers": {
        # --- Django handlers ---
        "django_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOCAL_LOG_DIR, "django.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 2,
            "formatter": "rich",
            "filters": ["request_id", "health_check", "redact_pii"],
        },
        "selector": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOCAL_LOG_DIR, "selector.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 2,
            "formatter": "rich",
            "filters": ["request_id", "redact_pii"],
        },
        "django_stream": {
            "level": "DEBUG",  # show all in dev console
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "filters": ["request_id", "health_check", "redact_pii"],
            "rich_tracebacks": True,  # pretty + colored tracebacks
            "markup": True,  # allow [red]text[/red] inside logs
            "show_time": True,
            "show_level": True,
            "show_path": True,
        },
        # --- Celery handlers ---
        "celery_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOCAL_LOG_DIR, "celery.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "rich",
        },
        # --- General app handlers ---
        "app_file": {
            "level": "INFO",
            "class": "logging.handlers.ConcurrentRotatingFileHandler",
            "filename": os.path.join(LOCAL_LOG_DIR, "app.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "rich",
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
        "level": "INFO",
    },
}

SILKY_META = True
SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True

# profiling functions
SILKY_DYNAMIC_PROFILING = [
    {
        "module": "shopping.product.api.views",
        "function": "ProductListAPIView.get_queryset",
    }
]
