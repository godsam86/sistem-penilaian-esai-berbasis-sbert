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
