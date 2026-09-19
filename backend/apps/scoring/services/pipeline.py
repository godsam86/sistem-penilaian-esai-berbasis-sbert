"""
Orkestrasi penilaian otomatis (bagian 15, 21). Dipanggil sinkron setiap
jawaban dikirim -- tidak ada Celery/queue (bagian 2/35).
"""
from django.conf import settings
from django.db import transaction

from apps.answers.models import Jawaban
from apps.scoring.models import Penilaian, PenilaianConceptUnit, ProcessingStatus
from apps.scoring.services.concept_scoring import score_concept_units
from apps.scoring.services.feedback import build_feedback
from apps.scoring.services.semantic_scoring import score_semantic
from apps.scoring.services.text_quality import evaluate_text_quality

SCORING_VERSION = "v1"


def score_jawaban(jawaban: Jawaban) -> Penilaian:
    params = settings.SCORING
    penilaian, _ = Penilaian.objects.get_or_create(jawaban=jawaban)

    try:
        teks = (jawaban.jawaban_teks or "").strip()
        jawaban_kosong = len(teks) == 0

        # Bagian 21 poin 1: jawaban kosong -> skor 0 langsung, tanpa panggil model.
        if jawaban_kosong:
            penilaian.semantic_raw = 0.0
            penilaian.semantic_score = 0.0
            penilaian.concept_score = 0.0
            penilaian.final_score = 0.0
            penilaian.relevance_status = "gagal"
            penilaian.text_quality_status = "gagal"
            penilaian.noise_penalty_applied = False
            penilaian.feedback = build_feedback(
                jawaban_kosong=True, relevance_status="gagal", text_quality_status="gagal",
                text_quality_alasan="jawaban kosong", concept_detail=[], concept_units_map={},
            )
            penilaian.model_version = settings.SBERT_MODEL
            penilaian.scoring_version = SCORING_VERSION
            penilaian.processing_status = ProcessingStatus.SUCCESS
            penilaian.processing_error = ""
            penilaian.save()
            return penilaian

        soal = jawaban.soal
        kb_chunks = _chunks_for_soal(soal)
        concept_units = list(soal.concept_units.all())
        concept_units_map = {cu.id: cu.konsep for cu in concept_units}

        semantic_result = score_semantic(teks, kb_chunks, params)
        text_quality = evaluate_text_quality(teks, params)
        concept_result = score_concept_units(teks, concept_units, params["CONCEPT_THRESHOLD"])

        # Bagian 21 poin 2: relevance gate berdasarkan similarity MENTAH, bukan skor terkalibrasi.
        relevance_gagal = semantic_result.semantic_raw < params["SEMANTIC_MIN_THRESHOLD"]
        relevance_status = "gagal" if relevance_gagal else "lolos"
        text_quality_status = "lolos" if text_quality.lolos else "gagal"

        skor_gabungan = (
            params["SEMANTIC_WEIGHT"] * semantic_result.semantic_score
            + params["CONCEPT_WEIGHT"] * concept_result.concept_score
        )

        noise_penalty_applied = False
        if relevance_gagal:
            skor_akhir = 0.0
        elif not text_quality.lolos:
            skor_akhir = skor_gabungan * params["NOISE_PENALTY"]
            noise_penalty_applied = True
        else:
            skor_akhir = skor_gabungan

        skor_akhir = round(max(0.0, min(100.0, skor_akhir)), 2)

        with transaction.atomic():
            penilaian.semantic_raw = semantic_result.semantic_raw
            penilaian.semantic_score = semantic_result.semantic_score
            penilaian.concept_score = concept_result.concept_score
            penilaian.final_score = skor_akhir
            penilaian.relevance_status = relevance_status
            penilaian.text_quality_status = text_quality_status
            penilaian.noise_penalty_applied = noise_penalty_applied
            penilaian.model_version = settings.SBERT_MODEL
            penilaian.scoring_version = SCORING_VERSION
            penilaian.processing_status = ProcessingStatus.SUCCESS
            penilaian.processing_error = ""
            penilaian.feedback = build_feedback(
                jawaban_kosong=False,
                relevance_status=relevance_status,
                text_quality_status=text_quality_status,
                text_quality_alasan=text_quality.alasan,
                concept_detail=concept_result.detail,
                concept_units_map=concept_units_map,
            )
            penilaian.save()

            PenilaianConceptUnit.objects.filter(penilaian=penilaian).delete()
            PenilaianConceptUnit.objects.bulk_create(
                [
                    PenilaianConceptUnit(
                        penilaian=penilaian,
                        concept_unit_id=d["concept_unit_id"],
                        similarity=d["similarity"],
                        detected=d["detected"],
                    )
                    for d in concept_result.detail
                ]
            )

    except Exception as exc:
        # Bagian 21: error pemrosesan JANGAN otomatis jadi skor 0 -- tandai
        # gagal diproses, sediakan mekanisme retry (lihat scoring/views.py).
        penilaian.processing_status = ProcessingStatus.FAILED
        penilaian.processing_error = str(exc)
        penilaian.save()

    return penilaian


def _chunks_for_soal(soal):
    """Bagian 11: HANYA chunk dari KB yang terhubung ke soal ini, bukan seluruh KB sekolah."""
    from apps.knowledge_base.models import KbChunk

    kb_ids = list(soal.knowledge_bases.values_list("id", flat=True))
    return KbChunk.objects.filter(knowledge_base_id__in=kb_ids)
