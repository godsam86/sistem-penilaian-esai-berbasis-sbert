from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.master_data.models import MasterGuru, MasterJurusan, MasterKelas, MasterSiswa
from apps.users.models import Role, Status, User


class AuthTests(APITestCase):
    """Bagian 34: login admin/guru/siswa, akun nonaktif, password salah, tanpa auth."""

    def setUp(self):
        self.login_url = reverse("login")

        self.admin = User.objects.create_user(
            email="admin@sekolah.id", password="RahasiaAdmin1", nama="Admin Satu", role=Role.ADMIN,
        )

        guru_user = User.objects.create_user(
            email="guru@sekolah.id", password="RahasiaGuru1", nama="Guru Satu", role=Role.GURU,
        )
        MasterGuru.objects.create(user=guru_user, nip="123456")

        kelas = MasterKelas.objects.create(nama_kelas="X TKJ 1", tingkat="X")
        jurusan = MasterJurusan.objects.create(kode_jurusan="TKJ", nama_jurusan="Teknik Komputer Jaringan")

        siswa_user = User.objects.create_user(
            email="siswa@sekolah.id", password=None, nama="Siswa Satu", role=Role.SISWA,
        )
        self.siswa_profile = MasterSiswa.objects.create(
            user=siswa_user, nisn="0012345678", kelas=kelas, jurusan=jurusan,
        )

        self.nonaktif_user = User.objects.create_user(
            email="nonaktif@sekolah.id", password="Rahasia1", nama="Nonaktif",
            role=Role.GURU, status=Status.NONAKTIF,
        )
        MasterGuru.objects.create(user=self.nonaktif_user)

    def test_login_admin_sukses(self):
        res = self.client.post(self.login_url, {"email": "admin@sekolah.id", "credential": "RahasiaAdmin1"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["role"], "admin")
        self.assertIn("access", res.data)

    def test_login_guru_sukses(self):
        res = self.client.post(self.login_url, {"email": "guru@sekolah.id", "credential": "RahasiaGuru1"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["role"], "guru")

    def test_login_siswa_dengan_nisn_sukses(self):
        res = self.client.post(self.login_url, {"email": "siswa@sekolah.id", "credential": "0012345678"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["user"]["role"], "siswa")
        self.assertEqual(res.data["user"]["siswa"]["nisn"], "0012345678")

    def test_login_siswa_nisn_salah_gagal(self):
        res = self.client.post(self.login_url, {"email": "siswa@sekolah.id", "credential": "salah"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_password_salah_gagal(self):
        res = self.client.post(self.login_url, {"email": "guru@sekolah.id", "credential": "salahpassword"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_akun_nonaktif_gagal(self):
        res = self.client.post(self.login_url, {"email": "nonaktif@sekolah.id", "credential": "Rahasia1"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_email_tidak_ada_pesan_generik(self):
        res_tidak_ada = self.client.post(self.login_url, {"email": "hantu@sekolah.id", "credential": "apapun"})
        res_salah_pw = self.client.post(self.login_url, {"email": "guru@sekolah.id", "credential": "apapun"})
        # Pesan error harus sama -- tidak membocorkan apakah email terdaftar (bagian 4).
        self.assertEqual(res_tidak_ada.data["detail"], res_salah_pw.data["detail"])

    def test_akses_endpoint_terlindungi_tanpa_token_ditolak(self):
        res = self.client.get(reverse("me"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_akses_endpoint_dengan_token_berhasil(self):
        login_res = self.client.post(self.login_url, {"email": "admin@sekolah.id", "credential": "RahasiaAdmin1"})
        token = login_res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.get(reverse("me"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], "admin@sekolah.id")


class AuthorizationTests(APITestCase):
    """Bagian 31: guru/admin/siswa hanya mengakses sesuai izinnya."""

    def setUp(self):
        self.login_url = reverse("login")
        self.kelas_url = reverse("master-kelas-list")

        User.objects.create_user(email="admin2@sekolah.id", password="Rahasia1", nama="Admin", role=Role.ADMIN)
        guru_user = User.objects.create_user(
            email="guru2@sekolah.id", password="Rahasia1", nama="Guru", role=Role.GURU
        )
        MasterGuru.objects.create(user=guru_user)

    def _token_for(self, email, credential):
        res = self.client.post(self.login_url, {"email": email, "credential": credential})
        return res.data["access"]

    def test_admin_boleh_akses_master_kelas(self):
        token = self._token_for("admin2@sekolah.id", "Rahasia1")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.get(self.kelas_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_guru_boleh_lihat_daftar_kelas_tapi_tidak_boleh_membuat(self):
        token = self._token_for("guru2@sekolah.id", "Rahasia1")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res_list = self.client.get(self.kelas_url)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        res_create = self.client.post(self.kelas_url, {"nama_kelas": "X TKJ 2", "tingkat": "X"})
        self.assertEqual(res_create.status_code, status.HTTP_403_FORBIDDEN)


class ChangePasswordTests(APITestCase):
    """Ubah password berlaku untuk admin/guru/siswa, verifikasi lewat kecocokan email."""

    def setUp(self):
        self.login_url = reverse("login")
        self.change_url = reverse("change-password")

        self.admin = User.objects.create_user(email="cp-admin@sekolah.id", password="Lama123!", nama="Admin", role=Role.ADMIN)

        guru_user = User.objects.create_user(email="cp-guru@sekolah.id", password="Lama123!", nama="Guru", role=Role.GURU)
        MasterGuru.objects.create(user=guru_user)

        kelas = MasterKelas.objects.create(nama_kelas="X TKJ 1", tingkat="X")
        jurusan = MasterJurusan.objects.create(kode_jurusan="TKJ", nama_jurusan="Teknik Komputer Jaringan")
        siswa_user = User.objects.create_user(email="cp-siswa@sekolah.id", password=None, nama="Siswa", role=Role.SISWA)
        MasterSiswa.objects.create(user=siswa_user, nisn="0099", kelas=kelas, jurusan=jurusan)

    def _token_for(self, email, credential):
        res = self.client.post(self.login_url, {"email": email, "credential": credential})
        return res.data["access"]

    def test_admin_ubah_password_dengan_email_benar(self):
        token = self._token_for("cp-admin@sekolah.id", "Lama123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.post(self.change_url, {"email": "cp-admin@sekolah.id", "new_password": "Baru123456!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_guru_ubah_password_email_salah_ditolak(self):
        token = self._token_for("cp-guru@sekolah.id", "Lama123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.post(self.change_url, {"email": "salah@sekolah.id", "new_password": "Baru123456!"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_siswa_juga_bisa_ubah_password(self):
        token = self._token_for("cp-siswa@sekolah.id", "0099")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        res = self.client.post(self.change_url, {"email": "cp-siswa@sekolah.id", "new_password": "Baru123456!"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
