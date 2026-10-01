"""
Bagian 29: ekspor hasil ke .xlsx / .pdf, menggunakan filter yang SAMA dengan tabel.

Format laporan:
  kop surat -> judul -> blok informasi ujian (semua dari database) ->
  tabel rekap per siswa -> ringkasan -> tanda tangan guru pengampu.

Nilai akhir per siswa = rata-rata skor seluruh soal dalam ujian (soal yang
tidak dijawab dihitung 0) -- bagian 21. Jika ada soal yang gagal diproses,
nilai TIDAK dipaksa jadi 0, melainkan ditandai (bagian 21).
"""
import io
from xml.sax.saxutils import escape

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.activity_logs.utils import log_activity
from apps.scoring.letterhead import add_excel_kop_surat, pdf_kop_surat_elements

JUDUL_LAPORAN = "LAPORAN HASIL PENILAIAN ESAI"
NAMA_SISTEM = "SMKN1 Pegagan Hilir - Sistem Penilaian Esai Otomatis"
BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]


# ────────────────────────── pengumpulan data ──────────────────────────

def _tgl(d):
    return f"{d.day} {BULAN[d.month - 1]} {d.year}"


def _gabung(nilai_list, maks=4):
    """Gabungkan nilai unik (urutan dipertahankan). Terlalu banyak -> diringkas."""
    unik = []
    for v in nilai_list:
        if v and v not in unik:
            unik.append(v)
    if not unik:
        return "-"
    if len(unik) > maks:
        return ", ".join(unik[:maks]) + f", dan {len(unik) - maks} lainnya"
    return ", ".join(unik)


def _tanggal_pelaksanaan(tanggal_list):
    if not tanggal_list:
        return "-"
    awal, akhir = min(tanggal_list), max(tanggal_list)
    if awal == akhir:
        return _tgl(awal)
    return f"{_tgl(awal)} s.d. {_tgl(akhir)}"


def _kumpulkan_laporan(queryset):
    """Ubah queryset Penilaian (1 baris per soal) jadi struktur laporan per siswa."""
    from apps.exams.models import UjianSoal

    penilaian_list = list(
        queryset.prefetch_related(None)
        .select_related("jawaban__ujian__guru__user")
        .order_by(
            "jawaban__ujian__nama_ujian",
            "jawaban__siswa__kelas__nama_kelas",
            "jawaban__siswa__user__nama",
            "jawaban__soal_id",
        )
    )

    total_soal_cache = {}
    grup = {}
    tanggal_list = []
    ujian_nama, ujian_jenis, kelas_list, jurusan_list, guru_list = [], [], [], [], []

    for p in penilaian_list:
        j = p.jawaban
        u = j.ujian
        s = j.siswa

        if u.id not in total_soal_cache:
            total_soal_cache[u.id] = UjianSoal.objects.filter(ujian_id=u.id).count()

        ujian_nama.append(u.nama_ujian)
        ujian_jenis.append(u.jenis_ujian)
        kelas_list.append(s.kelas.nama_kelas)
        jurusan_list.append(s.jurusan.nama_jurusan)
        guru_list.append(u.guru.user.nama)
        tanggal_list.append(timezone.localtime(j.submitted_at).date())

        key = (u.id, s.id)
        g = grup.setdefault(key, {
            "nama": s.user.nama, "nisn": s.nisn,
            "kelas": s.kelas.nama_kelas, "jurusan": s.jurusan.nama_jurusan,
            "ujian": u.nama_ujian, "total_soal": total_soal_cache[u.id],
            "skor": [], "gagal": False,
        })
        gagal = p.processing_status == "failed" or p.final_score is None
        g["gagal"] = g["gagal"] or gagal
        g["skor"].append(0.0 if gagal else float(p.final_score))
        g.setdefault("rincian", []).append({
            "soal": j.soal.pertanyaan,
            "skor": None if gagal else float(p.final_score),
            "status": "Gagal diproses" if gagal else "Berhasil",
        })

    baris = []
    for g in grup.values():
        total = max(g["total_soal"], len(g["skor"]))
        dijawab = len(g["skor"])
        nilai = None if g["gagal"] else round(sum(g["skor"]) / total, 2)

        catatan = []
        if g["gagal"]:
            catatan.append("Ada soal gagal diproses")
        if dijawab < total:
            catatan.append(f"{total - dijawab} soal belum dijawab")

        baris.append({**g, "dijawab": f"{dijawab}/{total}", "nilai": nilai, "keterangan": "; ".join(catatan)})

    nilai_angka = [b["nilai"] for b in baris if b["nilai"] is not None]
    guru_unik = [g for g in dict.fromkeys(guru_list) if g]

    return {
        "baris": baris,
        "multi_ujian": len(set(ujian_nama)) > 1,
        "info": [
            ("Nama Ujian", _gabung(ujian_nama)),
            ("Jenis Ujian", _gabung(ujian_jenis)),
            ("Tanggal Pelaksanaan", _tanggal_pelaksanaan(tanggal_list)),
            ("Kelas", _gabung(kelas_list)),
            ("Jurusan", _gabung(jurusan_list)),
            ("Guru Pengampu", _gabung(guru_list)),
        ],
        "guru_tunggal": guru_unik[0] if len(guru_unik) == 1 else None,
        "jumlah_peserta": len({(b["nisn"]) for b in baris}),
        "rata_rata": round(sum(nilai_angka) / len(nilai_angka), 2) if nilai_angka else None,
        "dicetak": _tgl(timezone.localdate()),
    }


def _kolom_rekap(multi_ujian):
    """(judul, lebar_excel, fraksi_pdf, kunci, rata_tengah)"""
    kolom = [
        ("No", 6, 0.05, None, True),
        ("Nama Siswa", 32, 0.25, "nama", False),
        ("NISN", 14, 0.11, "nisn", True),
        ("Kelas", 14, 0.10, "kelas", True),
        ("Jurusan", 26, 0.17, "jurusan", False),
    ]
    if multi_ujian:
        kolom.append(("Ujian", 24, 0.15, "ujian", False))
    kolom += [
        ("Dijawab", 11, 0.07, "dijawab", True),
        ("Nilai Akhir", 12, 0.08, "nilai", True),
        ("Keterangan", 30, 0.16, "keterangan", False),
    ]
    return kolom


def _format_nilai(n):
    return "-" if n is None else f"{n:.2f}"


# ─────────────────────────────── EXCEL ────────────────────────────────

_TIPIS = Side(style="thin", color="CBD5E1")
_BORDER = Border(left=_TIPIS, right=_TIPIS, top=_TIPIS, bottom=_TIPIS)
_HEADER_FILL = PatternFill("solid", fgColor="1D4ED8")
_ZEBRA_FILL = PatternFill("solid", fgColor="F1F5F9")


def _style_header(cell):
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = _HEADER_FILL
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = _BORDER


def export_xlsx(queryset, request):
    laporan = _kumpulkan_laporan(queryset)
    kolom = _kolom_rekap(laporan["multi_ujian"])
    n = len(kolom)
    terakhir = get_column_letter(n)

    wb = Workbook()
    ws = wb.active
    ws.title = "Rekap Nilai"

    for idx, (_, lebar, *_rest) in enumerate(kolom, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = lebar
    lebar_px = sum(int(k[1] * 7 + 5) for k in kolom)

    r = add_excel_kop_surat(ws, n, 1, lebar_px=lebar_px)

    # Judul
    r += 1
    ws.merge_cells(f"A{r}:{terakhir}{r}")
    ws[f"A{r}"] = JUDUL_LAPORAN
    ws[f"A{r}"].font = Font(bold=True, size=14)
    ws[f"A{r}"].alignment = Alignment(horizontal="center")
    r += 2

    # Blok informasi ujian (semua dari database)
    for label, nilai in laporan["info"]:
        ws.merge_cells(f"A{r}:B{r}")
        ws.merge_cells(f"C{r}:{terakhir}{r}")
        ws[f"A{r}"] = label
        ws[f"A{r}"].font = Font(bold=True)
        ws[f"C{r}"] = f": {nilai}"
        ws[f"C{r}"].alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
        if len(nilai) > 90:
            ws.row_dimensions[r].height = 32
        r += 1
    r += 1

    # Tabel rekap
    header_row = r
    for idx, (judul, *_rest) in enumerate(kolom, start=1):
        _style_header(ws.cell(row=r, column=idx, value=judul))
    ws.row_dimensions[r].height = 22
    r += 1

    for no, b in enumerate(laporan["baris"], start=1):
        for idx, (judul, _l, _f, kunci, tengah) in enumerate(kolom, start=1):
            if kunci is None:
                nilai = no
            elif kunci == "nilai":
                nilai = "-" if b["nilai"] is None else b["nilai"]
            else:
                nilai = b[kunci]
            cell = ws.cell(row=r, column=idx, value=nilai)
            cell.border = _BORDER
            cell.alignment = Alignment(horizontal="center" if tengah else "left", vertical="center", wrap_text=True)
            if kunci == "nilai" and b["nilai"] is not None:
                cell.number_format = "0.00"
            if no % 2 == 0:
                cell.fill = _ZEBRA_FILL
        r += 1

    if not laporan["baris"]:
        ws.merge_cells(f"A{r}:{terakhir}{r}")
        ws[f"A{r}"] = "Tidak ada data penilaian untuk filter ini."
        ws[f"A{r}"].alignment = Alignment(horizontal="center")
        r += 1

    # Ringkasan & tanda tangan
    r += 1
    ws[f"A{r}"] = "Jumlah Peserta"
    ws[f"A{r}"].font = Font(bold=True)
    ws[f"C{r}"] = f": {laporan['jumlah_peserta']}"
    r += 1
    ws[f"A{r}"] = "Rata-rata Nilai"
    ws[f"A{r}"].font = Font(bold=True)
    ws[f"C{r}"] = f": {_format_nilai(laporan['rata_rata'])}"
    r += 1
    ws[f"A{r}"] = "Dicetak pada"
    ws[f"A{r}"].font = Font(bold=True)
    ws[f"C{r}"] = f": {laporan['dicetak']}"

    if laporan["guru_tunggal"]:
        r += 2
        kolom_ttd = get_column_letter(max(n - 2, 3))
        ws.merge_cells(f"{kolom_ttd}{r}:{terakhir}{r}")
        ws[f"{kolom_ttd}{r}"] = "Guru Pengampu,"
        ws[f"{kolom_ttd}{r}"].alignment = Alignment(horizontal="center")
        r += 4
        ws.merge_cells(f"{kolom_ttd}{r}:{terakhir}{r}")
        ws[f"{kolom_ttd}{r}"] = laporan["guru_tunggal"]
        ws[f"{kolom_ttd}{r}"].font = Font(bold=True, underline="single")
        ws[f"{kolom_ttd}{r}"].alignment = Alignment(horizontal="center")

    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_title_rows = f"{header_row}:{header_row}"
    ws.oddFooter.left.text = NAMA_SISTEM
    ws.oddFooter.right.text = "Halaman &P dari &N"

    _sheet_rincian(wb, laporan)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    log_activity(request.user, "ekspor_xlsx", "penilaian", f"jumlah={queryset.count()}", request)
    response = HttpResponse(
        buffer.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=hasil-penilaian.xlsx"
    return response


def _sheet_rincian(wb, laporan):
    """Sheet kedua: rincian skor per soal untuk setiap siswa."""
    ws = wb.create_sheet("Rincian Per Soal")
    lebar = [("No", 6), ("Nama Siswa", 28), ("NISN", 14), ("Ujian", 24), ("Soal", 60), ("Skor", 10), ("Status", 16)]
    for idx, (_, w) in enumerate(lebar, start=1):
        ws.column_dimensions[get_column_letter(idx)].width = w

    ws.merge_cells("A1:G1")
    ws["A1"] = "RINCIAN SKOR PER SOAL"
    ws["A1"].font = Font(bold=True, size=13)
    ws["A1"].alignment = Alignment(horizontal="center")

    for idx, (judul, _) in enumerate(lebar, start=1):
        _style_header(ws.cell(row=3, column=idx, value=judul))

    r, no = 4, 1
    for b in laporan["baris"]:
        for item in b["rincian"]:
            nilai_baris = [no, b["nama"], b["nisn"], b["ujian"], item["soal"],
                           "-" if item["skor"] is None else item["skor"], item["status"]]
            for idx, v in enumerate(nilai_baris, start=1):
                cell = ws.cell(row=r, column=idx, value=v)
                cell.border = _BORDER
                cell.alignment = Alignment(
                    horizontal="center" if idx in (1, 3, 6, 7) else "left", vertical="top", wrap_text=True,
                )
                if idx == 6 and item["skor"] is not None:
                    cell.number_format = "0.00"
            r += 1
            no += 1

    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.print_title_rows = "3:3"


# ──────────────────────────────── PDF ─────────────────────────────────

def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawString(doc.leftMargin, 0.8 * cm, NAMA_SISTEM)
    canvas.drawRightString(doc.leftMargin + doc.width, 0.8 * cm, f"Halaman {canvas.getPageNumber()}")
    canvas.restoreState()


def export_pdf(queryset, request):
    laporan = _kumpulkan_laporan(queryset)
    kolom = _kolom_rekap(laporan["multi_ujian"])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.2 * cm, bottomMargin=1.6 * cm,
        title=JUDUL_LAPORAN, author=NAMA_SISTEM,
    )

    dasar = getSampleStyleSheet()["Normal"]
    s_judul = ParagraphStyle("judul", parent=dasar, fontName="Helvetica-Bold", fontSize=13, leading=16, alignment=TA_CENTER)
    s_label = ParagraphStyle("label", parent=dasar, fontName="Helvetica-Bold", fontSize=9, leading=12)
    s_isi = ParagraphStyle("isi", parent=dasar, fontSize=9, leading=12)
    s_sel = ParagraphStyle("sel", parent=dasar, fontSize=8, leading=10, alignment=TA_LEFT)
    s_sel_c = ParagraphStyle("sel_c", parent=s_sel, alignment=TA_CENTER)
    s_head = ParagraphStyle("head", parent=s_sel_c, fontName="Helvetica-Bold", textColor=colors.white)
    s_kecil = ParagraphStyle("kecil", parent=dasar, fontSize=8, leading=10, textColor=colors.HexColor("#475569"))

    def P(teks, gaya):
        return Paragraph(escape(str(teks)), gaya)

    elemen = pdf_kop_surat_elements(doc.width)
    elemen += [P(JUDUL_LAPORAN, s_judul), Spacer(1, 0.25 * cm)]
    elemen.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94a3b8")))
    elemen.append(Spacer(1, 0.2 * cm))

    # Blok informasi ujian: dua kolom label/isi berdampingan
    info = dict(laporan["info"])
    kiri = [("Nama Ujian", info["Nama Ujian"]), ("Jenis Ujian", info["Jenis Ujian"]),
            ("Tanggal Pelaksanaan", info["Tanggal Pelaksanaan"])]
    kanan = [("Kelas", info["Kelas"]), ("Jurusan", info["Jurusan"]), ("Guru Pengampu", info["Guru Pengampu"])]
    sisa = doc.width - (3.8 + 0.4 + 0.6 + 3.0 + 0.4) * cm
    lebar_info = [3.8 * cm, 0.4 * cm, sisa * 0.5, 0.6 * cm, 3.0 * cm, 0.4 * cm, sisa * 0.5]
    info_rows = [
        [P(a[0], s_label), P(":", s_isi), P(a[1], s_isi), "", P(b[0], s_label), P(":", s_isi), P(b[1], s_isi)]
        for a, b in zip(kiri, kanan)
    ]
    info_tbl = Table(info_rows, colWidths=lebar_info)
    info_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))
    elemen += [info_tbl, Spacer(1, 0.2 * cm)]
    elemen.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94a3b8")))
    elemen.append(Spacer(1, 0.3 * cm))

    # Tabel rekap
    total_frak = sum(k[2] for k in kolom)
    lebar_kolom = [doc.width * k[2] / total_frak for k in kolom]
    data = [[P(k[0], s_head) for k in kolom]]
    for no, b in enumerate(laporan["baris"], start=1):
        baris = []
        for judul, _l, _f, kunci, tengah in kolom:
            if kunci is None:
                teks = no
            elif kunci == "nilai":
                teks = _format_nilai(b["nilai"])
            else:
                teks = b[kunci]
            baris.append(P(teks, s_sel_c if tengah else s_sel))
        data.append(baris)
    if not laporan["baris"]:
        data.append([P("Tidak ada data penilaian untuk filter ini.", s_sel_c)] + [""] * (len(kolom) - 1))

    tabel = Table(data, colWidths=lebar_kolom, repeatRows=1)
    gaya = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
    ]
    if not laporan["baris"]:
        gaya.append(("SPAN", (0, 1), (-1, 1)))
    tabel.setStyle(TableStyle(gaya))
    elemen.append(tabel)

    # Ringkasan + tanda tangan (dijaga tidak terpisah antar halaman)
    ringkasan = Paragraph(
        f"<b>Jumlah peserta:</b> {laporan['jumlah_peserta']} &nbsp;&nbsp;&nbsp; "
        f"<b>Rata-rata nilai:</b> {_format_nilai(laporan['rata_rata'])}", s_isi,
    )
    blok_akhir = [Spacer(1, 0.4 * cm), ringkasan, Spacer(1, 0.1 * cm),
                  P(f"Dicetak pada {laporan['dicetak']}", s_kecil)]
    if laporan["guru_tunggal"]:
        ttd = Table(
            [["", Paragraph(f"Guru Pengampu,<br/><br/><br/><br/><b><u>{escape(laporan['guru_tunggal'])}</u></b>",
                            ParagraphStyle("ttd", parent=s_isi, alignment=TA_CENTER))]],
            colWidths=[doc.width - 7 * cm, 7 * cm],
        )
        ttd.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        blok_akhir += [Spacer(1, 0.4 * cm), ttd]
    elemen.append(KeepTogether(blok_akhir))

    doc.build(elemen, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)

    log_activity(request.user, "ekspor_pdf", "penilaian", f"jumlah={queryset.count()}", request)
    response = HttpResponse(buffer.read(), content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=hasil-penilaian.pdf"
    return response