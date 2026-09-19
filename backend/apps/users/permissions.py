from rest_framework.permissions import BasePermission

from apps.users.models import Role


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.ADMIN)


class IsGuru(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.GURU)


class IsSiswa(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.SISWA)


class IsGuruOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.GURU, Role.ADMIN)
        )


class IsOwnerGuru(BasePermission):
    """
    Object-level: guru hanya boleh mengakses object miliknya sendiri
    (bagian 8 & 31). Object harus punya atribut `guru` (FK ke MasterGuru)
    atau `guru_id`.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role != Role.GURU:
            return False
        guru_profile = getattr(request.user, "guru_profile", None)
        if guru_profile is None:
            return False
        owner_id = getattr(obj, "guru_id", None)
        return owner_id == guru_profile.id


class IsOwnerSiswa(BasePermission):
    """Siswa hanya boleh mengakses data miliknya sendiri (bagian 7 & 31)."""

    def has_object_permission(self, request, view, obj):
        if request.user.role != Role.SISWA:
            return False
        siswa_profile = getattr(request.user, "siswa_profile", None)
        if siswa_profile is None:
            return False
        owner_id = getattr(obj, "siswa_id", None)
        return owner_id == siswa_profile.id
