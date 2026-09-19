from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.exams.views import MasukUjianView, UjianTersediaListView, UjianViewSet

router = DefaultRouter()
router.register("", UjianViewSet, basename="ujian")

urlpatterns = [
    path("tersedia/", UjianTersediaListView.as_view(), name="ujian-tersedia"),
    path("masuk/", MasukUjianView.as_view(), name="ujian-masuk"),
] + router.urls
