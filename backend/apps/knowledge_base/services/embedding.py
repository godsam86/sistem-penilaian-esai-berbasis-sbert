"""
Wrapper SBERT (bagian 33): model dimuat SEKALI per process dan dipakai
ulang -- jangan memuat model baru setiap request.
"""
import threading

from django.conf import settings

_model = None
_lock = threading.Lock()


def get_embedder():
    """
    Lazy singleton. Memuat SentenceTransformer sekali per proses Gunicorn
    worker. Membutuhkan koneksi internet saat pertama kali (download bobot
    model dari HuggingFace) -- di production, cache model di volume Docker
    (bagian 30) supaya tidak download ulang setiap restart container.
    """
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                from sentence_transformers import SentenceTransformer

                _model = SentenceTransformer(settings.SBERT_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_embedder()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
