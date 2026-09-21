"""
Django settings - Sistem Penilaian Esai Otomatis Berbasis SBERT
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-env")
DEBUG = config("DJANGO_DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    # local apps
    "apps.users",
    "apps.master_data",
    "apps.knowledge_base",
    "apps.questions",
    "apps.exams",
    "apps.answers",
    "apps.scoring",
    "apps.activity_logs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="esai_db"),
        "USER": config("POSTGRES_USER", default="esai_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="esai_pass"),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "users.User"

AUTHENTICATION_BACKENDS = [
    "apps.users.auth_backends.EmailCredentialBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
]

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF & JWT ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# --- Scoring parameters (bagian 16 spesifikasi) ---
SBERT_MODEL = config("SBERT_MODEL", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# --- Chunking Knowledge Base (bagian 9) ---
KB_CHUNK_MAX_WORDS = config("KB_CHUNK_MAX_WORDS", default=150, cast=int)
KB_CHUNK_OVERLAP_WORDS = config("KB_CHUNK_OVERLAP_WORDS", default=30, cast=int)

SCORING = {
    "SEMANTIC_WEIGHT": config("SEMANTIC_WEIGHT", default=0.80, cast=float),
    "CONCEPT_WEIGHT": config("CONCEPT_WEIGHT", default=0.20, cast=float),
    "TOP_K": config("TOP_K", default=3, cast=int),
    "CONCEPT_THRESHOLD": config("CONCEPT_THRESHOLD", default=0.60, cast=float),
    "TEXT_MIN_WORDS": config("TEXT_MIN_WORDS", default=5, cast=int),
    "TEXT_MIN_ALPHA_RATIO": config("TEXT_MIN_ALPHA_RATIO", default=0.75, cast=float),
    "TEXT_MIN_VOWEL_RATIO": config("TEXT_MIN_VOWEL_RATIO", default=0.50, cast=float),
    "TEXT_MAX_UPPER_RATIO": config("TEXT_MAX_UPPER_RATIO", default=0.50, cast=float),
    "SEMANTIC_MIN_THRESHOLD": config("SEMANTIC_MIN_THRESHOLD", default=0.25, cast=float),
    "SEMANTIC_BASELINE": config("SEMANTIC_BASELINE", default=0.40, cast=float),
    "SEMANTIC_BELOW_BASELINE_MAX": config("SEMANTIC_BELOW_BASELINE_MAX", default=20, cast=float),
    "NOISE_PENALTY": config("NOISE_PENALTY", default=0.10, cast=float),
}
assert abs(SCORING["SEMANTIC_WEIGHT"] + SCORING["CONCEPT_WEIGHT"] - 1.0) < 1e-9, (
    "SEMANTIC_WEIGHT + CONCEPT_WEIGHT harus = 1.0"
)
assert 0 <= SCORING["SEMANTIC_MIN_THRESHOLD"] < SCORING["SEMANTIC_BASELINE"] < 1, (
    "Harus 0 <= SEMANTIC_MIN_THRESHOLD < SEMANTIC_BASELINE < 1"
)