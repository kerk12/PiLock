"""
Django settings for PiLock project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.utils.crypto import get_random_string
from django.core.urlresolvers import reverse_lazy

def writeNewSecretKey():
    fi = open(BASE_DIR+"/secret.key", "w")
    key = get_random_string(length=64, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)")
    fi.write(key)
    fi.close()
    os.chmod("secret.key", 400)
    return key


def getSecretKey():
    try:
        fi = open(BASE_DIR+"/secret.key", "r")
        key = fi.read()
        fi.close()
    except IOError:
        key = writeNewSecretKey()
    return key

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getSecretKey()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# HSTS: Change this to the max age defined by the server.
# Comment it to disable HSTS. (NOT recommended)
SECURE_HSTS_SECONDS = 63072000

# SSL Redirecting
# CAUTION: Needs to be set to True when using SSL. This will redirect all the traffic to HTTPS.
# Set to False when you are not using SSL.
SECURE_SSL_REDIRECT = True

# Secure session cookie
# Encrypts session cookies. Recommended: True
SESSION_COOKIE_SECURE = True


ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'AdminCP',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'PiLock.urls'

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

WSGI_APPLICATION = 'PiLock.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = '/var/www/PiLock/static/'
STATIC_URL = '/static/'

LOGIN_URL = reverse_lazy('ACP-Login')


def getServerVersion():
    version_object = open(BASE_DIR+"/main/resources/version.txt", "r")
    return version_object.read()


def getRoot():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    return root_dir

