# HiDOS Cell Cloud: Django web app and Celery analysis worker (same image)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# libglib2.0-0 is needed by opencv-python-headless
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/ requirements/
RUN pip install -r requirements/production.txt

COPY . .
RUN DJANGO_SETTINGS_MODULE=hidos.settings.production \
    DJANGO_SECRET_KEY=collectstatic-only-the-real-key-comes-from-the-environment \
    python manage.py collectstatic --noinput \
    && useradd --system --uid 1000 --home-dir /app hidos \
    && mkdir -p /data/media /data/chunked_uploads \
    && chown -R hidos /data

ENV DJANGO_SETTINGS_MODULE=hidos.settings.production \
    MEDIA_ROOT=/data/media \
    CHUNKED_UPLOAD_ROOT=/data/chunked_uploads
USER hidos
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=4)"
CMD ["gunicorn", "hidos.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-"]
