from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.users.models import User


class LoginSerializer(serializers.Serializer):
    """
    Satu form untuk ketiga role (bagian 4). `credential` = password
    (admin/guru) ATAU NISN (siswa) -- backend yang menentukan artinya
    berdasarkan role akun yang ditemukan lewat email, bukan frontend.
    """

    email = serializers.EmailField()
    credential = serializers.CharField(write_only=True, trim_whitespace=False)


class ProfileSiswaSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    kelas = serializers.CharField(source="kelas.nama_kelas")
    jurusan = serializers.CharField(source="jurusan.nama_jurusan")


class ProfileGuruSerializer(serializers.Serializer):
    nip = serializers.CharField(allow_null=True)


class ProfileAdminSerializer(serializers.Serializer):
    jabatan = serializers.CharField(allow_null=True)


class UserProfileSerializer(serializers.ModelSerializer):
    siswa = serializers.SerializerMethodField()
    guru = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "nama", "email", "role", "status", "siswa", "guru", "admin"]

    def get_siswa(self, obj):
        profile = getattr(obj, "siswa_profile", None)
        return ProfileSiswaSerializer(profile).data if profile else None

    def get_guru(self, obj):
        profile = getattr(obj, "guru_profile", None)
        return ProfileGuruSerializer(profile).data if profile else None

    def get_admin(self, obj):
        profile = getattr(obj, "admin_profile", None)
        return ProfileAdminSerializer(profile).data if profile else None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Ubah password untuk SEMUA role (admin/guru/siswa) -- atas permintaan
    eksplisit pengguna. Verifikasi cukup dengan mencocokkan email akun yang
    sedang login (bukan password lama) -- kalau email cocok, password baru
    langsung berlaku. Untuk siswa, field password ini tidak dipakai saat
    login (siswa tetap login pakai NISN, lihat auth_backends.py), tapi
    tetap disediakan sesuai permintaan.
    """

    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
