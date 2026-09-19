from django.db import models

from apps.knowledge_base.models import KnowledgeBase
from apps.master_data.mixins import StatusAuditModel
from apps.master_data.models import MasterGuru


class Soal(StatusAuditModel):
    id = models.BigAutoField(primary_key=True)
    guru = models.ForeignKey(MasterGuru, on_delete=models.PROTECT, related_name="soal_list")
    pertanyaan = models.TextField()
    jawaban_acuan = models.TextField(blank=True, default="")
    knowledge_bases = models.ManyToManyField(
        KnowledgeBase, through="SoalKnowledgeBase", related_name="soal_list"
    )

    class Meta:
        db_table = "soal"

    def __str__(self):
        return self.pertanyaan[:60]

    @property
    def siap_dipakai(self) -> bool:
        """Bagian 10: minimal 1 CU + minimal 1 referensi KB yang sudah selesai diproses."""
        ada_cu = self.concept_units.exists()
        ada_kb_siap = self.knowledge_bases.filter(processing_status="done").exists()
        return ada_cu and ada_kb_siap


class SoalKnowledgeBase(models.Model):
    id = models.BigAutoField(primary_key=True)
    soal = models.ForeignKey(Soal, on_delete=models.CASCADE)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "soal_knowledge_base"
        unique_together = [("soal", "knowledge_base")]


class ConceptUnit(models.Model):
    id = models.BigAutoField(primary_key=True)
    soal = models.ForeignKey(Soal, on_delete=models.CASCADE, related_name="concept_units")
    konsep = models.TextField()
    urutan = models.PositiveIntegerField(default=0)
    bobot = models.FloatField(null=True, blank=True)  # null = bobot sama rata (bagian 10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "concept_units"
        ordering = ["soal_id", "urutan"]

    def __str__(self):
        return self.konsep[:60]
