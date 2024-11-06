import os
import dj_database_url
from pathlib import Path
from decouple import config  # Import config from python-decouple
os.environ['PATH'] = r'E:\Files\GTK3-Runtime Win64\bin;' + os.environ['PATH']


# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Define environment variables directly
GOOGLE_OAUTH_CLIENT_ID = config('GOOGLE_OAUTH_CLIENT_ID')
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_USER = config('DATABASE_USER')
DATABASE_PASSWORD = config('DATABASE_PASSWORD')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Add your email host user here
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
CLIENT_SECRET = config('CLIENT_SECRET')
SOCIAL_AUTH_USER_MODEL = 'userauths.User_Reg'

# Security settings

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_OAUTH_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = CLIENT_SECRET
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
    'userauths.middleware.NoCacheMiddleware',  # Custom middleware to prevent caching
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# URL configurations
ROOT_URLCONF = 'PlantNursery.urls'
WSGI_APPLICATION = 'PlantNursery.wsgi.application'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'userauths.pipeline.custom_create_user',  # Make sure this function returns the correct response
    'userauths.pipeline.custom_login_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',

    'userauths.auth_pipelines.set_user_session',
    
)



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

# Database configuration using SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Enchanted Eden',
        'USER': 'postgres',
        'PASSWORD': 'Amalda@2002',  # Your actual PostgreSQL password
        'HOST': 'localhost',  # Try this instead of localhost
        'PORT': '5432',
    }
}

#
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(default='postgresql://enchnatededen_user:kkLlccBiPIAlJiIr8WhLcKKUhd72178E@dpg-cslaof68ii6s73d9cod0-a.oregon-postgres.render.com/enchnatededen')
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
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session expiry on every request
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

# Custom login URL
LOGIN_URL = '/userauths/login/'

# Referrer policy and cross-origin settings
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'



# settings.py

RAZORPAY_KEY_ID = "rzp_test_DRyi6K0A68qkc4"
RAZORPAY_KEY_SECRET = "3zvEn8RxuvCxgu8ATRny3g95"




# For development
ALLOWED_HOSTS = ['enchnated-eden.onrender.com', 'localhost', '127.0.0.1']

# For OAuth development
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'