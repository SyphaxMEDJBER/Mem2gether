from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-n^&6$qo8r#@ai5evtyt$5exb&i0oj+qqe1v4rf^-cmx99k+aof'
DEBUG = True

ALLOWED_HOSTS = []


# ===================== APPS =====================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps projet
    'authentification',
    'rooms',

    # Channels
    'channels',
]


# ===================== MIDDLEWARE =====================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]


# ===================== URLS / ASGI =====================

ROOT_URLCONF = 'application.urls'

ASGI_APPLICATION = "application.asgi.application"

WSGI_APPLICATION = 'application.wsgi.application'


# ===================== CHANNEL LAYERS =====================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# ===================== TEMPLATES =====================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # ton dossier templates/
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


# ===================== DATABASE =====================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ===================== PASSWORD VALIDATION =====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===================== LOCALISATION =====================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'

USE_I18N = True
USE_TZ = True


# ===================== STATIC =====================

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# ===================== MEDIA =====================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ===================== DJANGO DEFAULTS =====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===================== LOGIN / LOGOUT =====================

LOGIN_URL = 'signin'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'


# ===================== EMAIL SMTP =====================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'alaouisalma2002@gmail.com'
EMAIL_HOST_PASSWORD = 'xfrh ejck vgla hcil'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
