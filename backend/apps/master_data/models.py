from django.db import models

from apps.master_data.mixins import AuditModel, StatusAuditModel
from apps.users.models import User


class MasterKelas(StatusAuditModel):
    id = models.BigAutoField(primary_key=True)
    nama_kelas = models.CharField(max_length=100)
    tingkat = models.CharField(max_length=20)

    class Meta:
        db_table = "master_kelas"

    def __str__(self):
        return self.nama_kelas


class MasterJurusan(StatusAuditModel):
    id = models.BigAutoField(primary_key=True)
    kode_jurusan = models.CharField(max_length=20, unique=True)
    nama_jurusan = models.CharField(max_length=150)

    class Meta:
        db_table = "master_jurusan"

    def __str__(self):
        return self.kode_jurusan


class MasterSiswa(StatusAuditModel):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="siswa_profile")
    # String, bukan integer -- agar NISN berawalan 0 tidak hilang (bagian 5.1).
    nisn = models.CharField(max_length=20, unique=True)
    kelas = models.ForeignKey(MasterKelas, on_delete=models.PROTECT, related_name="siswa")
    jurusan = models.ForeignKey(MasterJurusan, on_delete=models.PROTECT, related_name="siswa")

    class Meta:
        db_table = "master_siswa"

    def __str__(self):
        return f"{self.user.nama} ({self.nisn})"


class MasterGuru(StatusAuditModel):
    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="guru_profile")
    nip = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = "master_guru"

    def __str__(self):
        return self.user.nama


class MasterAdmin(StatusAuditModel):
    """
    Tabel master khusus admin -- pola sama dengan master_guru/master_siswa,
    supaya akun admin juga punya baris profil terpisah dari tabel `users`
    (bukan cuma role='admin' tanpa data tambahan).
    """

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="admin_profile")
    jabatan = models.CharField(max_length=100, null=True, blank=True)  # misal "Kepala Tata Usaha"

    class Meta:
        db_table = "master_admin"

    def __str__(self):
        return self.user.nama
