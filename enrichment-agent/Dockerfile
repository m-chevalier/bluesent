FROM python:3.9-slim

WORKDIR /app

RUN pip install sentence-transformers hf_xet qdrant-client confluent-kafka google-genai

COPY agent.py .
COPY agentgemini.py .
COPY qdrant_utils.py .

CMD ["python", "agent.py"]