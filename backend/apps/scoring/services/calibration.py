"""
Bagian 19: pemetaan skor semantik. Rumus ini adalah KALIBRASI YANG
DIRANCANG UNTUK SISTEM INI, bukan rumus bawaan SBERT.
"""


def calibrate_semantic_score(s: float, t: float, b: float, m: float) -> float:
    """
    s = rata-rata cosine similarity Top-K
    t = SEMANTIC_MIN_THRESHOLD, b = SEMANTIC_BASELINE, m = SEMANTIC_BELOW_BASELINE_MAX
    """
    assert 0 <= t < b < 1, "Harus 0 <= t < b < 1"

    if s < t:
        skor = 0.0
    elif s < b:
        skor = m * (s - t) / (b - t)
    else:
        skor = m + (100 - m) * (s - b) / (1 - b)

    return max(0.0, min(100.0, skor))
