from django.contrib import admin

from apps.questions.models import ConceptUnit, Soal, SoalKnowledgeBase


class ConceptUnitInline(admin.TabularInline):
    model = ConceptUnit
    extra = 0


@admin.register(Soal)
class SoalAdmin(admin.ModelAdmin):
    list_display = ("id", "guru", "status")
    inlines = [ConceptUnitInline]


admin.site.register(SoalKnowledgeBase)
