from django.contrib.auth.backends import BaseBackend

from apps.users.models import Role, User


class EmailCredentialBackend(BaseBackend):
    """
    Backend untuk SATU form login (bagian 4 spesifikasi):
      - admin/guru : email + password (hash, django check_password)
      - siswa      : email + NISN (dicocokkan ke master_siswa.nisn)

    Role TIDAK PERNAH dipercaya dari input frontend -- selalu dibaca dari
    baris `users` yang ditemukan lewat email. Akun status=0 selalu ditolak.
    Pesan error di view HARUS generik agar tidak membocorkan apakah email
    terdaftar atau tidak.
    """

    def authenticate(self, request, email=None, credential=None, **kwargs):
        if not email or not credential:
            return None

        user = User.objects.filter(email__iexact=email).select_related(
            "siswa_profile"
        ).first()
        if user is None or not user.is_active:
            return None

        if user.role == Role.SISWA:
            siswa = getattr(user, "siswa_profile", None)
            if siswa is None or siswa.status != 1:
                return None
            if siswa.nisn != credential:
                return None
            return user

        # admin & guru -> password hash biasa
        if user.check_password(credential):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
