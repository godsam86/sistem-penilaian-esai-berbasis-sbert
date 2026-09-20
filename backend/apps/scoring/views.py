from django.db import models
from django.db.models import Avg
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.activity_logs.utils import log_activity
from apps.answers.models import Jawaban
from apps.exams.models import Ujian
from apps.scoring.models import Penilaian, ProcessingStatus
from apps.scoring.serializers import HasilGuruSerializer, HasilSiswaSerializer
from apps.scoring.services.pipeline import score_jawaban
from apps.users.permissions import IsAdmin, IsGuru, IsGuruOrAdmin, IsSiswa


def filtered_hasil_queryset(request):
    qs = Penilaian.objects.select_related(
        "jawaban__siswa__user", "jawaban__siswa__kelas", "jawaban__siswa__jurusan",
        "jawaban__ujian", "jawaban__soal",
    ).prefetch_related("detail_cu__concept_unit")

    user = request.user
    if user.role == "guru":
        qs = qs.filter(jawaban__ujian__guru=user.guru_profile)

    params = request.query_params
    if params.get("kelas_id"):
        qs = qs.filter(jawaban__siswa__kelas_id=params["kelas_id"])
    if params.get("jurusan_id"):
        qs = qs.filter(jawaban__siswa__jurusan_id=params["jurusan_id"])
    if params.get("ujian_id"):
        qs = qs.filter(jawaban__ujian_id=params["ujian_id"])
    search = params.get("search")
    if search:
        qs = qs.filter(
            models.Q(jawaban__siswa__user__nama__icontains=search)
            | models.Q(jawaban__siswa__nisn__icontains=search)
        )
    return qs.order_by("-created_at")


class HasilGuruViewSet(ReadOnlyModelViewSet):
    """
    Bagian 24: guru hanya melihat hasil ujian miliknya; admin melihat semua
    (bagian 25). Filter kelas/jurusan/ujian + pencarian nama/NISN + pagination.
    """

    serializer_class = HasilGuruSerializer
    permission_classes = [IsGuruOrAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["jawaban__siswa__user__nama", "jawaban__siswa__nisn"]

    def get_queryset(self):
        return filtered_hasil_queryset(self.request)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """Bagian 21: retry manual untuk penilaian yang gagal diproses."""
        penilaian = self.get_object()
        if penilaian.processing_status != ProcessingStatus.FAILED:
            return Response({"detail": "Penilaian ini tidak dalam status gagal."}, status=status.HTTP_400_BAD_REQUEST)
        score_jawaban(penilaian.jawaban)
        log_activity(request.user, "retry_penilaian", "penilaian", str(penilaian.pk), request)
        penilaian.refresh_from_db()
        return Response(HasilGuruSerializer(penilaian, context=self.get_serializer_context()).data)


class NilaiUjianSiswaView(APIView):
    """Bagian 7 & 23: nilai akhir ujian = rata-rata skor seluruh soal; soal tak dijawab = 0."""

    permission_classes = [IsSiswa]

    def get(self, request, ujian_id):
        siswa = request.user.siswa_profile
        ujian = Ujian.objects.filter(pk=ujian_id, kelas=siswa.kelas, jurusan=siswa.jurusan).first()
        if ujian is None:
            return Response({"detail": "Ujian tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)
        if not ujian.hasil_published:
            return Response({"detail": "Hasil belum dipublikasikan oleh guru."}, status=status.HTTP_403_FORBIDDEN)

        total_soal = ujian.soal_list.count()
        jawaban_qs = Jawaban.objects.filter(ujian=ujian, siswa=siswa).select_related("penilaian", "soal")
        jumlah_dijawab = jawaban_qs.count()

        skor_list = [j.penilaian.final_score or 0.0 for j in jawaban_qs if hasattr(j, "penilaian")]
        skor_list += [0.0] * (total_soal - jumlah_dijawab)  # soal tak dijawab = 0
        nilai_akhir = round(sum(skor_list) / total_soal, 2) if total_soal else 0.0

        detail = HasilSiswaSerializer(
            [j.penilaian for j in jawaban_qs if hasattr(j, "penilaian")], many=True
        ).data
        return Response({"nilai_akhir": nilai_akhir, "detail_per_soal": detail})


class ExportPermission(IsGuruOrAdmin):
    pass


class ExportXlsxView(APIView):
    permission_classes = [IsGuruOrAdmin]

    def get(self, request):
        from apps.scoring.export import export_xlsx
        return export_xlsx(filtered_hasil_queryset(request), request)


class ExportPdfView(APIView):
    permission_classes = [IsGuruOrAdmin]

    def get(self, request):
        from apps.scoring.export import export_pdf
        return export_pdf(filtered_hasil_queryset(request), request)
