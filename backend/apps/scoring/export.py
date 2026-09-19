"""Bagian 29: ekspor hasil ke .xlsx / .pdf, menggunakan filter yang SAMA dengan tabel."""
import io

from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from apps.activity_logs.utils import log_activity

HEADERS = ["Nama Siswa", "NISN", "Kelas", "Jurusan", "Ujian", "Jenis", "Skor Akhir", "Status"]


def _rows_from_queryset(qs):
    rows = []
    for p in qs:
        j = p.jawaban
        rows.append(
            [
                j.siswa.user.nama,
                j.siswa.nisn,
                j.siswa.kelas.nama_kelas,
                j.siswa.jurusan.nama_jurusan,
                j.ujian.nama_ujian,
                j.ujian.jenis_ujian,
                p.final_score if p.final_score is not None else "-",
                p.processing_status,
            ]
        )
    return rows


def export_xlsx(queryset, request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Hasil Penilaian"
    ws.append(HEADERS)
    for row in _rows_from_queryset(queryset):
        ws.append(row)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    log_activity(request.user, "ekspor_xlsx", "penilaian", f"jumlah={queryset.count()}", request)
    response = HttpResponse(buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=hasil-penilaian.xlsx"
    return response


def export_pdf(queryset, request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    data = [HEADERS] + _rows_from_queryset(queryset)
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    doc.build([table])
    buffer.seek(0)

    log_activity(request.user, "ekspor_pdf", "penilaian", f"jumlah={queryset.count()}", request)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=hasil-penilaian.pdf"
    return response
