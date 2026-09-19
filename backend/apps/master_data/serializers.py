from django.db import transaction
from rest_framework import serializers

from apps.master_data.models import MasterAdmin, MasterGuru, MasterJurusan, MasterKelas, MasterSiswa
from apps.users.models import Role, Status, User


class MasterKelasSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterKelas
        fields = ["id", "nama_kelas", "tingkat", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MasterJurusanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterJurusan
        fields = ["id", "kode_jurusan", "nama_jurusan", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class GuruAccountSerializer(serializers.ModelSerializer):
    """
    Admin membuat/mengubah akun guru: baris `users` (role=guru) +
    `master_guru` sekaligus, dalam satu transaksi (bagian 25).
    """

    id = serializers.IntegerField(source="user.id", read_only=True)
    nama = serializers.CharField(source="user.nama")
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    status = serializers.IntegerField(source="user.status", required=False)

    class Meta:
        model = MasterGuru
        fields = ["id", "nama", "email", "password", "nip", "status", "created_at", "updated_at"]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password", None)
        user = User.objects.create_user(
            email=user_data["email"],
            password=password,
            nama=user_data["nama"],
            role=Role.GURU,
            status=user_data.get("status", Status.AKTIF),
        )
        return MasterGuru.objects.create(user=user, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        password = validated_data.pop("password", None)
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        if password:
            instance.user.set_password(password)
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AdminAccountSerializer(serializers.ModelSerializer):
    """Admin membuat/mengubah akun admin lain: `users` (role=admin) + `master_admin`, satu transaksi."""

    id = serializers.IntegerField(source="user.id", read_only=True)
    nama = serializers.CharField(source="user.nama")
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    status = serializers.IntegerField(source="user.status", required=False)

    class Meta:
        model = MasterAdmin
        fields = ["id", "nama", "email", "password", "jabatan", "status", "created_at", "updated_at"]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = validated_data.pop("password", None)
        user = User.objects.create_user(
            email=user_data["email"],
            password=password,
            nama=user_data["nama"],
            role=Role.ADMIN,
            status=user_data.get("status", Status.AKTIF),
            is_staff=True,
        )
        return MasterAdmin.objects.create(user=user, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        password = validated_data.pop("password", None)
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        if password:
            instance.user.set_password(password)
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SiswaAccountSerializer(serializers.ModelSerializer):
    """Admin membuat/mengubah akun siswa: `users` (role=siswa, tanpa password) + `master_siswa`."""

    id = serializers.IntegerField(source="user.id", read_only=True)
    nama = serializers.CharField(source="user.nama")
    email = serializers.EmailField(source="user.email")
    status = serializers.IntegerField(source="user.status", required=False)

    class Meta:
        model = MasterSiswa
        fields = [
            "id", "nama", "email", "nisn", "kelas", "jurusan", "status",
            "created_at", "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.create_user(
            email=user_data["email"],
            password=None,  # siswa login via NISN, bukan password
            nama=user_data["nama"],
            role=Role.SISWA,
            status=user_data.get("status", Status.AKTIF),
        )
        return MasterSiswa.objects.create(user=user, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
