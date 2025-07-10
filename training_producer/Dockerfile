FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY training_producer.py .

COPY training_wordlist.txt .

RUN chown -R appuser:appgroup /app

USER appuser

CMD ["python", "training_producer.py"]