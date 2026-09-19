"""Bagian 12: token 5 karakter huruf kapital, acak, unik untuk ujian aktif."""
import secrets
import string

from apps.exams.models import Ujian, UjianStatus

ALPHABET = string.ascii_uppercase  # hanya huruf kapital -- tidak mudah ditebak, tidak ambigu dgn digit


def generate_unique_token(max_attempts: int = 50) -> str:
    for _ in range(max_attempts):
        token = "".join(secrets.choice(ALPHABET) for _ in range(5))
        if not Ujian.objects.filter(token=token, status=UjianStatus.AKTIF).exists():
            return token
    raise RuntimeError("Gagal membuat token unik setelah beberapa percobaan.")
