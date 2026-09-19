from rest_framework import serializers

from apps.scoring.models import Penilaian, PenilaianConceptUnit


class PenilaianConceptUnitSerializer(serializers.ModelSerializer):
    konsep = serializers.CharField(source="concept_unit.konsep", read_only=True)

    class Meta:
        model = PenilaianConceptUnit
        fields = ["concept_unit", "konsep", "similarity", "detected"]


class HasilGuruSerializer(serializers.ModelSerializer):
    """Bagian 24: detail lengkap untuk dashboard guru/admin."""

    nama_siswa = serializers.CharField(source="jawaban.siswa.user.nama", read_only=True)
    nisn = serializers.CharField(source="jawaban.siswa.nisn", read_only=True)
    kelas = serializers.CharField(source="jawaban.siswa.kelas.nama_kelas", read_only=True)
    jurusan = serializers.CharField(source="jawaban.siswa.jurusan.nama_jurusan", read_only=True)
    nama_ujian = serializers.CharField(source="jawaban.ujian.nama_ujian", read_only=True)
    jenis_ujian = serializers.CharField(source="jawaban.ujian.jenis_ujian", read_only=True)
    pertanyaan = serializers.CharField(source="jawaban.soal.pertanyaan", read_only=True)
    jawaban_teks = serializers.CharField(source="jawaban.jawaban_teks", read_only=True)
    knowledge_base_terkait = serializers.SerializerMethodField()
    detail_cu = PenilaianConceptUnitSerializer(many=True, read_only=True)

    class Meta:
        model = Penilaian
        fields = [
            "id", "nama_siswa", "nisn", "kelas", "jurusan", "nama_ujian", "jenis_ujian",
            "pertanyaan", "jawaban_teks", "knowledge_base_terkait",
            "semantic_raw", "semantic_score", "concept_score", "detail_cu",
            "relevance_status", "text_quality_status", "noise_penalty_applied",
            "final_score", "feedback", "processing_status", "processing_error",
        ]

    def get_knowledge_base_terkait(self, obj):
        return list(obj.jawaban.soal.knowledge_bases.values_list("judul", flat=True))


class HasilSiswaSerializer(serializers.ModelSerializer):
    """Bagian 7 & 23: siswa hanya lihat setelah dipublikasikan -- tanpa detail internal guru."""

    pertanyaan = serializers.CharField(source="jawaban.soal.pertanyaan", read_only=True)
    jawaban_teks = serializers.CharField(source="jawaban.jawaban_teks", read_only=True)

    class Meta:
        model = Penilaian
        fields = ["id", "pertanyaan", "jawaban_teks", "final_score", "feedback"]
