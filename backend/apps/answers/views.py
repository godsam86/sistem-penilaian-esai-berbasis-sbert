from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.activity_logs.utils import log_activity
from apps.answers.models import Jawaban
from apps.answers.serializers import JawabanSerializer, JawabanSubmitSerializer
from apps.exams.models import UjianStatus
from apps.scoring.services.pipeline import score_jawaban
from apps.users.permissions import IsSiswa


class SubmitJawabanView(APIView):
    """
    Bagian 7 & 14: satu kali pengumpulan per siswa per soal per ujian, jawaban
    yang sudah dikumpulkan tidak dapat diubah. Setelah submit, penilaian
    otomatis langsung berjalan sinkron (bagian 15, tanpa Celery).
    """

    permission_classes = [IsSiswa]

    def post(self, request):
        serializer = JawabanSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        siswa = request.user.siswa_profile
        ujian = data["ujian_id"]
        soal = data["soal_id"]

        # Bagian 12: verifikasi token, status ujian, kelas, jurusan di SETIAP request penting.
        if ujian.status != UjianStatus.AKTIF:
            return Response({"detail": "Ujian tidak aktif."}, status=status.HTTP_403_FORBIDDEN)
        if ujian.token != data["token"].upper():
            return Response({"detail": "Token tidak valid."}, status=status.HTTP_403_FORBIDDEN)
        if ujian.kelas_id != siswa.kelas_id or ujian.jurusan_id != siswa.jurusan_id:
            return Response({"detail": "Ujian ini bukan untuk kelas/jurusan Anda."}, status=status.HTTP_403_FORBIDDEN)
        if not ujian.soal_list.filter(pk=soal.pk).exists():
            return Response({"detail": "Soal ini bukan bagian dari ujian tersebut."}, status=status.HTTP_400_BAD_REQUEST)

        if Jawaban.objects.filter(ujian=ujian, siswa=siswa, soal=soal).exists():
            return Response(
                {"detail": "Jawaban untuk soal ini sudah dikumpulkan dan tidak dapat diubah."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            with transaction.atomic():
                jawaban = Jawaban.objects.create(
                    ujian=ujian, siswa=siswa, soal=soal, jawaban_teks=data["jawaban_teks"]
                )
        except IntegrityError:
            return Response(
                {"detail": "Jawaban untuk soal ini sudah dikumpulkan dan tidak dapat diubah."},
                status=status.HTTP_409_CONFLICT,
            )

        log_activity(request.user, "kirim_jawaban", "jawaban", str(jawaban.pk), request)
        score_jawaban(jawaban)
        log_activity(request.user, "proses_penilaian", "penilaian", f"jawaban={jawaban.pk}", request)

        jawaban.refresh_from_db()
        return Response(JawabanSerializer(jawaban).data, status=status.HTTP_201_CREATED)


class RiwayatJawabanView(APIView):
    """Bagian 7: siswa melihat riwayat ujian & jawabannya sendiri."""

    permission_classes = [IsSiswa]

    def get(self, request):
        siswa = request.user.siswa_profile
        ujian_id = request.query_params.get("ujian_id")
        qs = Jawaban.objects.filter(siswa=siswa).select_related("soal", "ujian", "penilaian")
        if ujian_id:
            qs = qs.filter(ujian_id=ujian_id)
        return Response(JawabanSerializer(qs.order_by("ujian_id", "soal_id"), many=True).data)
