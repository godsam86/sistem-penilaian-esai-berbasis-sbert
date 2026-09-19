"""
Ekstraksi teks dari file Knowledge Base (bagian 9 spesifikasi).
Mengembalikan (teks, butuh_ocr: bool).
"""
import io


class ExtractionError(Exception):
    pass


def extract_text(file_field, sumber: str) -> tuple[str, bool]:
    sumber = sumber.lower()
    file_field.seek(0)
    raw = file_field.read()

    if sumber == "pdf":
        return _extract_pdf(raw)
    if sumber == "docx":
        return _extract_docx(raw)
    if sumber == "doc":
        raise ExtractionError(
            "Format .doc lama membutuhkan dependensi tambahan (antiword/libreoffice) "
            "yang tidak tersedia. Silakan konversi ke .docx."
        )
    raise ExtractionError(f"Sumber file tidak didukung: {sumber}")


def _extract_pdf(raw: bytes) -> tuple[str, bool]:
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(raw))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    full_text = "\n".join(pages_text).strip()

    # PDF hasil scan biasanya tidak punya teks yang bisa diekstrak sama sekali.
    butuh_ocr = len(full_text) < 20
    return full_text, butuh_ocr


def _extract_docx(raw: bytes) -> tuple[str, bool]:
    import docx

    document = docx.Document(io.BytesIO(raw))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    full_text = "\n".join(paragraphs).strip()
    return full_text, False
