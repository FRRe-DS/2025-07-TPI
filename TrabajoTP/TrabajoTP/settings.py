"""
Django settings for TrabajoTP project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import jwt

load_dotenv()  # Cargar variables del archivo .env

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-x9wu4d!r_v((1rkmqpj#_p4gtsujfx&tybwbte-x!v_mzo(!vz'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Permite todos los hosts en desarrollo

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'corsheaders',
    'social_django',  # Para integración con Keycloak
    'portal_compras'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',  # Middleware para social auth
]

ROOT_URLCONF = 'TrabajoTP.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  # Context processor para social auth
                'social_django.context_processors.login_redirect',  # Context processor para redirects
            ],
        },
    },
]

WSGI_APPLICATION = 'TrabajoTP.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'portal_db'),
        'USER': os.getenv('DB_USER', 'portal_user'),
        'PASSWORD': os.getenv('DB_PASS', 'portal_password'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración Keycloak - usa localhost para el navegador
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL', 'http://localhost:8080')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'ds-2025-realm')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID', 'grupo-07')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET', 'tdSnJM8CsPPl6dJW4Tq6k9JWnSqndkfH')

# Configuración de Social Auth para Keycloak - usa localhost
SOCIAL_AUTH_KEYCLOAK_KEY = KEYCLOAK_CLIENT_ID
SOCIAL_AUTH_KEYCLOAK_SECRET = KEYCLOAK_CLIENT_SECRET
SOCIAL_AUTH_KEYCLOAK_AUTHORIZATION_URL = f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth'
SOCIAL_AUTH_KEYCLOAK_ACCESS_TOKEN_URL = f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token'
SOCIAL_AUTH_KEYCLOAK_USERINFO_URL = f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo'

# Configuración OAuth2 para Keycloak
AUTHENTICATION_BACKENDS = (
    'portal_compras.backends.CustomKeycloakOAuth2', 
    'django.contrib.auth.backends.ModelBackend',
)
KEYCLOAK_PUBLIC_KEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvRNUYBCIBoBLKvj9dFjHHhR3YCY93OkBQ/okdg5F1kRrXZOlHWoP1DLh4IYadr0DtlBWqQJWgzHr/Symo86F5f4mLqdiGX7zXoH6jvig8EX1fOF+tkXK4GeyEpPaU3FBHEoptSZGiHSQJhd2q1bPVwyh9LcsWdUktRUEhyJaa+kTQxLtt816dny9JpRgDt1JfZYNs9i66iqfBfGoF88Mf7z7QKKP9D9JlYHvnzKcqtSqUcW0T2QO195gBGV0hL/df1owBVC0CI1pKoddUZNAiEvUDk2OE7ERdcBy5YY04vwoP6EVrGJi3bYKrtkYZdmxj7obfgUhHSvuu2BwxpN1yQIDAQAB'
KEYCLOAK_PUBLIC_KEY = KEYCLOAK_PUBLIC_KEY
SOCIAL_AUTH_KEYCLOAK_SCOPE = ['openid']

# Deshabilitar verificación de aud claim
JWT_DECODE_OPTIONS = {
    "verify_aud": False,
    "verify_signature": False  # Temporalmente
}

# Deshabilitar verificaciones estrictas
SOCIAL_AUTH_SANITIZE_REDIRECTS = False
SOCIAL_AUTH_REDIRECT_IS_HTTPS = False

# Configuración general de Social Auth
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login-error/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'
SOCIAL_AUTH_USER_FIELDS = ['email', 'username']

# Pipeline para crear usuarios desde Keycloak
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'social_core.pipeline.user.user_details',
    'portal_compras.pipeline.get_email_from_keycloak',
)
SOCIAL_AUTH_KEYCLOAK_EXTRA_DATA = [
    ('email', 'email'),
    ('given_name', 'first_name'),
    ('family_name', 'last_name')
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
]

# Configuración OAuth2 Toolkit (para API)
OAUTH2_PROVIDER = {
    'SCOPES': {
        'read': 'Read scope',
        'write': 'Write scope',
        'groups': 'Access to your groups'
    },
    'ACCESS_TOKEN_EXPIRE_SECONDS': 36000,
}

OAUTH2_CLIENT_ID = 'wqfxWwrqNYA5ONIzZS0uzIfAuX73I1v7ApkovDFD'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

# Configuración de sesiones
SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hora

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'