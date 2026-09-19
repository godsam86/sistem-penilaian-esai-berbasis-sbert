from django.contrib import admin

from apps.scoring.models import Penilaian, PenilaianConceptUnit


class PenilaianConceptUnitInline(admin.TabularInline):
    model = PenilaianConceptUnit
    extra = 0


@admin.register(Penilaian)
class PenilaianAdmin(admin.ModelAdmin):
    list_display = ("id", "jawaban", "final_score", "processing_status")
    list_filter = ("processing_status", "relevance_status", "text_quality_status")
    inlines = [PenilaianConceptUnitInline]
