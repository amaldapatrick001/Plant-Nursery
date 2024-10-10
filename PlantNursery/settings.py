import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Define environment variables directly
GOOGLE_OAUTH_CLIENT_ID = '130668388328-jkl8a6uqp9op73h46pff1401ab16vop5.apps.googleusercontent.com'
SECRET_KEY = 'django-insecure-_&b(9(a%^7)t%%&9ctl$)bb8t2mo1djy8#kc_szj7ss6v!ahpk'
DEBUG = True
DATABASE_NAME = 'Enchanted_Eden'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'Amalda@123'
EMAIL_HOST_USER = 'amaldapatrick2025@mca.ajce.in'  # Add your email host user here
EMAIL_HOST_PASSWORD = 'Amalda@MCA'

# Security settings
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Installed applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'userauths',
    'products',
]

# Middleware configurations
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'userauths.middleware.NoCacheMiddleware',  # Custom middleware to prevent caching
]

# URL configurations
ROOT_URLCONF = 'PlantNursery.urls'

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# WSGI application
WSGI_APPLICATION = 'PlantNursery.wsgi.application'

# Database configuration using PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE_NAME,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email backend configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = EMAIL_HOST_USER  # Use the defined EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Set to True for expiry on browser close

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site configuration
SITE_ID = 1
SITE_NAME = 'Enchanted Eden'
DOMAIN = 'localhost:8000'
PASSWORD_RESET_EMAIL_TEMPLATE = 'userauths/password_reset_email.html'

# Authentication settings
LOGIN_URL = '/userauths/login/'

# Cross-Origin and Referrer settings (for Google sign-in)
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
if not GOOGLE_OAUTH_CLIENT_ID:
    raise ValueError('GOOGLE_OAUTH_CLIENT_ID is missing. Please add it to your .env file.')

