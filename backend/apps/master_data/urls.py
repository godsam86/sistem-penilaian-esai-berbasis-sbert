from rest_framework.routers import DefaultRouter

from apps.master_data.views import (
    AdminAccountViewSet,
    GuruAccountViewSet,
    MasterJurusanViewSet,
    MasterKelasViewSet,
    SiswaAccountViewSet,
)

router = DefaultRouter()
router.register("kelas", MasterKelasViewSet, basename="master-kelas")
router.register("jurusan", MasterJurusanViewSet, basename="master-jurusan")
router.register("admin", AdminAccountViewSet, basename="master-admin")
router.register("guru", GuruAccountViewSet, basename="master-guru")
router.register("siswa", SiswaAccountViewSet, basename="master-siswa")

urlpatterns = router.urls
