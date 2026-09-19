from django.contrib import admin

from apps.activity_logs.models import LogActivity


@admin.register(LogActivity)
class LogActivityAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "module")
    list_filter = ("module", "action")
    search_fields = ("description", "user__nama", "user__email")
    readonly_fields = [f.name for f in LogActivity._meta.fields]
    ordering = ("-created_at",)
