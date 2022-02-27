"""
Django settings for SFNewsPortal project.

Generated by 'django-admin startproject' using Django 3.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
from pathlib import Path
from news.mail_pass import mail_pass
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import news.apps


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4&0x5w2&cb11-0nv%c0gwwz&l=mkp2q-1qmbp%j_m*$t9x4y@2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']
SITE_ID = 1

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# CELERY/REDIS

# вариант для локального редиса под WLS
# CELERY_BROKER_URL = 'redis://localhost:6379'  # URL брокера сообщений (Redis).
# CELERY_RESULT_BACKEND = 'redis://localhost:6379'  # хранилище результатов выполнения задач

# Вариант для облачного редиса
# формат: redis://юзернейм(у_нас_тут_пустой):пароль@эндпоинт:порт/0
CELERY_BROKER_URL = 'redis://:FaUmx3YAWwHTqMcRhKSithVxmSP2hPew@redis-14990.c293.eu-central-1-1.ec2.cloud.redislabs.com:14990/0'
CELERY_RESULT_BACKEND = 'redis://:FaUmx3YAWwHTqMcRhKSithVxmSP2hPew@redis-14990.c293.eu-central-1-1.ec2.cloud.redislabs.com:14990/0'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache_files'),  # Указываем, куда будем сохранять кэшируемые файлы! Не забываем создать папку cache_files внутри папки с manage.py!
    }
}


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_FORMS = {'signup': 'sign.forms.BasicSignupForm'}

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

# EMAIL CONFIG
EMAIL_FROM = 'dek18@yandex.ru'

EMAIL_HOST = 'smtp.yandex.ru'  # адрес сервера Яндекс-почты для всех один и тот же
EMAIL_PORT = 465  # порт smtp сервера тоже одинаковый
EMAIL_HOST_USER = 'dekonstantin18'  # имя пользователя
EMAIL_HOST_PASSWORD = mail_pass  # пароль от почты
EMAIL_USE_SSL = True  # Яндекс использует ssl

# APSCHEDULER SETTINGS
# формат даты, которую будет воспринимать наш задачник (вспоминаем модуль по фильтрам)
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

# если задача не выполняется за 25 секунд, то она автоматически снимается
APSCHEDULER_RUN_NOW_TIMEOUT = 25  # Seconds


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # подключаем статические страницы для шаблонов
    'django.contrib.sites',
    'django.contrib.flatpages',

    # добавляем фильтры
    'django_filters',

    # подключаем наше приложение новостей и статей
    # (автоматом при создании проекта создалось в данном случае)
    # тут же подключаются сигналы (они в ready внутри NewsConfig прописаны)
    'news.apps.NewsConfig',

    # приложение для авторизации
    # хотя фактически сейчас используется allauth
    'sign',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # providers you want to enable:
    'allauth.socialaccount.providers.google',

    # модуль для периодических задач
    'django_apscheduler',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # для подключения статических страниц
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'sf_news_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'sf_news_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'time-lvl-msg': {
            'format': '{asctime} {levelname} {message}',
            'style': '{',
        },
        'time-lvl-path-msg': {
            'format': '{asctime} {levelname} {pathname} {message}',
            'style': '{',
        },
        'time-lvl-path-msg-stack': {
            'format': '{asctime} {levelname} {pathname} {exc_info} {message}',
            'style': '{',
        },
        'time-lvl-mod-msg': {
            'format': '{asctime} {levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console-debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'time-lvl-msg'
        },
        'console-warn': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'time-lvl-path-msg'
        },
        'console-err': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'time-lvl-path-msg-stack'
        },
        'general-info-log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'time-lvl-mod-msg',
            'filters': ['require_debug_false'],
            'filename': 'general.log'
        },
        'security-log': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'time-lvl-mod-msg',
            'filename': 'security.log'
        },
        'error-log': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'formatter': 'time-lvl-path-msg-stack',
            'filename': 'errors.log'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'time-lvl-path-msg'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console-debug', 'console-warn', 'console-err', 'general-info-log'],
            'propagate': True
        },
        'django.security': {
            'handlers': ['security-log'],
        },
        'django.request': {
            'handlers': ['mail_admins', 'error-log'],
            'level': 'ERROR',
        },
        'django.server': {
            'handlers': ['error-log'],
            'level': 'ERROR',
        },
        'django.template': {
            'handlers': ['error-log'],
            'level': 'ERROR',
        },
        'django.db_backends': {
            'handlers': ['error-log'],
            'level': 'ERROR',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
}
