
import os
from decouple import config, Csv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPLICATION_DIR = os.path.dirname(globals()['__file__'])

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), ".."),
)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Application definition

# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
INSTALLED_APPS = [

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',
    'django_celery_beat',
    'django_nvd3',
    'djangobower',
    # Any apps which will override adminlte's templates (i.e. your apps)
    'reports',

    # The general purpose templates
    'django_adminlte',

    # Optional: Skin for the admin interface
    'django_adminlte_theme',

    # Any apps which need to have their templates overridden by adminlte
    'django.contrib.admin',

]

MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # This must be first on the list
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # This must be last
]

ROOT_URLCONF = 'analyticreports.urls'

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

WSGI_APPLICATION = 'analyticreports.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {

        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': '',
        'HOST': '',

    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Kampala'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'

# noinspection PyUnresolvedReferences
BOWER_COMPONENTS_ROOT = os.path.join(APPLICATION_DIR, 'components')
BOWER_PATH = '/usr/local/bin/bower'

# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
]

# noinspection PyUnresolvedReferences,PyUnresolvedReferences
BOWER_INSTALLED_APPS = [
    'jquery',
    'underscore',
    'd3',
    'nvd3'
]

# noinspection PyUnresolvedReferences
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#  For Gmail or Google Apps
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config(
    'EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')


CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'localhost:6379',
    },
}
