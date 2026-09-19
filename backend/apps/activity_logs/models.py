from django.conf import settings
from django.db import models


class LogActivity(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs"
    )
    action = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "log_activity"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.created_at}] {self.action} - {self.module}"
