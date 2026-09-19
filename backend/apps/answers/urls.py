from django.urls import path

from apps.answers.views import RiwayatJawabanView, SubmitJawabanView

urlpatterns = [
    path("submit/", SubmitJawabanView.as_view(), name="jawaban-submit"),
    path("riwayat/", RiwayatJawabanView.as_view(), name="jawaban-riwayat"),
]
