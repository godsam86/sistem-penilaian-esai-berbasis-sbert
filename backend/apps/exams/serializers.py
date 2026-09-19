from django.db import transaction
from rest_framework import serializers

from apps.exams.models import Ujian, UjianSoal
from apps.exams.token_generator import generate_unique_token
from apps.master_data.models import MasterJurusan, MasterKelas
from apps.questions.models import Soal


class UjianSoalItemSerializer(serializers.Serializer):
    soal_id = serializers.PrimaryKeyRelatedField(source="soal", queryset=Soal.objects.all())
    urutan = serializers.IntegerField()


class UjianSerializer(serializers.ModelSerializer):
    soal_items = UjianSoalItemSerializer(many=True, write_only=True, required=False)
    kelas_id = serializers.PrimaryKeyRelatedField(source="kelas", queryset=MasterKelas.objects.all())
    jurusan_id = serializers.PrimaryKeyRelatedField(source="jurusan", queryset=MasterJurusan.objects.all())
    jumlah_soal = serializers.IntegerField(source="soal_list.count", read_only=True)

    class Meta:
        model = Ujian
        fields = [
            "id", "nama_ujian", "jenis_ujian", "kelas_id", "jurusan_id",
            "token", "status", "hasil_published", "jumlah_soal", "soal_items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["token", "created_at", "updated_at"]

    def validate_soal_items(self, items):
        request = self.context["request"]
        guru_profile = request.user.guru_profile
        for item in items:
            soal = item["soal"]
            if soal.guru_id != guru_profile.id:
                raise serializers.ValidationError("Soal harus milik Anda sendiri (bagian 31).")
            if not soal.siap_dipakai:
                raise serializers.ValidationError(
                    f"Soal id={soal.id} belum siap dipakai: butuh minimal 1 Concept Unit "
                    "dan minimal 1 Knowledge Base yang sudah selesai diproses (bagian 10)."
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        soal_items = validated_data.pop("soal_items", [])
        ujian = Ujian.objects.create(token=generate_unique_token(), **validated_data)
        UjianSoal.objects.bulk_create(
            [UjianSoal(ujian=ujian, soal=item["soal"], urutan=item["urutan"]) for item in soal_items]
        )
        return ujian

    @transaction.atomic
    def update(self, instance, validated_data):
        soal_items = validated_data.pop("soal_items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if soal_items is not None:
            UjianSoal.objects.filter(ujian=instance).delete()
            UjianSoal.objects.bulk_create(
                [UjianSoal(ujian=instance, soal=item["soal"], urutan=item["urutan"]) for item in soal_items]
            )
        return instance


class UjianTersediaSerializer(serializers.ModelSerializer):
    """Bagian 7: siswa melihat nama, jenis, guru pembuat, jumlah soal, status -- tanpa token/jawaban_acuan."""

    guru_pembuat = serializers.CharField(source="guru.user.nama", read_only=True)
    jumlah_soal = serializers.IntegerField(source="soal_list.count", read_only=True)
    sudah_dikerjakan = serializers.SerializerMethodField()

    class Meta:
        model = Ujian
        fields = ["id", "nama_ujian", "jenis_ujian", "guru_pembuat", "jumlah_soal", "status", "sudah_dikerjakan"]

    def get_sudah_dikerjakan(self, obj):
        siswa_profile = self.context["request"].user.siswa_profile
        total_soal = obj.soal_list.count()
        total_jawaban = obj.jawaban_set.filter(siswa=siswa_profile).count() if hasattr(obj, "jawaban_set") else 0
        return total_soal > 0 and total_jawaban >= total_soal


class SoalUntukSiswaSerializer(serializers.ModelSerializer):
    """Soal yang dilihat siswa saat mengerjakan -- TANPA jawaban_acuan."""

    sudah_dijawab = serializers.SerializerMethodField()

    class Meta:
        model = Soal
        fields = ["id", "pertanyaan", "sudah_dijawab"]

    def get_sudah_dijawab(self, obj):
        siswa_profile = self.context["request"].user.siswa_profile
        ujian = self.context["ujian"]
        return obj.jawaban_set.filter(siswa=siswa_profile, ujian=ujian).exists() if hasattr(obj, "jawaban_set") else False


class TokenMasukSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=5)
