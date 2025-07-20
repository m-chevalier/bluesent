FROM python:3.9-slim

WORKDIR /app

RUN pip install sentence-transformers hf_xet qdrant-client confluent-kafka google-genai pydantic mistralai

COPY agent.py .
COPY agentmistral.py .
COPY qdrant_utils.py .

CMD ["python", "agent.py"]
