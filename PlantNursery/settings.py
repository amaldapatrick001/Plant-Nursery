import os
from pathlib import Path
import dj_database_url

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and Authentication
GOOGLE_OAUTH_CLIENT_ID = '130668388328-jkl8a6uqp9op73h46pff1401ab16vop5.apps.googleusercontent.com'
SECRET_KEY = 'django-insecure-_&b(9(a%^7)t%%&9ctl$)bb8t2mo1djy8#kc_szj7ss6v!ahpk'
DEBUG = True
CLIENT_SECRET = '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'

# Database Configuration
DATABASE_NAME = 'Enchanted_Eden'
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'Amalda@2002'

# Email Configuration
EMAIL_HOST_USER = 'amaldapatrick2025@mca.ajce.in'
EMAIL_HOST_PASSWORD = 'Amalda@MCA'

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
    'purchase',
    'social_django',
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Middleware configurations
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'userauths.middleware.NoCacheMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# URLs and WSGI configuration
ROOT_URLCONF = 'PlantNursery.urls'
WSGI_APPLICATION = 'PlantNursery.wsgi.application'

# Social Auth Settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_OAUTH_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = CLIENT_SECRET

# Static and Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Database configuration
DATABASES = {
    'default': dj_database_url.config(default='postgresql://enchnatededen_user:kkLlccBiPIAlJiIr8WhLcKKUhd72178E@dpg-cslaof68ii6s73d9cod0-a.oregon-postgres.render.com/enchnatededen')
}

# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Login settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/userauths/login/'

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Razorpay
RAZORPAY_KEY_ID = 'rzp_test_DRyi6K0A68qkc4'
RAZORPAY_KEY_SECRET = '3zvEn8RxuvCxgu8ATRny3g95'

# Allowed Hosts for deployment
ALLOWED_HOSTS = ['enchnated-eden.onrender.com', 'localhost', '127.0.0.1']

# OAuth Development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
