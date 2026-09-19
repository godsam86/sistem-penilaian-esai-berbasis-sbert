# Sistem Penilaian Esai Otomatis Berbasis SBERT

Django + DRF + React (Vite) + PostgreSQL 15 + Docker Compose, untuk mata
pelajaran Bahasa Indonesia di lingkungan SMK.

## Struktur

```
.
├── backend/           # Django + DRF + SBERT
├── frontend/           # React + Vite + Nginx (produksi)
├── docker-compose.yml
└── .env.example
```

## Menjalankan dengan Docker (produksi)

```bash
cp .env.example .env
# edit .env: DJANGO_SECRET_KEY, POSTGRES_PASSWORD, ADMIN_PASSWORD, dst.

docker compose build
docker compose up -d
```

Saat container `backend` pertama kali start, `entrypoint.sh` otomatis:
1. Menunggu PostgreSQL siap.
2. Menjalankan `migrate`.
3. Membuat akun admin pertama dari `ADMIN_EMAIL` / `ADMIN_PASSWORD` di `.env`
   (lewat `python manage.py seed_admin` — aman dijalankan berulang, tidak
   akan membuat duplikat).
4. `collectstatic`.

Akses:
- Frontend: `http://localhost:3000`
- Backend API: diakses lewat proxy Nginx di `/api/` (tidak perlu port terpisah)
- Django admin (opsional, untuk debug): `http://localhost:3000/api/../admin/`
  — lebih mudah lewat `docker compose exec backend python manage.py shell`

Database di-bind hanya ke `127.0.0.1:5432` di mesin tempat Docker berjalan (lihat `docker-compose.yml`) -- tidak ter-expose ke jaringan/internet, tapi bisa diakses dari tool GUI seperti DBeaver/pgAdmin yang jalan di mesin yang sama. Untuk connect dari DBeaver:
- Host: `localhost` (atau `127.0.0.1`) -- **bukan** `db` (nama `db` cuma dikenali di dalam jaringan Docker Compose, bukan dari luar)
- Port: `5432`
- Database/User/Password: sesuai `POSTGRES_DB`/`POSTGRES_USER`/`POSTGRES_PASSWORD` di `.env` Anda

Kalau di-deploy ke server produksi dan tidak butuh akses langsung dari luar, baris `ports: - "127.0.0.1:5432:5432"` pada service `db` di `docker-compose.yml` boleh dihapus lagi.

## Migration & superuser manual (jika diperlukan)

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_admin
```

## Development lokal (tanpa Docker)

Backend:
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY=dev-secret
export POSTGRES_HOST=localhost   # arahkan ke Postgres lokal Anda
python manage.py migrate
python manage.py seed_admin
python manage.py runserver 0.0.0.0:8000
```

Testing (tidak butuh Postgres aktif, pakai SQLite in-memory):
```bash
python manage.py test --settings=config.settings_test
```

Frontend:
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000, proxy /api -> http://backend:8000 (ubah di vite.config.js jika backend lokal beda host)
```

## Deployment ke Ubuntu Server 22.04 LTS

1. Install Docker & Docker Compose plugin:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo apt install docker-compose-plugin
   ```
2. Clone/upload project ini ke server, misal ke `/opt/esai-sistem`.
3. `cp .env.example .env` lalu isi nilai produksi (secret key acak, password
   database yang kuat, `DJANGO_ALLOWED_HOSTS` diisi domain/IP server).
4. `docker compose up -d --build`
5. (Opsional) pasang Nginx/Caddy di level host sebagai reverse proxy ke port
   3000 dengan TLS (Let's Encrypt), jika ingin diakses lewat domain dengan HTTPS.
6. Backup rutin volume `db_data` (lihat bagian "Backup" di bawah).

## Backup database

```bash
docker compose exec db pg_dump -U <POSTGRES_USER> <POSTGRES_DB> > backup_$(date +%Y%m%d).sql
```

## Catatan penting

- Model SBERT (`paraphrase-multilingual-MiniLM-L12-v2`) diunduh otomatis dari
  HuggingFace saat pertama kali dipakai, lalu di-cache di volume Docker
  `sbert_cache` — butuh koneksi internet saat container backend pertama kali
  memproses Knowledge Base/jawaban, setelah itu tidak perlu unduh ulang.
- Tidak ada Celery/Redis/queue — semua pemrosesan (embedding, scoring)
  berjalan sinkron di request-response cycle, sesuai spesifikasi (bagian 2, 35).
- Parameter scoring di bagian 16 adalah konfigurasi awal, bukan parameter
  optimal — sesuaikan lewat `.env` berdasarkan hasil evaluasi penelitian Anda.
