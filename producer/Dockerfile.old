FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

RUN pip install confluent_kafka websockets prometheus_client fasttext argostranslate "numpy<2.0"

COPY producer.py .
COPY allowed-list.txt .
COPY lid.176.ftz .
COPY translation.py .
COPY utils.py .

ENV ARGOS_PACKAGES_DIR=/app/data/argos-translate/packages/

CMD ["python", "-u", "producer.py"]