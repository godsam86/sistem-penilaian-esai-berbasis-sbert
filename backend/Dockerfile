FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Torch CPU-only, dipasang TERPISAH dari requirements.txt dengan --index-url
# (bukan --extra-index-url) yang HANYA berlaku untuk perintah ini saja --
# tidak ada ambiguitas index, tidak ada resiko menarik build CUDA/NVIDIA.
# sentence-transformers==3.0.1 hanya butuh torch>=1.11.0 (tanpa batas atas),
# jadi begitu torch CPU ini terpasang, `pip install -r requirements.txt`
# di bawah tidak akan menimpanya dengan build lain.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.3.1

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media /app/staticfiles
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1"]
