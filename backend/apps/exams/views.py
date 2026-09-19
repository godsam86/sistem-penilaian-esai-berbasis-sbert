from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.activity_logs.utils import log_activity
from apps.exams.models import Ujian, UjianStatus
from apps.exams.serializers import (
    SoalUntukSiswaSerializer,
    TokenMasukSerializer,
    UjianSerializer,
    UjianTersediaSerializer,
)
from apps.users.permissions import IsGuru, IsSiswa


class UjianViewSet(viewsets.ModelViewSet):
    """Guru hanya mengelola ujian miliknya sendiri (bagian 8, 31)."""

    serializer_class = UjianSerializer
    permission_classes = [IsGuru]

    def get_queryset(self):
        return Ujian.objects.filter(guru=self.request.user.guru_profile).order_by("-created_at")

    def perform_create(self, serializer):
        ujian = serializer.save(guru=self.request.user.guru_profile, created_by=self.request.user.id)
        log_activity(self.request.user, "buat_ujian", "ujian", str(ujian.pk), self.request)

    def perform_update(self, serializer):
        ujian = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_ujian", "ujian", str(ujian.pk), self.request)

    @action(detail=True, methods=["post"])
    def publikasikan(self, request, pk=None):
        """Bagian 23: guru mengatur hasil sudah/belum dipublikasikan."""
        ujian = self.get_object()
        ujian.hasil_published = bool(request.data.get("hasil_published", True))
        ujian.save(update_fields=["hasil_published"])
        log_activity(request.user, "publikasi_hasil", "ujian", str(ujian.pk), request)
        return Response(UjianSerializer(ujian, context=self.get_serializer_context()).data)


class UjianTersediaListView(APIView):
    """Bagian 7: siswa hanya melihat ujian untuk kelas & jurusannya."""

    permission_classes = [IsSiswa]

    def get(self, request):
        siswa = request.user.siswa_profile
        qs = Ujian.objects.filter(
            kelas=siswa.kelas, jurusan=siswa.jurusan, status=UjianStatus.AKTIF
        ).order_by("-created_at")
        data = UjianTersediaSerializer(qs, many=True, context={"request": request}).data
        return Response(data)


class MasukUjianView(APIView):
    """
    Bagian 7 & 12: siswa memasukkan token. Backend WAJIB memverifikasi
    user login, status akun, kelas, jurusan, token, dan status ujian --
    token bukan pengganti autentikasi.
    """

    permission_classes = [IsSiswa]

    def post(self, request):
        serializer = TokenMasukSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"].upper()

        siswa = request.user.siswa_profile
        ujian = Ujian.objects.filter(token=token, status=UjianStatus.AKTIF).first()

        if ujian is None:
            return Response({"detail": "Token tidak valid atau ujian tidak aktif."}, status=status.HTTP_404_NOT_FOUND)
        if ujian.kelas_id != siswa.kelas_id or ujian.jurusan_id != siswa.jurusan_id:
            return Response(
                {"detail": "Ujian ini bukan untuk kelas/jurusan Anda."}, status=status.HTTP_403_FORBIDDEN
            )

        soal_qs = ujian.soal_list.all().order_by("ujiansoal__urutan")
        soal_data = SoalUntukSiswaSerializer(
            soal_qs, many=True, context={"request": request, "ujian": ujian}
        ).data
        return Response(
            {
                "ujian": {
                    "id": ujian.id,
                    "nama_ujian": ujian.nama_ujian,
                    "jenis_ujian": ujian.jenis_ujian,
                },
                "soal": soal_data,
            }
        )
