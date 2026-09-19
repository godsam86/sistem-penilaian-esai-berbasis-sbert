"""
Bagian 20: Concept Unit scoring. Similarity CU = similarity TERTINGGI
terhadap bagian jawaban yang relevan. Untuk kesederhanaan (bagian 2: tidak
menambah kompleksitas tanpa perlu) dan karena jawaban esai umumnya singkat,
"bagian jawaban" didekati dengan memecah jawaban jadi kalimat -- CU
dibandingkan dengan setiap kalimat, similarity tertinggi yang dipakai.
"""
import re
from dataclasses import dataclass

import numpy as np

from apps.knowledge_base.services import embedding


@dataclass
class ConceptUnitResult:
    concept_score: float  # 0..100
    detail: list          # [{concept_unit_id, similarity, detected}, ...]


def _split_kalimat(text: str) -> list[str]:
    kalimat = [k.strip() for k in re.split(r"(?<=[.!?])\s+|\n+", text) if k.strip()]
    return kalimat or ([text.strip()] if text.strip() else [])


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0


def score_concept_units(jawaban_teks: str, concept_units, threshold: float) -> ConceptUnitResult:
    concept_units = list(concept_units)
    if not concept_units:
        return ConceptUnitResult(concept_score=0.0, detail=[])

    kalimat_list = _split_kalimat(jawaban_teks)
    if not kalimat_list:
        detail = [{"concept_unit_id": cu.id, "similarity": 0.0, "detected": False} for cu in concept_units]
        return ConceptUnitResult(concept_score=0.0, detail=detail)

    kalimat_vecs = np.array(embedding.embed_texts(kalimat_list))
    cu_vecs = np.array(embedding.embed_texts([cu.konsep for cu in concept_units]))

    detail = []
    terdeteksi = 0
    for cu, cu_vec in zip(concept_units, cu_vecs):
        best_sim = max(_cosine_sim(cu_vec, kal_vec) for kal_vec in kalimat_vecs)
        is_detected = best_sim >= threshold
        if is_detected:
            terdeteksi += 1
        detail.append(
            {"concept_unit_id": cu.id, "similarity": round(best_sim, 6), "detected": is_detected}
        )

    concept_score = (terdeteksi / len(concept_units)) * 100
    return ConceptUnitResult(concept_score=round(concept_score, 4), detail=detail)
