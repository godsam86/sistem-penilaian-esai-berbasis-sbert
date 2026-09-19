from django.db import transaction
from rest_framework import serializers

from apps.knowledge_base.models import KnowledgeBase
from apps.questions.models import ConceptUnit, Soal


class ConceptUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptUnit
        fields = ["id", "konsep", "urutan", "bobot"]


class SoalSerializer(serializers.ModelSerializer):
    concept_units = ConceptUnitSerializer(many=True, required=False)
    knowledge_base_ids = serializers.PrimaryKeyRelatedField(
        source="knowledge_bases", many=True, queryset=KnowledgeBase.objects.all(), required=False
    )
    siap_dipakai = serializers.BooleanField(read_only=True)

    class Meta:
        model = Soal
        fields = [
            "id", "pertanyaan", "jawaban_acuan", "status",
            "knowledge_base_ids", "concept_units", "siap_dipakai",
            "created_at", "updated_at",
        ]

    def validate_knowledge_base_ids(self, kbs):
        request = self.context["request"]
        guru_profile = request.user.guru_profile
        for kb in kbs:
            if kb.guru_id != guru_profile.id:
                raise serializers.ValidationError(
                    "Knowledge Base harus milik Anda sendiri (bagian 31)."
                )
        return kbs

    @transaction.atomic
    def create(self, validated_data):
        cu_data = validated_data.pop("concept_units", [])
        kbs = validated_data.pop("knowledge_bases", [])
        soal = Soal.objects.create(**validated_data)
        soal.knowledge_bases.set(kbs)
        ConceptUnit.objects.bulk_create(
            [ConceptUnit(soal=soal, **cu) for cu in cu_data]
        )
        return soal

    @transaction.atomic
    def update(self, instance, validated_data):
        cu_data = validated_data.pop("concept_units", None)
        kbs = validated_data.pop("knowledge_bases", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if kbs is not None:
            instance.knowledge_bases.set(kbs)
        if cu_data is not None:
            # Replace penuh -- guru membuat CU secara dinamis, jumlah tidak dibatasi (bagian 10).
            instance.concept_units.all().delete()
            ConceptUnit.objects.bulk_create(
                [ConceptUnit(soal=instance, **cu) for cu in cu_data]
            )
        return instance
