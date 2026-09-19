"""
Bootstrap akun admin pertama dari environment variable, supaya deployment
tidak butuh input interaktif `createsuperuser` (bagian 30).
Jalankan: python manage.py seed_admin
"""
from decouple import config
from django.core.management.base import BaseCommand

from apps.master_data.models import MasterAdmin
from apps.users.models import Role, Status, User


class Command(BaseCommand):
    help = "Membuat akun admin pertama (users + master_admin) dari env ADMIN_EMAIL/ADMIN_PASSWORD/ADMIN_NAMA jika belum ada."

    def handle(self, *args, **options):
        email = config("ADMIN_EMAIL", default="admin@sekolah.id")
        password = config("ADMIN_PASSWORD", default=None)
        nama = config("ADMIN_NAMA", default="Administrator")

        if not password:
            self.stdout.write(self.style.WARNING("ADMIN_PASSWORD tidak diset di .env -- dilewati."))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"Akun admin {email} sudah ada -- dilewati."))
            return

        user = User.objects.create_user(
            email=email, password=password, nama=nama,
            role=Role.ADMIN, status=Status.AKTIF, is_staff=True, is_superuser=True,
        )
        MasterAdmin.objects.create(user=user)
        self.stdout.write(self.style.SUCCESS(f"Akun admin {email} berhasil dibuat (users + master_admin)."))
