from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ("email", "nama", "role", "status", "is_staff")
    list_filter = ("role", "status")
    search_fields = ("email", "nama")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Info", {"fields": ("nama", "role", "status")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "nama", "role", "status", "password1", "password2")}),
    )
    filter_horizontal = ()
    list_filter = ("role", "status", "is_staff")
