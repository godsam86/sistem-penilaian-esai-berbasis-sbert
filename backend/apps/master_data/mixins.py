from django.db import models


class StatusChoices(models.IntegerChoices):
    NONAKTIF = 0, "Nonaktif"
    AKTIF = 1, "Aktif"


class AuditModel(models.Model):
    """
    Field audit standar dipakai di hampir semua tabel (bagian 26 spesifikasi).
    created_by/updated_by menyimpan id user (bukan FK ketat ke users, supaya
    baris tetap valid walau user pembuat kemudian dinonaktifkan).
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.BigIntegerField(null=True, blank=True)
    updated_by = models.BigIntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class StatusAuditModel(AuditModel):
    status = models.SmallIntegerField(choices=StatusChoices.choices, default=StatusChoices.AKTIF)

    class Meta:
        abstract = True
