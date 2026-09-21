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
    """
    Kandidat pembanding untuk tiap Concept Unit: kalimat penuh (dipisah
    tanda baca akhir) DITAMBAH klausa yang dipisah koma di dalamnya.

    Ditambahkan karena jawaban esai sering menggabungkan beberapa definisi
    konsep dalam satu kalimat majemuk, contoh pola nyata:
    "Tesis berisi ..., argumentasi berisi ..., sedangkan penegasan ulang
    berisi ...". Kalau hanya dipisah per kalimat, gabungan itu jadi SATU
    vektor "encer" berisi campuran 3 konsep -- similarity-nya ke SETIAP
    Concept Unit di dalamnya jadi turun, walau isinya sudah benar.

    Menambah klausa per-koma sebagai kandidat TAMBAHAN (bukan pengganti)
    hanya bisa menaikkan atau menyamakan similarity maksimum tiap CU --
    tidak pernah menurunkannya, karena kalimat penuh tetap ikut dibandingkan.
    """
    kalimat_penuh = [k.strip() for k in re.split(r"(?<=[.!?])\s+|\n+", text) if k.strip()]

    klausa = []
    for k in kalimat_penuh:
        for bagian in k.split(","):
            bagian = bagian.strip().rstrip(".!?")
            if len(bagian.split()) >= 3:  # lewati pecahan terlalu pendek untuk jadi bermakna
                klausa.append(bagian)

    kandidat = kalimat_penuh + klausa
    dilihat = set()
    unik = []
    for k in kandidat:
        if k not in dilihat:
            dilihat.add(k)
            unik.append(k)

    return unik or ([text.strip()] if text.strip() else [])


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