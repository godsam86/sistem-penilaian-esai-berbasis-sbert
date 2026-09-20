from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.knowledge_base.models import KbChunk, KnowledgeBase, ProcessingStatus
from apps.knowledge_base.services.chunking import split_into_chunks
from apps.master_data.models import MasterGuru
from apps.users.models import Role, User


def _fake_embed_texts(texts):
    return [[0.1, 0.2, 0.3] for _ in texts]


def _fake_embed_text(text):
    return [0.1, 0.2, 0.3]


class ChunkingSettingsTests(TestCase):
    """Panjang chunk & overlap sekarang diatur lewat KB_CHUNK_MAX_WORDS / KB_CHUNK_OVERLAP_WORDS di .env."""

    def test_default_dari_settings_dipakai(self):
        from django.conf import settings
        self.assertEqual(settings.KB_CHUNK_MAX_WORDS, 150)
        self.assertEqual(settings.KB_CHUNK_OVERLAP_WORDS, 30)

    def test_override_eksplisit_tetap_bisa(self):
        teks = " ".join([f"kata{i}" for i in range(120)])
        chunks = split_into_chunks(teks, max_words=50, overlap=10)
        self.assertEqual(len(chunks[0].split()), 50)


class ChunkCurationTests(APITestCase):
    """Kurasi chunk: bisa dilihat, diedit (re-embed), dan dihapus -- atas permintaan Anda."""

    def setUp(self):
        self.login_url = reverse("login")
        guru_user = User.objects.create_user(email="kur-guru@sekolah.id", password="Rahasia1", nama="Guru", role=Role.GURU)
        self.guru = MasterGuru.objects.create(user=guru_user)

        self.kb = KnowledgeBase.objects.create(
            judul="Materi Tes", sumber="text", teks="isi materi",
            guru=self.guru, processing_status=ProcessingStatus.DONE,
        )
        self.chunk1 = KbChunk.objects.create(knowledge_base=self.kb, chunk_index=0, content="chunk pertama", embedding=[0.1, 0.2])
        self.chunk2 = KbChunk.objects.create(knowledge_base=self.kb, chunk_index=1, content="chunk kedua", embedding=[0.3, 0.4])

        self.token = self._login()

    def _login(self):
        res = self.client.post(self.login_url, {"email": "kur-guru@sekolah.id", "credential": "Rahasia1"})
        return res.data["access"]

    def test_guru_bisa_lihat_daftar_chunk(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.get(f"/api/knowledge-base/{self.kb.id}/chunks/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    @patch("apps.knowledge_base.services.embedding.embed_texts", side_effect=_fake_embed_texts)
    def test_guru_bisa_edit_isi_chunk_dan_reembed(self, mock_embed):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.patch(
            f"/api/knowledge-base/{self.kb.id}/chunks/{self.chunk1.id}/",
            {"content": "isi chunk yang sudah dikurasi"},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.chunk1.refresh_from_db()
        self.assertEqual(self.chunk1.content, "isi chunk yang sudah dikurasi")
        self.assertEqual(self.chunk1.embedding, [0.1, 0.2, 0.3])  # embedding baru dari stub

    def test_edit_chunk_kosong_ditolak(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.patch(f"/api/knowledge-base/{self.kb.id}/chunks/{self.chunk1.id}/", {"content": "   "})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guru_bisa_hapus_satu_chunk(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        res = self.client.delete(f"/api/knowledge-base/{self.kb.id}/chunks/{self.chunk1.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.kb.chunks.count(), 1)
        # KB tidak ikut ter-reprocess -- chunk lain tetap utuh.
        self.chunk2.refresh_from_db()
        self.assertEqual(self.chunk2.content, "chunk kedua")

    def test_guru_lain_tidak_bisa_akses_chunk_kb_orang_lain(self):
        other_user = User.objects.create_user(email="lain@sekolah.id", password="Rahasia1", nama="Guru Lain", role=Role.GURU)
        MasterGuru.objects.create(user=other_user)
        res_login = self.client.post(self.login_url, {"email": "lain@sekolah.id", "credential": "Rahasia1"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res_login.data['access']}")
        res = self.client.get(f"/api/knowledge-base/{self.kb.id}/chunks/")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
