from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from apps.activity_logs.utils import log_activity
from apps.master_data.models import MasterAdmin, MasterGuru, MasterJurusan, MasterKelas, MasterSiswa
from apps.master_data.serializers import (
    AdminAccountSerializer,
    GuruAccountSerializer,
    MasterJurusanSerializer,
    MasterKelasSerializer,
    SiswaAccountSerializer,
)
from apps.users.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated


class ReadableByAnyAuthenticatedMixin:
    """
    Guru butuh baca daftar kelas/jurusan untuk membuat ujian (bagian 8), tapi
    tidak boleh mengubahnya -- itu tetap wewenang admin (bagian 25).
    """

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsAdmin()]



class SoftDeactivateMixin:
    """
    Bagian 25: admin tidak menghapus, hanya menonaktifkan (status=0).
    Riwayat transaksi terkait tetap aman (bagian 28). Bisa diaktifkan
    kembali lewat action `aktifkan` (atas permintaan Anda).
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        target = getattr(instance, "user", instance)  # akun -> nonaktifkan users.status
        target.status = 0
        target.save(update_fields=["status"])
        log_activity(
            request.user,
            action="nonaktifkan",
            module=self.activity_module,
            description=f"id={instance.pk}",
            request=request,
        )
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def aktifkan(self, request, pk=None):
        instance = self.get_object()
        target = getattr(instance, "user", instance)
        target.status = 1
        target.save(update_fields=["status"])
        log_activity(
            request.user,
            action="aktifkan",
            module=self.activity_module,
            description=f"id={instance.pk}",
            request=request,
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MasterKelasViewSet(ReadableByAnyAuthenticatedMixin, viewsets.ModelViewSet):
    queryset = MasterKelas.objects.all().order_by("nama_kelas")
    serializer_class = MasterKelasSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["nama_kelas", "tingkat"]
    activity_module = "master_kelas"

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user.id)
        log_activity(self.request.user, "buat", self.activity_module, str(instance.pk), self.request)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah", self.activity_module, str(instance.pk), self.request)


class MasterJurusanViewSet(ReadableByAnyAuthenticatedMixin, viewsets.ModelViewSet):
    queryset = MasterJurusan.objects.all().order_by("nama_jurusan")
    serializer_class = MasterJurusanSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["nama_jurusan", "kode_jurusan"]
    activity_module = "master_jurusan"

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user.id)
        log_activity(self.request.user, "buat", self.activity_module, str(instance.pk), self.request)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah", self.activity_module, str(instance.pk), self.request)


class GuruAccountViewSet(SoftDeactivateMixin, viewsets.ModelViewSet):
    queryset = MasterGuru.objects.select_related("user").order_by("user__nama")
    serializer_class = GuruAccountSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["user__nama", "user__email", "nip"]
    activity_module = "master_guru"

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user.id)
        log_activity(self.request.user, "buat_akun_guru", self.activity_module, str(instance.pk), self.request)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_akun_guru", self.activity_module, str(instance.pk), self.request)


class AdminAccountViewSet(SoftDeactivateMixin, viewsets.ModelViewSet):
    """
    Bagian 25 (perluasan atas permintaan Anda): admin mengelola akun admin
    lain lewat master_admin, pola sama seperti master_guru/master_siswa.
    """

    queryset = MasterAdmin.objects.select_related("user").order_by("user__nama")
    serializer_class = AdminAccountSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["user__nama", "user__email", "jabatan"]
    activity_module = "master_admin"

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user.id)
        log_activity(self.request.user, "buat_akun_admin", self.activity_module, str(instance.pk), self.request)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_akun_admin", self.activity_module, str(instance.pk), self.request)

    def destroy(self, request, *args, **kwargs):
        # Cegah admin menonaktifkan akunnya sendiri -- supaya tidak ada yang
        # tidak sengaja mengunci diri sendiri keluar dari sistem.
        instance = self.get_object()
        if instance.user_id == request.user.id:
            return Response(
                {"detail": "Anda tidak dapat menonaktifkan akun Anda sendiri."}, status=400
            )
        return super().destroy(request, *args, **kwargs)


class SiswaAccountViewSet(SoftDeactivateMixin, viewsets.ModelViewSet):
    queryset = MasterSiswa.objects.select_related("user", "kelas", "jurusan").order_by("user__nama")
    serializer_class = SiswaAccountSerializer
    permission_classes = [IsAdmin]
    filter_backends = [SearchFilter]
    search_fields = ["user__nama", "nisn"]
    activity_module = "master_siswa"

    def get_queryset(self):
        qs = super().get_queryset()
        kelas_id = self.request.query_params.get("kelas_id")
        jurusan_id = self.request.query_params.get("jurusan_id")
        if kelas_id:
            qs = qs.filter(kelas_id=kelas_id)
        if jurusan_id:
            qs = qs.filter(jurusan_id=jurusan_id)
        return qs

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user.id)
        log_activity(self.request.user, "buat_akun_siswa", self.activity_module, str(instance.pk), self.request)

    def perform_update(self, serializer):
        instance = serializer.save(updated_by=self.request.user.id)
        log_activity(self.request.user, "ubah_akun_siswa", self.activity_module, str(instance.pk), self.request)