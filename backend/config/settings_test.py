"""
Override DB ke SQLite in-memory HANYA untuk menjalankan test secara lokal
tanpa perlu instance PostgreSQL. Produksi & development tetap pakai
settings.py (PostgreSQL) -- lihat bagian 30 spesifikasi.
Jalankan test dengan: python manage.py test --settings=config.settings_test
"""
from config.settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
