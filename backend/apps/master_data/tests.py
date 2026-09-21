from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.master_data.models import MasterAdmin
from apps.users.models import Role, User


class AdminAccountTests(APITestCase):
    """Bagian 25 (perluasan): admin bisa kelola akun admin lain lewat master_admin."""

    def setUp(self):
        self.login_url = reverse("login")
        self.admin_url = reverse("master-admin-list")

        user = User.objects.create_user(email="super@sekolah.id", password="Rahasia1", nama="Super Admin", role=Role.ADMIN)
        MasterAdmin.objects.create(user=user, jabatan="Kepala Sekolah")

    def _token(self):
        res = self.client.post(self.login_url, {"email": "super@sekolah.id", "credential": "Rahasia1"})
        return res.data["access"]

    def test_admin_bisa_lihat_daftar_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        res = self.client.get(self.admin_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_admin_bisa_buat_admin_baru(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        res = self.client.post(self.admin_url, {
            "nama": "Admin Kedua", "email": "admin2@sekolah.id", "password": "Rahasia2", "jabatan": "Wakil Kepala",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="admin2@sekolah.id", role=Role.ADMIN).exists())

    def test_admin_tidak_bisa_nonaktifkan_akun_sendiri(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        my_admin = MasterAdmin.objects.get(user__email="super@sekolah.id")
        res = self.client.delete(f"{self.admin_url}{my_admin.id}/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_bisa_nonaktifkan_admin_lain(self):
        other_user = User.objects.create_user(email="other@sekolah.id", password="x", nama="Admin Lain", role=Role.ADMIN)
        other_admin = MasterAdmin.objects.create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        res = self.client.delete(f"{self.admin_url}{other_admin.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        other_user.refresh_from_db()
        self.assertEqual(other_user.status, 0)


class GuruAccountEditDeactivateTests(APITestCase):
    """
    Regresi bug: field `id` di response HARUS id baris master_guru sendiri,
    bukan id baris users -- supaya edit/nonaktifkan pakai id yang benar
    (persis alur yang dipakai frontend: pakai id dari hasil list/create).
    """

    def setUp(self):
        self.login_url = reverse("login")
        self.guru_url = reverse("master-guru-list")
        admin_user = User.objects.create_user(email="admin-g@sekolah.id", password="Rahasia1", nama="Admin", role=Role.ADMIN)
        MasterAdmin.objects.create(user=admin_user)
        res = self.client.post(self.login_url, {"email": "admin-g@sekolah.id", "credential": "Rahasia1"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_id_yang_dikembalikan_adalah_id_master_guru_bukan_id_user(self):
        from apps.master_data.models import MasterGuru

        res = self.client.post(self.guru_url, {"nama": "Guru A", "email": "gurua@sekolah.id", "password": "Rahasia1"})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        master_guru = MasterGuru.objects.get(user__email="gurua@sekolah.id")
        self.assertEqual(res.data["id"], master_guru.id)

    def test_edit_guru_pakai_id_dari_response_berhasil(self):
        res_create = self.client.post(self.guru_url, {"nama": "Guru B", "email": "gurub@sekolah.id", "password": "Rahasia1"})
        guru_id = res_create.data["id"]
        res_edit = self.client.put(f"{self.guru_url}{guru_id}/", {"nama": "Guru B Diubah", "email": "gurub@sekolah.id"})
        self.assertEqual(res_edit.status_code, status.HTTP_200_OK)
        self.assertEqual(res_edit.data["nama"], "Guru B Diubah")

    def test_nonaktifkan_guru_pakai_id_dari_response_berhasil(self):
        res_create = self.client.post(self.guru_url, {"nama": "Guru C", "email": "guruc@sekolah.id", "password": "Rahasia1"})
        guru_id = res_create.data["id"]
        res_delete = self.client.delete(f"{self.guru_url}{guru_id}/")
        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)


class SiswaAccountEditDeactivateTests(APITestCase):
    """Regresi bug yang sama untuk master_siswa (laporan Anda persis di sini)."""

    def setUp(self):
        from apps.master_data.models import MasterJurusan, MasterKelas

        self.login_url = reverse("login")
        self.siswa_url = reverse("master-siswa-list")
        admin_user = User.objects.create_user(email="admin-s@sekolah.id", password="Rahasia1", nama="Admin", role=Role.ADMIN)
        MasterAdmin.objects.create(user=admin_user)
        res = self.client.post(self.login_url, {"email": "admin-s@sekolah.id", "credential": "Rahasia1"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

        self.kelas = MasterKelas.objects.create(nama_kelas="X TKJ 1", tingkat="X")
        self.jurusan = MasterJurusan.objects.create(kode_jurusan="TKJ", nama_jurusan="Teknik Komputer Jaringan")

    def _create_siswa(self, nisn="001"):
        return self.client.post(self.siswa_url, {
            "nama": "Siswa A", "email": f"siswa{nisn}@sekolah.id", "nisn": nisn,
            "kelas": self.kelas.id, "jurusan": self.jurusan.id,
        })

    def test_edit_email_dan_nama_siswa_pakai_id_dari_response_berhasil(self):
        res_create = self._create_siswa("1001")
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)
        siswa_id = res_create.data["id"]

        res_edit = self.client.put(f"{self.siswa_url}{siswa_id}/", {
            "nama": "Siswa A Diubah", "email": "siswa1001-baru@sekolah.id",
            "nisn": "1001", "kelas": self.kelas.id, "jurusan": self.jurusan.id,
        })
        self.assertEqual(res_edit.status_code, status.HTTP_200_OK)
        self.assertEqual(res_edit.data["email"], "siswa1001-baru@sekolah.id")

    def test_nonaktifkan_siswa_pakai_id_dari_response_berhasil(self):
        res_create = self._create_siswa("1002")
        siswa_id = res_create.data["id"]
        res_delete = self.client.delete(f"{self.siswa_url}{siswa_id}/")
        self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)


class AktifkanKembaliTests(APITestCase):
    """Guru/siswa/admin yang sudah dinonaktifkan bisa diaktifkan lagi lewat action `aktifkan`."""

    def setUp(self):
        self.login_url = reverse("login")
        admin_user = User.objects.create_user(email="admin-akt@sekolah.id", password="Rahasia1", nama="Admin", role=Role.ADMIN)
        MasterAdmin.objects.create(user=admin_user)
        res = self.client.post(self.login_url, {"email": "admin-akt@sekolah.id", "credential": "Rahasia1"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_aktifkan_guru_yang_nonaktif(self):
        guru_url = reverse("master-guru-list")
        res_create = self.client.post(guru_url, {"nama": "Guru Nonaktif", "email": "guru-non@sekolah.id", "password": "Rahasia1"})
        guru_id = res_create.data["id"]
        self.client.delete(f"{guru_url}{guru_id}/")

        res_aktif = self.client.post(f"{guru_url}{guru_id}/aktifkan/")
        self.assertEqual(res_aktif.status_code, status.HTTP_200_OK)
        self.assertEqual(res_aktif.data["status"], 1)

    def test_aktifkan_siswa_yang_nonaktif(self):
        from apps.master_data.models import MasterJurusan, MasterKelas

        kelas = MasterKelas.objects.create(nama_kelas="X TKJ 2", tingkat="X")
        jurusan = MasterJurusan.objects.create(kode_jurusan="TKJ2", nama_jurusan="TKJ 2")
        siswa_url = reverse("master-siswa-list")
        res_create = self.client.post(siswa_url, {
            "nama": "Siswa Nonaktif", "email": "siswa-non@sekolah.id", "nisn": "9999",
            "kelas": kelas.id, "jurusan": jurusan.id,
        })
        siswa_id = res_create.data["id"]
        self.client.delete(f"{siswa_url}{siswa_id}/")

        res_aktif = self.client.post(f"{siswa_url}{siswa_id}/aktifkan/")
        self.assertEqual(res_aktif.status_code, status.HTTP_200_OK)
        self.assertEqual(res_aktif.data["status"], 1)

    def test_aktifkan_admin_yang_nonaktif(self):
        admin_url = reverse("master-admin-list")
        other_user = User.objects.create_user(email="admin-non@sekolah.id", password="x", nama="Admin Nonaktif", role=Role.ADMIN)
        other_admin = MasterAdmin.objects.create(user=other_user)
        self.client.delete(f"{admin_url}{other_admin.id}/")

        res_aktif = self.client.post(f"{admin_url}{other_admin.id}/aktifkan/")
        self.assertEqual(res_aktif.status_code, status.HTTP_200_OK)
        other_user.refresh_from_db()
        self.assertEqual(other_user.status, 1)