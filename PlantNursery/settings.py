import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Now use the API_KEY in your requests

# Google Calendar Settings
GOOGLE_CALENDAR_CREDENTIALS_FILE = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE')

# Google Calendar Settings
GOOGLE_CALENDAR_SETTINGS = {
    'CLIENT_SECRETS_FILE': os.getenv('GOOGLE_CLIENT_SECRETS_FILE'),
    'TOKEN_FILE': os.path.join(BASE_DIR, 'qa_sessions', 'token.pickle'),
    'SCOPES': ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events'],
}
# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and Authentication
GOOGLE_OAUTH_CLIENT_ID = '130668388328-jkl8a6uqp9op73h46pff1401ab16vop5.apps.googleusercontent.com'
SECRET_KEY = 'django-insecure-_&b(9(a%^7)t%%&9ctl$)bb8t2mo1djy8#kc_szj7ss6v!ahpk'
DEBUG = True
CLIENT_SECRET = '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'
GOOGLE_OAUTH_REDIRECT_URI = 'http://localhost:8000/userauths/google/callback'  # Remove trailing slash
SITE_URL = 'http://localhost:8000'  # Base URL without trailing slash
# Database Configuration

GOOGLE_CALENDAR_CREDENTIALS = os.path.join(BASE_DIR, 'credentials/service-account-key.json')
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'EnchantedEden',
        'USER': 'postgres',
        'PASSWORD': 'Amalda@2002',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',  # Try 'prefer' or 'disable'
        },
    }
}


# Use Render Database URL if needed
# DATABASES['default'] = dj_database_url.config(
#     default='postgresql://enchnatededen_user:kkLlccBiPIAlJiIr8WhLcKKUhd72178E@dpg-cslaof68ii6s73d9cod0-a.oregon-postgres.render.com/enchnatededen'
# )


# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER="amaldapatrick2025@mca.ajce.in"
EMAIL_HOST_PASSWORD="gaeo uuau ymdg sebd"  # New app password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


# Installed applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',

    'core',
    'userauths',
    'products',
    'purchase',
    'social_django',
    'django_celery_beat',
    'widget_tweaks',
    'delivery',
    'blog',
    'qa_sessions',
    'disease_detection',
    

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

# URL configurations
ROOT_URLCONF = 'PlantNursery.urls'
WSGI_APPLICATION = 'PlantNursery.wsgi.application'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/userauths/login/'

# Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = GOOGLE_OAUTH_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = CLIENT_SECRET
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.event',
]

# Additional Social Auth Settings
SOCIAL_AUTH_LOGIN_ERROR_URL = '/userauths/login/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

# Session Settings for Google Auth
SESSION_COOKIE_SECURE = True  # For HTTPS
SESSION_COOKIE_SAMESITE = 'Lax'

# Template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',  # Add this line if not present
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'userauths.context_processors.expert_profile',
                'qa_sessions.context_processors.notifications_context',

            ],
        },
    },
]

# Static and Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

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

# Razorpay Configuration
RAZORPAY_KEY_ID = 'rzp_test_DRyi6K0A68qkc4'
RAZORPAY_KEY_SECRET = '3zvEn8RxuvCxgu8ATRny3g95'

# Allowed Hosts
ALLOWED_HOSTS = ['enchnated-eden.onrender.com', 'localhost', '127.0.0.1']

# Enable insecure transport for OAuth during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'userauths': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

