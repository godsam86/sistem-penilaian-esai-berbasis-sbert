from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    GURU = "guru", "Guru"
    SISWA = "siswa", "Siswa"


class Status(models.IntegerChoices):
    NONAKTIF = 0, "Nonaktif"
    AKTIF = 1, "Aktif"


class UserManager(BaseUserManager):
    """
    Manager kustom. Login siswa memakai NISN sebagai kredensial kedua
    (bukan password acak), tapi identitas login (username field) tetap
    email untuk SEMUA role -- role ditentukan backend, tidak dipercaya
    dari input frontend. Lihat apps/users/auth_backends.py.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email wajib diisi")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("status", Status.AKTIF)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Tabel `users`. HANYA menangani akun/autentikasi/role/identitas dasar.
    Data spesifik siswa/guru ada di master_siswa / master_guru (relasi 1-1).
    """

    id = models.BigAutoField(primary_key=True)
    nama = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.AKTIF)

    # Wajib untuk kompatibilitas Django admin/permissions minimal.
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nama", "role"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.nama} ({self.role})"

    @property
    def is_active(self):
        # Dipakai Django auth machinery: akun status=0 tidak boleh lolos autentikasi.
        return self.status == Status.AKTIF

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
