from rest_framework import serializers

from apps.knowledge_base.models import KbChunk, KnowledgeBase


class KbChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = KbChunk
        fields = ["id", "chunk_index", "content", "metadata"]
        # embedding sengaja tidak diekspos ke frontend -- data internal.


class KbChunkCurationSerializer(serializers.ModelSerializer):
    """Untuk kurasi manual: guru boleh mengedit isi sebuah chunk (bagian 9, atas permintaan Anda)."""

    class Meta:
        model = KbChunk
        fields = ["id", "chunk_index", "content"]
        read_only_fields = ["id", "chunk_index"]

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Isi chunk tidak boleh kosong.")
        return value


class KnowledgeBaseSerializer(serializers.ModelSerializer):
    jumlah_chunk = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = KnowledgeBase
        fields = [
            "id", "judul", "sumber", "teks", "file", "status",
            "processing_status", "processing_error", "jumlah_chunk",
            "created_at", "updated_at",
        ]
        read_only_fields = ["processing_status", "processing_error", "created_at", "updated_at"]

    def validate(self, attrs):
        sumber = attrs.get("sumber", getattr(self.instance, "sumber", None))
        file = attrs.get("file", getattr(self.instance, "file", None))
        teks = attrs.get("teks", getattr(self.instance, "teks", ""))
        if sumber == "text" and not teks:
            raise serializers.ValidationError("Teks wajib diisi jika sumber = text.")
        if sumber in ("pdf", "docx", "doc") and not file:
            raise serializers.ValidationError("File wajib diunggah untuk sumber ini.")
        return attrs


class KnowledgeBaseDetailSerializer(KnowledgeBaseSerializer):
    chunks = KbChunkSerializer(many=True, read_only=True)

    class Meta(KnowledgeBaseSerializer.Meta):
        fields = KnowledgeBaseSerializer.Meta.fields + ["chunks"]
