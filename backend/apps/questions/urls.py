from rest_framework.routers import DefaultRouter

from apps.questions.views import SoalViewSet

router = DefaultRouter()
router.register("", SoalViewSet, basename="soal")

urlpatterns = router.urls
