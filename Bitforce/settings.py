"""
Django settings para Bitforce (Producción en Railway + Front en Netlify)
"""
from pathlib import Path
from datetime import timedelta
import os

# ========================
# BASE / CONFIG GENERAL
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-key-dev")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# Hosts y CSRF desde env (Railway)
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS",
    "bitforce-production.up.railway.app,localhost,127.0.0.1",
).split(",")

CSRF_TRUSTED_ORIGINS = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://bitforce-production.up.railway.app,https://bitforce-gym.netlify.app",
).split(",")

# ========================
# APPS
# ========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps locales
    "AccountAdmin",
    "BitforceApp",

    # Terceros
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # antes de CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Bitforce.urls"

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

WSGI_APPLICATION = "Bitforce.wsgi.application"

# ========================
# BASE DE DATOS (Railway)
# ========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQLDATABASE", "MYSQL_DATABASE", default="railway"),
        "USER": env("MYSQLUSER", "MYSQL_USER", default="root"),
        "PASSWORD": env("MYSQLPASSWORD", "MYSQL_PASSWORD", "MYSQL_ROOT_PASSWORD", default=""),
        "HOST": env("MYSQLHOST", "MYSQL_HOST", default="localhost"),
        "PORT": env("MYSQLPORT", "MYSQL_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ========================
# PASSWORDS
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ========================
# I18N / TZ
# ========================
LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Mendoza"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ========================
# CORS (Netlify + local)
# ========================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://bitforce-gym.netlify.app",
    "http://localhost:3000",
]

# --- Toggle API pública (para pruebas) ---
API_PUBLIC = os.getenv("DJANGO_API_PUBLIC", "False") == "True"
if API_PUBLIC:
    # 🔓 Permitir todo CORS temporalmente
    CORS_ALLOW_ALL_ORIGINS = True

# ========================
# DRF + JWT
# ========================
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (
        ("rest_framework.permissions.AllowAny",)  # 🔓 público si DJANGO_API_PUBLIC=True
        if API_PUBLIC
        else ("rest_framework.permissions.IsAuthenticated",)  # 🔒 protegido por defecto
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ========================
# USER MODEL
# ========================
AUTH_USER_MODEL = "AccountAdmin.GymUser"

# ========================
# HTTPS detrás de proxy (Railway)
# ========================
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ========================
# ARCHIVOS ESTÁTICOS (requerido por Django)
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
