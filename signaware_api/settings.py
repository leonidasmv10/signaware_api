from pathlib import Path
from datetime import timedelta
import os
from corsheaders.defaults import (
    default_headers,
)

# Cargar variables de entorno desde .env
from dotenv import load_dotenv
load_dotenv()

# =============================================================================
# Project Paths
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# Security Settings
# =============================================================================
SECRET_KEY = "django-insecure-m9pk-5@z^xd%fde@qcb_e&@2*t^(_ovl&igg4i%3-4o@w6t%co"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# =============================================================================
# Application Definition
# =============================================================================
INSTALLED_APPS = [
    # Django Core Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third Party Apps
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # Local Apps
    "users",
    "core",
    "agent",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =============================================================================
# URL & Template Configuration
# =============================================================================
ROOT_URLCONF = "signaware_api.urls"

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

# =============================================================================
# ASGI/WSGI Configuration
# =============================================================================
ASGI_APPLICATION = "signaware_api.asgi.application"

# =============================================================================
# Database Configuration
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# =============================================================================
# Password Validation
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================================================================
# Internationalization
# =============================================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

# =============================================================================
# Static Files
# =============================================================================
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# REST Framework Configuration
# =============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

# =============================================================================
# CORS Configuration
# =============================================================================
CORS_ALLOWED_ORIGINS = [
    "https://safedrivev.netlify.app",
    "http://localhost:5173",
]

CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

# =============================================================================
# Email Configuration
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "recover.safedrive@gmail.com"
EMAIL_HOST_PASSWORD = "eazc mmjd ktjn rgkd"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# =============================================================================
# JWT Configuration
# =============================================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}

CSRF_TRUSTED_ORIGINS = [
    'https://safedriveapi.shop',
]
