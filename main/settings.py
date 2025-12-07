import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY
# =============================================================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# Для локальной разработки принудительно добавляем localhost
env_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
if DEBUG:
    # При локальной разработке всегда добавляем localhost
    if 'localhost' not in env_hosts:
        env_hosts.append('localhost')
    if '127.0.0.1' not in env_hosts:
        env_hosts.append('127.0.0.1')

ALLOWED_HOSTS = env_hosts

# =============================================================================
# APPS
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'whitenoise.runserver_nostatic', # раскоментить перед продакшн
    'fotos',
]

MIDDLEWARE = [
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # раскоментить перед продакшн
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

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

WSGI_APPLICATION = 'main.wsgi.application'

# =============================================================================
# DATABASE
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_ROOT = '/app/media' # на деплой amvera
MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'  # локалка

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CSRF & SESSION CONFIGURATION
# =============================================================================
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # False для Amvera (нет HTTPS)
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
] + [
    f"http://{host}" for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
]

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False  # False для Amvera (нет HTTPS)

# =============================================================================
# SECURITY FOR PRODUCTION
# =============================================================================
# Смягченные настройки для Amvera
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Было 'DENY'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = False  # Важно: False для Amvera
SECURE_HSTS_SECONDS = 0  # Важно: 0 для Amvera (нет HTTPS)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# =============================================================================
# LOGGING
# =============================================================================
LOG_FILE = BASE_DIR / 'django.log'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': str(LOG_FILE),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# # =============================================================================
# # WHITENOISE SETTINGS
# # =============================================================================
# # WhiteNoise настройки для медиа файлов
# WHITENOISE_ROOT = MEDIA_ROOT
# WHITENOISE_MANIFEST_STATIC_FILES = True
# WHITENOISE_IMMUTABLE_CACHE = False  # Важно для медиа файлов

# # Настройки для статических файлов
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# ADDITIONAL SETTINGS
# =============================================================================
# Отключаем проверку реферера для Amvera
SECURE_REFERRER_POLICY = None

# Отключаем проверку Content-Type для статических файлов
SECURE_CONTENT_TYPE_NOSNIFF = True

# Настройки для загрузки файлов
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Отключаем проверку хоста при DEBUG=False (для Amvera)
if not DEBUG:
    # Разрешаем все хосты из ALLOWED_HOSTS
    pass