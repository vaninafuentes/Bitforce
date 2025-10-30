"""
Django settings for Bitforce project (producción listo para Railway + Netlify).
"""

import os
from pathlib import Path
from datetime import timedelta

# ========================
# BASE / CONFIG GENERAL
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta (usá variable de entorno en producción)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'insecure-key-dev')

# Debug activado solo localmente
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Hosts permitidos
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')


# ========================
# APLICACIONES
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps locales
    'AccountAdmin',
    'BitforceApp',

    # Librerías externas
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'rest_framework_simplejwt.token_blacklist',
]


# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ========================
# URLS / TEMPLATES / WSGI
# ========================
ROOT_URLCONF = 'Bitforce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Bitforce.wsgi.application'


# ========================
# BASE DE DATOS
# ========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway',  # nombre de la base en Railway
        'USER': 'root',     # usuario root de Railway
        'PASSWORD': 'HXSuTsHHxupcqVUhbPiUAHJaXazlMpzz',  # tu MYSQL_ROOT_PASSWORD / MYSQLPASSWORD
        'HOST': 'yamanote.proxy.rlwy.net',  # dominio público que te da Railway
        'PORT': '37264',    # puerto público que te da Railway
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}


# ========================
# CONTRASEÑAS
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ========================
# IDIOMA Y ZONA HORARIA
# ========================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Mendoza'
USE_I18N = True
USE_TZ = True


# ========================
# ARCHIVOS ESTÁTICOS
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ========================
# CORS (para conectar con Netlify)
# ========================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://bitforce-gym.netlify.app",  # dominio de tu frontend
    "http://localhost:3000",             # entorno local
]


# ========================
# DRF + JWT
# ========================
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}


# ========================
# USUARIO PERSONALIZADO
# ========================
AUTH_USER_MODEL = 'AccountAdmin.GymUser'
