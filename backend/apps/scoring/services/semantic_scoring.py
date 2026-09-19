"""Bagian 19: semantic scoring -- bandingkan jawaban HANYA dengan chunk KB yang terhubung ke soal."""
from dataclasses import dataclass

import numpy as np

from apps.knowledge_base.services import embedding
from apps.scoring.services.calibration import calibrate_semantic_score


@dataclass
class SemanticResult:
    semantic_raw: float          # rata-rata cosine similarity top-K (0..1)
    semantic_score: float        # hasil kalibrasi (0..100)
    top_k_chunks: list           # [{chunk_id, similarity}, ...] untuk audit (bagian 24)


def _cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def score_semantic(jawaban_teks: str, kb_chunks, params: dict) -> SemanticResult:
    """
    kb_chunks: queryset/list KbChunk milik KB yang terhubung ke soal ini SAJA
    (bagian 11) -- jangan pernah membandingkan ke seluruh KB sekolah.
    """
    chunk_list = list(kb_chunks)
    if not chunk_list:
        return SemanticResult(semantic_raw=0.0, semantic_score=0.0, top_k_chunks=[])

    jawaban_vec = np.array(embedding.embed_text(jawaban_teks))
    similarities = []
    for chunk in chunk_list:
        sim = _cosine_sim(jawaban_vec, np.array(chunk.embedding))
        similarities.append((chunk.id, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    k = min(params["TOP_K"], len(similarities))
    top_k = similarities[:k]

    s = sum(sim for _, sim in top_k) / k if k else 0.0

    semantic_score = calibrate_semantic_score(
        s=s,
        t=params["SEMANTIC_MIN_THRESHOLD"],
        b=params["SEMANTIC_BASELINE"],
        m=params["SEMANTIC_BELOW_BASELINE_MAX"],
    )

    return SemanticResult(
        semantic_raw=round(s, 6),
        semantic_score=round(semantic_score, 4),
        top_k_chunks=[{"chunk_id": cid, "similarity": round(sim, 6)} for cid, sim in top_k],
    )
