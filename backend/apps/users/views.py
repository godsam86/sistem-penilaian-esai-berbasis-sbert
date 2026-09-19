from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.activity_logs.utils import log_activity
from apps.users.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    UserProfileSerializer,
)

# Pesan generik -- jangan pernah bilang "email tidak ditemukan" vs
# "password salah" secara berbeda (bagian 4: tidak membocorkan keberadaan akun).
GENERIC_LOGIN_ERROR = "Email atau kredensial tidak valid, atau akun tidak aktif."


class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            credential=serializer.validated_data["credential"],
        )
        if user is None:
            return Response({"detail": GENERIC_LOGIN_ERROR}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        log_activity(user, action="login", module="auth", request=request)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserProfileSerializer(user).data,
            }
        )


class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                # Token sudah invalid/expired -- tetap anggap logout berhasil.
                pass
        log_activity(request.user, action="logout", module="auth", request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileView(APIView):
    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    Berlaku untuk SEMUA role (admin/guru/siswa). Verifikasi cukup dengan
    mencocokkan email akun yang sedang login -- bukan password lama.
    """

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["email"].strip().lower() != request.user.email.lower():
            return Response({"detail": "Email tidak sesuai dengan akun Anda."}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        log_activity(request.user, action="ubah_password", module="auth", request=request)
        return Response({"detail": "Password berhasil diubah."})
