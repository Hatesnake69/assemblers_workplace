"""
Django settings for assemblers_workplace project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
import pytz as pytz
import yaml
from dotenv import load_dotenv
from pydantic.dataclasses import dataclass

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3#sh#qmzp%!!s14411f4hjz82o&p!@=y-j^ph#)8ppc=o=atja"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "nested_admin",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.ip_whitelist_middleware.WhitelistMiddleware",
]

ROOT_URLCONF = "assemblers_workplace.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates/")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "assemblers_workplace.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


class Settings:
    user: str = os.getenv("POSTGRES_USER")
    password: str = os.getenv("POSTGRES_PASSWORD")
    host: str = os.getenv("POSTGRES_HOST")
    port: str = os.getenv("POSTGRES_PORT")
    name: str = os.getenv("POSTGRES_NAME")

    timezone = pytz.timezone(os.getenv("TZ"))

    get_wb_new_orders_url = os.getenv("GET_WB_NEW_ORDERS_URL")
    post_wb_new_supply_url = os.getenv("POST_WB_NEW_SUPPLY_URL")
    get_mapping_url = os.getenv("GET_MAPPING_URL")
    get_product_info_url = os.getenv("GET_PRODUCT_INFO_URL")

    ms_token: str = os.getenv("MS_TOKEN")


@dataclass
class IpConfig:
    name: str
    ip: str


@dataclass
class AccountWarehouse:
    name: str
    id: str


@dataclass
class AccountConfig:
    name: str
    wb_token: str
    warehouses: list[AccountWarehouse]


@dataclass
class Config:
    allowed_ips: list[IpConfig]
    accounts: list[AccountConfig]


with open("config.yaml", "r") as file:
    config_data = yaml.safe_load(file)

config = Config(**config_data)
settings = Settings()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": settings.name,
        "USER": settings.user,
        "PASSWORD": settings.password,
        "HOST": settings.host,
        "PORT": settings.port,
    }
}

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"  # URL-префикс для медиа-файлов
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
