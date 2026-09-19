from rest_framework.routers import DefaultRouter

from apps.knowledge_base.views import KnowledgeBaseViewSet

router = DefaultRouter()
router.register("", KnowledgeBaseViewSet, basename="knowledge-base")

urlpatterns = router.urls
