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
GOOGLE_CALENDAR_SETTINGS = {
    'CLIENT_SECRETS_FILE': os.path.join(BASE_DIR, 'qa_sessions', 'client_secret.json'),
    'TOKEN_FILE': os.path.join(BASE_DIR, 'qa_sessions', 'token.pickle'),
    'SCOPES': [os.getenv('GOOGLE_CALENDAR_SCOPES')],
}
# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Security and Authentication
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
SECRET_KEY = 'django-insecure-_&b(9(a%^7)t%%&9ctl$)bb8t2mo1djy8#kc_szj7ss6v!ahpk'
DEBUG = os.getenv('DEBUG') == 'True'
CLIENT_SECRET = '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'
GOOGLE_OAUTH_REDIRECT_URI = os.getenv('GOOGLE_OAUTH_REDIRECT_URI')
SITE_URL = os.getenv('SITE_URL')
# Database Configuration

GOOGLE_CALENDAR_CREDENTIALS = os.path.join(BASE_DIR, 'credentials/service-account-key.json')

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv('DB_HOST'),
#         'PORT': os.getenv('DB_PORT'),
#         'OPTIONS': {
#             'sslmode': 'prefer',  # Try 'prefer' or 'disable'
#         },
#     }
# }





DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://enchnatededen_gibv_user:Xb9ZFFXUZAXrPeoYxLfnLQ3frsjugCB6@dpg-cv27v9dds78s73e6m4og-a.oregon-postgres.render.com/enchnatededen_gibv',
        conn_max_age=600,
        ssl_require=True
    )
}
# # Use Render Database URL if needed
# if os.getenv('DATABASE_URL'):
#     DATABASES['default'] = dj_database_url.config(
#         default=os.getenv('DATABASE_URL')
#     )

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
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
    'django_extensions',
     'whitenoise.runserver_nostatic', 
    # 'chatterbot.ext.django_chatterbot',

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
    'expert_QA_session',
    'channels',
    # 'solar_forecast',
    # 'pdd',
    'chatbot',
    'plant_layout',
]


ASGI_APPLICATION = 'PlantNursery.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
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
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('CLIENT_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPES', 'email,profile').split(',')

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
SITE_NAME = os.getenv('SITE_NAME')
DOMAIN = os.getenv('DOMAIN')
PASSWORD_RESET_EMAIL_TEMPLATE = 'userauths/password_reset_email.html'

# Razorpay Configuration
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')

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

# Get API keys from environment variables
GEMINI_API_KEY = "AIzaSyBMzsJbJhAmKsc5EOdvWzJ24QIDcU4YxT8"
OPENWEATHER_API_KEY = "0acebc8791d9539d4e0b68f7262d10b6"

# Add validation to ensure keys are present
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in environment variables")

# Weather API Key
OPENWEATHERMAP_API_KEY = "0acebc8791d9539d4e0b68f7262d10b6"

# AI Recommendation Settings
AI_RECOMMENDATION_SETTINGS = {
    'MIN_MATCH_SCORE': 50,
    'MAX_RECOMMENDATIONS': 8,
    'UPDATE_INTERVAL_HOURS': 1
}