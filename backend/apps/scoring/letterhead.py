"""
Kop surat SMKN1 Pegagan Hilir untuk ekspor hasil penilaian.

Gambar kop surat disisipkan sebagai GAMBAR UTUH (bukan teks) -- untuk
menggantinya cukup timpa file assets/kop_surat.png.
"""
import math
import os

from openpyxl.drawing.image import Image as XLImage
from openpyxl.utils import get_column_letter
from reportlab.lib.units import cm
from reportlab.platypus import Image as PDFImage
from reportlab.platypus import Spacer

KOP_SURAT_PATH = os.path.join(os.path.dirname(__file__), "assets", "kop_surat.png")
_ASPECT_RATIO = 262 / 1323  # tinggi/lebar gambar asli -- supaya tidak gepeng saat di-resize
_TINGGI_BARIS_PT = 20


def pdf_kop_surat_elements(doc_width):
    """Elemen reportlab (Image + Spacer) untuk ditaruh paling atas sebelum isi laporan."""
    if not os.path.exists(KOP_SURAT_PATH):
        return []
    lebar = doc_width
    tinggi = lebar * _ASPECT_RATIO
    return [
        PDFImage(KOP_SURAT_PATH, width=lebar, height=tinggi),
        Spacer(1, 0.4 * cm),
    ]


def add_excel_kop_surat(worksheet, jumlah_kolom, baris_header, lebar_px=780):
    """
    Tempel kop surat di atas worksheet, lebarnya mengikuti `lebar_px`
    (samakan dengan total lebar kolom tabel). Mengembalikan nomor baris
    pertama yang AMAN dipakai setelah kop surat.
    """
    if not os.path.exists(KOP_SURAT_PATH):
        return baris_header

    tinggi_px = int(lebar_px * _ASPECT_RATIO)
    px_per_baris = _TINGGI_BARIS_PT * 96 / 72
    jumlah_baris = max(1, math.ceil(tinggi_px / px_per_baris))

    img = XLImage(KOP_SURAT_PATH)
    img.width = lebar_px
    img.height = tinggi_px
    worksheet.add_image(img, "A1")

    kolom_terakhir = get_column_letter(max(jumlah_kolom, 1))
    worksheet.merge_cells(f"A1:{kolom_terakhir}{jumlah_baris}")
    for i in range(1, jumlah_baris + 1):
        worksheet.row_dimensions[i].height = _TINGGI_BARIS_PT

    return jumlah_baris + 1