"""
Pemecahan teks menjadi chunk sesuai batas token model SBERT (bagian 9, 17).
Model paraphrase-multilingual-MiniLM-L12-v2 punya batas ~128 token subword.
Kita gunakan pendekatan berbasis kata (aproksimasi token) dengan overlap kecil
agar konteks di batas chunk tidak hilang.

Panjang chunk & overlap diatur lewat KB_CHUNK_MAX_WORDS / KB_CHUNK_OVERLAP_WORDS
di .env (default 150 kata & overlap 30 kata) -- bukan hardcode di kode ini.
"""
import re

from django.conf import settings


def split_into_chunks(text: str, max_words: int | None = None, overlap: int | None = None):
    if max_words is None:
        max_words = settings.KB_CHUNK_MAX_WORDS
    if overlap is None:
        overlap = settings.KB_CHUNK_OVERLAP_WORDS

    text = text.strip()
    if not text:
        return []

    # Pecah per paragraf dulu supaya tidak memotong konteks secara acak,
    # baru gabungkan/pecah lagi sampai memenuhi batas kata per chunk.
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    words_stream = []
    for p in paragraphs:
        words_stream.extend(p.split())
        words_stream.append("\n")  # marker batas paragraf (tidak dihitung sebagai kata nyata)

    words = [w for w in words_stream if w != "\n"]

    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == len(words):
            break
        start = end - overlap  # overlap supaya kalimat di batas chunk tidak putus konteks

    return chunks
