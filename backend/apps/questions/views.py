from rest_framework import viewsets

from apps.activity_logs.utils import log_activity
from apps.questions.models import Soal
from apps.questions.serializers import SoalSerializer
from apps.users.permissions import IsGuru


class SoalViewSet(viewsets.ModelViewSet):
    """Guru hanya mengelola soal miliknya sendiri (bagian 8, 31)."""

    serializer_class = SoalSerializer
    permission_classes = [IsGuru]

    def get_queryset(self):
        return (
            Soal.objects.filter(guru=self.request.user.guru_profile)
            .prefetch_related("concept_units", "knowledge_bases")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        soal = serializer.save(guru=self.request.user.guru_profile, created_by=self.request.user.id)
        log_activity(self.request.user, "buat_soal", "soal", str(soal.pk), self.request)

    def perform_update(self, serializer):
        soal = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_soal", "soal", str(soal.pk), self.request)
