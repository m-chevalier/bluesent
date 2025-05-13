FROM python:3.10-slim

WORKDIR /app

COPY producer.py .

RUN pip install confluent_kafka

CMD ["python", "producer.py"]