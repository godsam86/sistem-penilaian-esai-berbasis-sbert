"""
Bagian 17 & 18: validasi kualitas teks. Heuristik ini BUKAN bukti bahwa
jawaban salah -- hanya menandai kualitas teks (noise, capslock, dsb).
"""
import re
from dataclasses import dataclass

VOKAL = set("aiueoAIUEO")


@dataclass
class TextQualityResult:
    jumlah_kata: int
    rasio_alfabet: float
    rasio_vokal: float
    rasio_kapital: float
    lolos: bool
    alasan: str = ""


def _rasio_kapital_mencurigakan(text: str) -> float:
    """
    Rasio huruf kapital di ANTARA karakter alfabet saja (bukan seluruh
    string), supaya singkatan wajar seperti CPU/RAM/SQL di tengah kalimat
    tidak otomatis dianggap noise (bagian 18) -- itu dinilai lewat rasio
    alfabet & vokal, bukan lewat kapital semata.
    """
    huruf = [c for c in text if c.isalpha()]
    if not huruf:
        return 0.0
    kapital = sum(1 for c in huruf if c.isupper())
    return kapital / len(huruf)


def evaluate_text_quality(text: str, params: dict) -> TextQualityResult:
    text = text.strip()
    kata_list = text.split()
    jumlah_kata = len(kata_list)

    total_char = len(text.replace(" ", ""))
    huruf_char = sum(1 for c in text if c.isalpha())
    rasio_alfabet = (huruf_char / total_char) if total_char else 0.0

    kata_dengan_vokal = sum(1 for k in kata_list if any(c in VOKAL for c in k))
    rasio_vokal = (kata_dengan_vokal / jumlah_kata) if jumlah_kata else 0.0

    rasio_kapital = _rasio_kapital_mencurigakan(text)

    alasan = []
    if jumlah_kata < params["TEXT_MIN_WORDS"]:
        alasan.append(f"jumlah kata ({jumlah_kata}) di bawah minimum ({params['TEXT_MIN_WORDS']})")
    if rasio_alfabet < params["TEXT_MIN_ALPHA_RATIO"]:
        alasan.append(f"rasio karakter alfabet ({rasio_alfabet:.2f}) terlalu rendah")
    if rasio_vokal < params["TEXT_MIN_VOWEL_RATIO"]:
        alasan.append(f"rasio kata berpola vokal ({rasio_vokal:.2f}) terlalu rendah")
    if rasio_kapital > params["TEXT_MAX_UPPER_RATIO"]:
        alasan.append(f"rasio kapital ({rasio_kapital:.2f}) mencurigakan")

    return TextQualityResult(
        jumlah_kata=jumlah_kata,
        rasio_alfabet=round(rasio_alfabet, 4),
        rasio_vokal=round(rasio_vokal, 4),
        rasio_kapital=round(rasio_kapital, 4),
        lolos=(len(alasan) == 0),
        alasan="; ".join(alasan),
    )
