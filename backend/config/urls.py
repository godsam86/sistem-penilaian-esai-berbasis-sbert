from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from apps.scoring.views import PublicStatsView
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/master/", include("apps.master_data.urls")),
    path("api/knowledge-base/", include("apps.knowledge_base.urls")),
    path("api/soal/", include("apps.questions.urls")),
    path("api/ujian/", include("apps.exams.urls")),
    path("api/jawaban/", include("apps.answers.urls")),
    path("api/penilaian/", include("apps.scoring.urls")),
    path("api/public/stats/", PublicStatsView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
