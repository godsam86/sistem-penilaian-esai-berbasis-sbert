from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.scoring.views import (
    ExportPdfView,
    ExportXlsxView,
    HasilGuruViewSet,
    NilaiUjianSiswaView,
    PublicStatsView,
)

router = DefaultRouter()
router.register("hasil", HasilGuruViewSet, basename="hasil-guru")

urlpatterns = [
    path("public/stats/", PublicStatsView.as_view(), name="public-stats"),
    path("nilai-ujian/<int:ujian_id>/", NilaiUjianSiswaView.as_view(), name="nilai-ujian-siswa"),
    path("export/xlsx/", ExportXlsxView.as_view(), name="export-xlsx"),
    path("export/pdf/", ExportPdfView.as_view(), name="export-pdf"),
] + router.urls
