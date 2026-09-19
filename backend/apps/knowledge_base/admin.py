from django.contrib import admin

from apps.knowledge_base.models import KbChunk, KnowledgeBase


@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ("judul", "guru", "sumber", "processing_status", "status")
    list_filter = ("processing_status", "sumber", "status")
    search_fields = ("judul",)


admin.site.register(KbChunk)
