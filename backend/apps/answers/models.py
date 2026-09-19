from django.db import models

from apps.exams.models import Ujian
from apps.master_data.models import MasterSiswa
from apps.questions.models import Soal


class Jawaban(models.Model):
    id = models.BigAutoField(primary_key=True)
    ujian = models.ForeignKey(Ujian, on_delete=models.PROTECT, related_name="jawaban_set")
    siswa = models.ForeignKey(MasterSiswa, on_delete=models.PROTECT, related_name="jawaban_set")
    soal = models.ForeignKey(Soal, on_delete=models.PROTECT, related_name="jawaban_set")
    jawaban_teks = models.TextField(blank=True, default="")
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jawaban"
        # Bagian 14 & 28: satu siswa hanya bisa punya satu jawaban untuk satu
        # soal pada satu ujian -- dijaga di level database, bukan cuma app.
        constraints = [
            models.UniqueConstraint(
                fields=["ujian", "siswa", "soal"], name="uniq_jawaban_ujian_siswa_soal"
            )
        ]

    def __str__(self):
        return f"jawaban#{self.id} ujian={self.ujian_id} siswa={self.siswa_id} soal={self.soal_id}"
