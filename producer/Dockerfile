FROM python:3.10-slim

WORKDIR /app

COPY producer.py .
COPY allowed-list.txt .

RUN pip install confluent_kafka websockets prometheus_client

CMD ["python", "producer.py"]