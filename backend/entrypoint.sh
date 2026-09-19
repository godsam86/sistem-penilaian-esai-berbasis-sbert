#!/bin/sh
set -e

echo "Menunggu PostgreSQL siap di ${POSTGRES_HOST}:${POSTGRES_PORT}..."
python << 'PYEOF'
import os
import socket
import time

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))

for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("PostgreSQL siap.")
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("PostgreSQL tidak merespons setelah 60 detik.")
PYEOF

python manage.py migrate --noinput
python manage.py seed_admin
python manage.py collectstatic --noinput

exec "$@"
