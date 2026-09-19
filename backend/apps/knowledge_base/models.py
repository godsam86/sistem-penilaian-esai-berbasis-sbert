from django.db import models

from apps.master_data.mixins import AuditModel
from apps.master_data.models import MasterGuru


class ProcessingStatus(models.TextChoices):
    PENDING = "pending", "Menunggu"
    PROCESSING = "processing", "Diproses"
    DONE = "done", "Selesai"
    FAILED = "failed", "Gagal"
    NEEDS_OCR = "needs_ocr", "Butuh OCR"


class KnowledgeBase(AuditModel):
    STATUS_AKTIF = 1
    STATUS_NONAKTIF = 0

    id = models.BigAutoField(primary_key=True)
    judul = models.CharField(max_length=255)
    sumber = models.CharField(max_length=50)  # 'pdf' | 'docx' | 'text'
    teks = models.TextField(blank=True, default="")
    file = models.FileField(upload_to="knowledge_base/", null=True, blank=True)
    guru = models.ForeignKey(MasterGuru, on_delete=models.PROTECT, related_name="knowledge_bases")
    status = models.SmallIntegerField(default=STATUS_AKTIF)
    processing_status = models.CharField(
        max_length=20, choices=ProcessingStatus.choices, default=ProcessingStatus.PENDING
    )
    processing_error = models.TextField(blank=True, default="")

    class Meta:
        db_table = "knowledge_base"

    def __str__(self):
        return self.judul


class KbChunk(models.Model):
    id = models.BigAutoField(primary_key=True)
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.IntegerField()
    content = models.TextField()
    # Bagian 7: embedding disimpan sebagai list float (JSON) -- keputusan Anda,
    # tanpa pgvector. Similarity dihitung di Python/numpy (apps/scoring).
    embedding = models.JSONField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "kb_chunks"
        unique_together = [("knowledge_base", "chunk_index")]
        ordering = ["knowledge_base_id", "chunk_index"]

    def __str__(self):
        return f"{self.knowledge_base_id}#{self.chunk_index}"
