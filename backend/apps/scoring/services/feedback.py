"""
Bagian 22: feedback dibuat backend dengan TEMPLATE BERBASIS ATURAN, bukan
generative AI. SBERT hanya dipakai untuk embedding/similarity -- feedback
TIDAK PERNAH mengklaim "jawaban pasti benar" hanya karena similarity tinggi.
"""


def build_feedback(
    *,
    jawaban_kosong: bool,
    relevance_status: str,
    text_quality_status: str,
    text_quality_alasan: str,
    concept_detail: list,
    concept_units_map: dict,
) -> str:
    if jawaban_kosong:
        return "Jawaban tidak diisi (kosong)."

    baris = []

    if relevance_status == "gagal":
        baris.append(
            "Jawaban Anda terdeteksi secara semantik tidak relevan dengan materi rujukan "
            "untuk soal ini. Coba tinjau ulang kembali konsep utama yang ditanyakan."
        )
        return " ".join(baris)

    if text_quality_status == "gagal":
        baris.append(
            f"Jawaban terindikasi bermasalah dari sisi kualitas teks ({text_quality_alasan}). "
            "Ini BUKAN penilaian atas kebenaran konten, hanya indikasi kualitas penulisan -- "
            "skor diberi penalti karena teks sulit dinilai secara semantik."
        )

    terdeteksi = [d for d in concept_detail if d["detected"]]
    belum = [d for d in concept_detail if not d["detected"]]

    if terdeteksi:
        nama_terdeteksi = ", ".join(concept_units_map[d["concept_unit_id"]] for d in terdeteksi)
        baris.append(f"Konsep yang terdeteksi secara semantik: {nama_terdeteksi}.")
    if belum:
        nama_belum = ", ".join(concept_units_map[d["concept_unit_id"]] for d in belum)
        baris.append(
            f"Konsep yang belum terdeteksi secara semantik: {nama_belum}. "
            "Pertimbangkan untuk melengkapi jawaban dengan konsep tersebut."
        )
    if not concept_detail:
        baris.append(
            "Jawaban terdeteksi cukup mirip secara semantik dengan materi rujukan. "
            "Similarity tinggi hanya menunjukkan kemiripan semantik, bukan bukti mutlak kebenaran."
        )

    return " ".join(baris)
