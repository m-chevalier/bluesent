FROM python:3.10-slim

WORKDIR /app

RUN pip install confluent_kafka websockets prometheus_client

COPY producer.py .
COPY allowed-list.txt .

CMD ["python", "producer.py"]