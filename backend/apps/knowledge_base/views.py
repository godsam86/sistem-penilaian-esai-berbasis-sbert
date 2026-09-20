from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.activity_logs.utils import log_activity
from apps.knowledge_base.models import KbChunk, KnowledgeBase
from apps.knowledge_base.processing import process_knowledge_base
from apps.knowledge_base.serializers import (
    KbChunkCurationSerializer,
    KnowledgeBaseDetailSerializer,
    KnowledgeBaseSerializer,
)
from apps.knowledge_base.services.embedding import embed_text
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

    @action(detail=True, methods=["get"], url_path="chunks")
    def chunks(self, request, pk=None):
        """Kurasi: lihat seluruh chunk milik Knowledge Base ini (bagian 9, atas permintaan Anda)."""
        kb = self.get_object()
        data = KbChunkCurationSerializer(kb.chunks.all().order_by("chunk_index"), many=True).data
        return Response(data)

    @action(detail=True, methods=["patch", "delete"], url_path=r"chunks/(?P<chunk_id>[^/.]+)")
    def chunk_detail(self, request, pk=None, chunk_id=None):
        """
        Kurasi manual per chunk:
        - PATCH: ubah isi teks chunk, lalu embedding chunk itu DIBUAT ULANG (bukan seluruh KB).
        - DELETE: hapus chunk ini saja dari Knowledge Base (tidak memicu reprocess KB penuh).
        """
        kb = self.get_object()
        chunk = get_object_or_404(KbChunk, pk=chunk_id, knowledge_base=kb)

        if request.method == "DELETE":
            chunk.delete()
            log_activity(request.user, "hapus_chunk", "knowledge_base", f"kb={kb.pk} chunk={chunk_id}", request)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = KbChunkCurationSerializer(chunk, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Konten berubah -> embedding chunk INI SAJA dibuat ulang (bukan seluruh KB direset).
        chunk.embedding = embed_text(chunk.content)
        chunk.save(update_fields=["content", "embedding", "updated_at"])
        log_activity(request.user, "kurasi_chunk", "knowledge_base", f"kb={kb.pk} chunk={chunk_id}", request)
        return Response(KbChunkCurationSerializer(chunk).data)
