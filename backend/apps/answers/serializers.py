from rest_framework import serializers

from apps.answers.models import Jawaban
from apps.exams.models import Ujian
from apps.questions.models import Soal


class JawabanSubmitSerializer(serializers.Serializer):
    """
    Bagian 12: setiap pengiriman jawaban tetap wajib menyertakan & memverifikasi
    token, bukan hanya sekali di awal -- token bukan pengganti autentikasi,
    tapi tetap bagian dari pengecekan di setiap request penting.
    """

    ujian_id = serializers.PrimaryKeyRelatedField(queryset=Ujian.objects.all())
    soal_id = serializers.PrimaryKeyRelatedField(queryset=Soal.objects.all())
    token = serializers.CharField(max_length=5)
    jawaban_teks = serializers.CharField(allow_blank=True, trim_whitespace=False)


class JawabanSerializer(serializers.ModelSerializer):
    pertanyaan = serializers.CharField(source="soal.pertanyaan", read_only=True)
    final_score = serializers.FloatField(source="penilaian.final_score", read_only=True, default=None)
    feedback = serializers.CharField(source="penilaian.feedback", read_only=True, default="")

    class Meta:
        model = Jawaban
        fields = [
            "id", "ujian", "soal", "pertanyaan", "jawaban_teks",
            "submitted_at", "final_score", "feedback",
        ]
        read_only_fields = fields
