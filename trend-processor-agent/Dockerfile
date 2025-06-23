FROM python:3.10-slim

WORKDIR /app

RUN pip install psycopg2-binary confluent-kafka

COPY agent.py .
COPY postgres_utils.py .

CMD ["python", "agent.py"]