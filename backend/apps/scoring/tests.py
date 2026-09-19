from unittest.mock import patch

from django.test import TestCase

from apps.answers.models import Jawaban
from apps.exams.models import Ujian, UjianSoal
from apps.knowledge_base.models import KbChunk, KnowledgeBase, ProcessingStatus
from apps.master_data.models import MasterGuru, MasterJurusan, MasterKelas, MasterSiswa
from apps.questions.models import ConceptUnit, Soal, SoalKnowledgeBase
from apps.scoring.services.calibration import calibrate_semantic_score
from apps.scoring.services.pipeline import score_jawaban
from apps.scoring.services.text_quality import evaluate_text_quality
from apps.users.models import Role, User

TEXT_PARAMS = {
    "TEXT_MIN_WORDS": 5,
    "TEXT_MIN_ALPHA_RATIO": 0.75,
    "TEXT_MIN_VOWEL_RATIO": 0.50,
    "TEXT_MAX_UPPER_RATIO": 0.50,
}

SCORING_PARAMS = {
    "SEMANTIC_WEIGHT": 0.80,
    "CONCEPT_WEIGHT": 0.20,
    "TOP_K": 3,
    "CONCEPT_THRESHOLD": 0.60,
    "SEMANTIC_MIN_THRESHOLD": 0.25,
    "SEMANTIC_BASELINE": 0.40,
    "SEMANTIC_BELOW_BASELINE_MAX": 20,
    "NOISE_PENALTY": 0.10,
    **TEXT_PARAMS,
}


class CalibrationTests(TestCase):
    """Bagian 19: verifikasi rumus kalibrasi persis sesuai spesifikasi."""

    def test_di_bawah_threshold_nol(self):
        self.assertEqual(calibrate_semantic_score(0.10, t=0.25, b=0.40, m=20), 0.0)

    def test_tepat_di_threshold_nol(self):
        self.assertEqual(calibrate_semantic_score(0.25, t=0.25, b=0.40, m=20), 0.0)

    def test_antara_threshold_dan_baseline_linear(self):
        # s tepat di tengah t..b -> setengah dari m
        hasil = calibrate_semantic_score(0.325, t=0.25, b=0.40, m=20)
        self.assertAlmostEqual(hasil, 10.0, places=2)

    def test_tepat_di_baseline(self):
        self.assertAlmostEqual(calibrate_semantic_score(0.40, t=0.25, b=0.40, m=20), 20.0, places=2)

    def test_di_atas_baseline(self):
        # s=0.70 -> m + (100-m)*(0.70-0.40)/(1-0.40) = 20 + 80*0.5 = 60
        self.assertAlmostEqual(calibrate_semantic_score(0.70, t=0.25, b=0.40, m=20), 60.0, places=2)

    def test_maksimum_seratus(self):
        self.assertAlmostEqual(calibrate_semantic_score(1.0, t=0.25, b=0.40, m=20), 100.0, places=2)


class TextQualityTests(TestCase):
    """Bagian 18: singkatan seperti CPU/RAM/SQL tidak otomatis jadi noise."""

    def test_jawaban_normal_lolos(self):
        hasil = evaluate_text_quality(
            "Fotosintesis adalah proses pembuatan makanan oleh tumbuhan menggunakan cahaya matahari.",
            TEXT_PARAMS,
        )
        self.assertTrue(hasil.lolos)

    def test_singkatan_teknis_tidak_otomatis_gagal(self):
        hasil = evaluate_text_quality(
            "CPU dan RAM adalah komponen penting dalam sebuah komputer modern saat ini.",
            TEXT_PARAMS,
        )
        self.assertTrue(hasil.lolos)

    def test_jawaban_terlalu_pendek_gagal(self):
        hasil = evaluate_text_quality("ya benar", TEXT_PARAMS)
        self.assertFalse(hasil.lolos)

    def test_jawaban_full_kapital_gagal(self):
        hasil = evaluate_text_quality("INI JAWABAN SAYA YANG DITULIS SELURUHNYA DENGAN HURUF KAPITAL", TEXT_PARAMS)
        self.assertFalse(hasil.lolos)

    def test_jawaban_kosong_setelah_strip(self):
        hasil = evaluate_text_quality("   ", TEXT_PARAMS)
        self.assertEqual(hasil.jumlah_kata, 0)
        self.assertFalse(hasil.lolos)


def _fake_embed_texts(texts):
    """
    Stub deterministik pengganti SBERT (tidak butuh download model/internet).
    Vektor dibuat dari hash kata supaya teks yang identik/mirip punya
    similarity tinggi, dan teks acak punya similarity rendah -- cukup untuk
    memvalidasi ALUR pipeline (bukan kualitas semantik model asli).
    """
    import hashlib

    import numpy as np

    vectors = []
    for t in texts:
        words = t.lower().split()
        vec = np.zeros(64)
        for w in words:
            idx = int(hashlib.md5(w.encode()).hexdigest(), 16) % 64
            vec[idx] += 1
        norm = np.linalg.norm(vec)
        vectors.append((vec / norm).tolist() if norm else vec.tolist())
    return vectors


class ScoringPipelineTests(TestCase):
    """Bagian 34: uji end-to-end pipeline penilaian dengan embedder di-stub."""

    def setUp(self):
        kelas = MasterKelas.objects.create(nama_kelas="X TKJ 1", tingkat="X")
        jurusan = MasterJurusan.objects.create(kode_jurusan="TKJ", nama_jurusan="Teknik Komputer Jaringan")

        guru_user = User.objects.create_user(email="guru@sekolah.id", password="x", nama="Guru", role=Role.GURU)
        self.guru = MasterGuru.objects.create(user=guru_user)

        siswa_user = User.objects.create_user(email="siswa@sekolah.id", password=None, nama="Siswa", role=Role.SISWA)
        self.siswa = MasterSiswa.objects.create(user=siswa_user, nisn="001", kelas=kelas, jurusan=jurusan)

        self.kb = KnowledgeBase.objects.create(
            judul="Materi Fotosintesis", sumber="text",
            teks="fotosintesis adalah proses tumbuhan membuat makanan menggunakan cahaya matahari",
            guru=self.guru, processing_status=ProcessingStatus.DONE,
        )
        with patch("apps.knowledge_base.services.embedding.embed_texts", side_effect=_fake_embed_texts):
            from apps.knowledge_base.services.chunking import split_into_chunks
            from apps.knowledge_base.services.embedding import embed_texts

            chunk_texts = split_into_chunks(self.kb.teks)
            embeddings = embed_texts(chunk_texts)
            for i, (content, emb) in enumerate(zip(chunk_texts, embeddings)):
                KbChunk.objects.create(knowledge_base=self.kb, chunk_index=i, content=content, embedding=emb)

        self.soal = Soal.objects.create(guru=self.guru, pertanyaan="Jelaskan proses fotosintesis.")
        SoalKnowledgeBase.objects.create(soal=self.soal, knowledge_base=self.kb)
        self.cu = ConceptUnit.objects.create(soal=self.soal, konsep="cahaya matahari", urutan=1)

        self.ujian = Ujian.objects.create(
            nama_ujian="UTS", jenis_ujian="UTS", guru=self.guru, kelas=kelas, jurusan=jurusan, token="ABCDE"
        )
        UjianSoal.objects.create(ujian=self.ujian, soal=self.soal, urutan=1)

    @patch("apps.knowledge_base.services.embedding.embed_texts", side_effect=_fake_embed_texts)
    def test_jawaban_kosong_skor_nol(self, mock_embed):
        jawaban = Jawaban.objects.create(ujian=self.ujian, siswa=self.siswa, soal=self.soal, jawaban_teks="")
        penilaian = score_jawaban(jawaban)
        self.assertEqual(penilaian.final_score, 0.0)
        self.assertEqual(penilaian.relevance_status, "gagal")
        self.assertEqual(penilaian.processing_status, "success")

    @patch("apps.knowledge_base.services.embedding.embed_texts", side_effect=_fake_embed_texts)
    def test_jawaban_relevan_dapat_skor_di_atas_nol(self, mock_embed):
        jawaban = Jawaban.objects.create(
            ujian=self.ujian, siswa=self.siswa, soal=self.soal,
            jawaban_teks="fotosintesis adalah proses tumbuhan membuat makanan menggunakan cahaya matahari",
        )
        penilaian = score_jawaban(jawaban)
        self.assertIsNotNone(penilaian.final_score)
        self.assertGreater(penilaian.final_score, 0.0)
        self.assertEqual(penilaian.relevance_status, "lolos")

    @patch("apps.knowledge_base.services.embedding.embed_texts", side_effect=_fake_embed_texts)
    def test_jawaban_tidak_relevan_skor_nol(self, mock_embed):
        jawaban = Jawaban.objects.create(
            ujian=self.ujian, siswa=self.siswa, soal=self.soal,
            jawaban_teks="kucing saya suka bermain bola di halaman setiap sore hari",
        )
        penilaian = score_jawaban(jawaban)
        self.assertEqual(penilaian.final_score, 0.0)
        self.assertEqual(penilaian.relevance_status, "gagal")

    def test_jawaban_ganda_ditolak_database(self):
        from django.db import IntegrityError

        Jawaban.objects.create(ujian=self.ujian, siswa=self.siswa, soal=self.soal, jawaban_teks="jawaban pertama")
        with self.assertRaises(IntegrityError):
            Jawaban.objects.create(ujian=self.ujian, siswa=self.siswa, soal=self.soal, jawaban_teks="jawaban kedua")
