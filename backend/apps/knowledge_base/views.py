from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.activity_logs.utils import log_activity
from apps.knowledge_base.models import KnowledgeBase
from apps.knowledge_base.processing import process_knowledge_base
from apps.knowledge_base.serializers import (
    KnowledgeBaseDetailSerializer,
    KnowledgeBaseSerializer,
)
from apps.users.permissions import IsGuru


class KnowledgeBaseViewSet(viewsets.ModelViewSet):
    """Guru hanya mengelola Knowledge Base miliknya sendiri (bagian 8, 31)."""

    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsGuru]

    def get_queryset(self):
        return KnowledgeBase.objects.filter(guru=self.request.user.guru_profile).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return KnowledgeBaseDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        kb = serializer.save(guru=self.request.user.guru_profile, created_by=self.request.user.id)
        log_activity(self.request.user, "buat_kb", "knowledge_base", str(kb.pk), self.request)
        process_knowledge_base(kb)
        kb.refresh_from_db()

    def perform_update(self, serializer):
        kb = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_kb", "knowledge_base", str(kb.pk), self.request)
        # Materi berubah -> embedding harus diperbarui (bagian 9).
        process_knowledge_base(kb)
        kb.refresh_from_db()

    @action(detail=True, methods=["post"])
    def reprocess(self, request, pk=None):
        """Retry manual jika processing_status='failed' (bagian 21)."""
        kb = self.get_object()
        process_knowledge_base(kb)
        kb.refresh_from_db()
        log_activity(request.user, "reprocess_kb", "knowledge_base", str(kb.pk), request)
        return Response(KnowledgeBaseSerializer(kb).data)
