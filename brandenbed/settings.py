# brandenbed/settings.py
import os
from pathlib import Path
from decouple import config
import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    os.getenv('RENDER_EXTERNAL_HOSTNAME', ''),  # Render auto injects this
]
# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
]

LOCAL_APPS = [
    'core',
    'accounts',
    'dashboard',
    'employees',
    'properties',
    'landlords',
    'residents',
    'leads',
    'payments',
    'support',
    'maintenance',
    'housekeeping',
    'reports'
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'brandenbed.urls'

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
                'core.context_processors.company_info',
                'django.template.context_processors.i18n',  # For language support
            ],
        },
    },
]

WSGI_APPLICATION = 'brandenbed.wsgi.application'

# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}
# Password validation
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

AUTH_USER_MODEL = 'accounts.User'

# Internationalization
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Languages for multilingual support
LANGUAGES = [
    ('en', 'English'),
    ('de', 'Deutsch'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# # settings.py
# STATIC_URL = "/static/"

# STATICFILES_DIRS = [
#     BASE_DIR / "static",   # your single shared folder
# ]


# # only for deployment, not dev
# STATIC_ROOT = BASE_DIR / "staticfiles"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


COMPRESS_ROOT = BASE_DIR / 'static'

COMPRESS_ENABLED = True

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",  # if you still need it
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login/Logout URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_USE_TLS = 'True'
EMAIL_HOST_USER = 'initcore25@gmail.com'
EMAIL_HOST_PASSWORD = 'lnlfvjlp wpderjya'
DEFAULT_FROM_EMAIL = 'no-reply@brandenbed.com'



# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # or 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (for "remember me")
SESSION_COOKIE_SECURE = not DEBUG  # Secure cookies in production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Allow persistent sessions

# For additional security
SESSION_SAVE_EVERY_REQUEST = False



# Company information
COMPANY_NAME = 'Your Company Name'
COMPANY_PHONE = '+49 30 12345678'
COMPANY_EMAIL = 'info@company.com'
COMPANY_ADDRESS = '123 Main Street, 10115 Berlin, Germany'
CONTACT_EMAIL = 'contact@company.com'  # For receiving contact form submissions

