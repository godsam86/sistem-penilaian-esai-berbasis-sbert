from django.db import models

from apps.master_data.mixins import AuditModel
from apps.master_data.models import MasterGuru, MasterJurusan, MasterKelas
from apps.questions.models import Soal


class UjianStatus(models.TextChoices):
    AKTIF = "aktif", "Aktif"
    NONAKTIF = "nonaktif", "Nonaktif"
    SELESAI = "selesai", "Selesai"


class Ujian(AuditModel):
    id = models.BigAutoField(primary_key=True)
    nama_ujian = models.CharField(max_length=255)
    jenis_ujian = models.CharField(max_length=50)  # UTS/UAS/Ulangan Harian/dst -- teks bebas
    guru = models.ForeignKey(MasterGuru, on_delete=models.PROTECT, related_name="ujian_list")
    kelas = models.ForeignKey(MasterKelas, on_delete=models.PROTECT, related_name="ujian_list")
    jurusan = models.ForeignKey(MasterJurusan, on_delete=models.PROTECT, related_name="ujian_list")
    token = models.CharField(max_length=5)
    status = models.CharField(max_length=20, choices=UjianStatus.choices, default=UjianStatus.AKTIF)
    hasil_published = models.BooleanField(default=False)

    soal_list = models.ManyToManyField(Soal, through="UjianSoal", related_name="ujian_list")

    class Meta:
        db_table = "ujian"
        constraints = [
            # Token unik HANYA di antara ujian yang statusnya aktif (bagian 12).
            models.UniqueConstraint(
                fields=["token"],
                condition=models.Q(status="aktif"),
                name="uniq_token_ujian_aktif",
            )
        ]

    def __str__(self):
        return f"{self.nama_ujian} [{self.token}]"


class UjianSoal(models.Model):
    id = models.BigAutoField(primary_key=True)
    ujian = models.ForeignKey(Ujian, on_delete=models.CASCADE)
    soal = models.ForeignKey(Soal, on_delete=models.PROTECT)
    urutan = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ujian_soal"
        unique_together = [("ujian", "soal")]
        ordering = ["ujian_id", "urutan"]
