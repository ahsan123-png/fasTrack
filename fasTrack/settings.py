from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d6l@z1cx37$)yic7q8s8fvg9)*4*9^(tg3ys^dtwz3z061z_a7'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ["*"]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userEx',
    'salesInvoice',
    'corsheaders',
    'schedule',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'fasTrack.urls'

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

WSGI_APPLICATION = 'fasTrack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STRIPE_SECRET_KEY = 'sk_test_51Pw4qzEnQNLsnCj1NLNJftCJaYhNo7ZYB2YntOJsO4OlQsscEdmZSCTRPlqBnnkFTKbs94g0bWQMXBsnizBzXdhh00lvuKtAqu' 
STRIPE_PUBLISHABLE_KEY = 'pk_test_51Pw4qzEnQNLsnCj14FKz4CjTGplHuZb9a72NWOEwOmhpfiHZ57RckjlZZusgcJYBk9OIDfvlUTtioU3pkFbTEdXt0075iT2P8j' 

# Email Handler
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.fastrakconnect.com'  # SMTP server
EMAIL_PORT = 465
EMAIL_USE_TLS = False  
EMAIL_USE_SSL = True  
EMAIL_HOST_USER = 'info@api.fastrakconnect.com' 
EMAIL_HOST_PASSWORD = 'k&u6?(meE7%' 
#add Cores settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",  # If you're using JWT or other tokens
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",  # If you're using CSRF tokens
    "x-requested-with",
]
GOOGLE_CLIENT_SECRETS_JSON = os.path.join(BASE_DIR, 'credentials', 'client_secret.json')
GOOGLE_REDIRECT_URI = "https://api.fastrakconnect.com/google-drive-callback/"
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # or your preferred broker
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'