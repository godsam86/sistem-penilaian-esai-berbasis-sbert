from apps.activity_logs.models import LogActivity


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_activity(user, action, module, description="", request=None):
    """
    Pencatatan eksplisit untuk aktivitas penting (bagian 26 spesifikasi):
    login, logout, buat/ubah/nonaktifkan akun, KB, soal, ujian, kirim jawaban,
    proses penilaian, publikasi hasil. Dipanggil langsung dari view terkait,
    BUKAN lewat middleware blanket, agar log tetap bermakna dan tidak berisik.
    """
    LogActivity.objects.create(
        user=user if (user and getattr(user, "is_authenticated", False)) else None,
        action=action,
        module=module,
        description=description,
        ip_address=_client_ip(request),
    )
