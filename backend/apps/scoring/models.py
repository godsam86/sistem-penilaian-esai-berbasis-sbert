from django.db import models

from apps.answers.models import Jawaban
from apps.questions.models import ConceptUnit


class ProcessingStatus(models.TextChoices):
    SUCCESS = "success", "Berhasil"
    FAILED = "failed", "Gagal Diproses"


class Penilaian(models.Model):
    id = models.BigAutoField(primary_key=True)
    jawaban = models.OneToOneField(Jawaban, on_delete=models.PROTECT, related_name="penilaian")

    semantic_raw = models.FloatField(null=True, blank=True)      # cosine similarity mentah rata-rata top-K
    semantic_score = models.FloatField(null=True, blank=True)    # hasil kalibrasi 0-100
    concept_score = models.FloatField(null=True, blank=True)     # 0-100
    final_score = models.FloatField(null=True, blank=True)       # 0-100

    feedback = models.TextField(blank=True, default="")
    relevance_status = models.CharField(max_length=20, blank=True, default="")     # lolos/gagal
    text_quality_status = models.CharField(max_length=20, blank=True, default="")  # lolos/gagal
    noise_penalty_applied = models.BooleanField(default=False)

    model_version = models.CharField(max_length=100, blank=True, default="")
    scoring_version = models.CharField(max_length=20, blank=True, default="")

    # Usulan tambahan (dijelaskan di Tahap 2): error pemrosesan TIDAK BOLEH
    # otomatis jadi skor 0 (bagian 21) -- harus bisa ditandai gagal + retry.
    processing_status = models.CharField(
        max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.SUCCESS
    )
    processing_error = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "penilaian"

    def __str__(self):
        return f"penilaian#{self.id} jawaban={self.jawaban_id} skor={self.final_score}"


class PenilaianConceptUnit(models.Model):
    id = models.BigAutoField(primary_key=True)
    penilaian = models.ForeignKey(Penilaian, on_delete=models.CASCADE, related_name="detail_cu")
    concept_unit = models.ForeignKey(ConceptUnit, on_delete=models.PROTECT)
    similarity = models.FloatField()
    detected = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "penilaian_concept_unit"
        unique_together = [("penilaian", "concept_unit")]
