FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/backend

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . /srv/backend

RUN mkdir -p /srv/data/raw /srv/data/processed /srv/data/incoming \
             /srv/data/archive /srv/data/metadata /srv/data/documents \
             /srv/data/exports/powerbi /srv/data/chroma /srv/data/db

EXPOSE 8000

CMD ["sh", "-c", "mkdir -p /srv/data/db /srv/data/chroma /srv/data/incoming /srv/data/processed /srv/data/raw /srv/data/archive /srv/data/metadata /srv/data/documents /srv/data/exports/powerbi && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
