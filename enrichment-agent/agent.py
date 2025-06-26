from sentence_transformers import SentenceTransformer
from confluent_kafka import Consumer, Producer
from qdrant_client import QdrantClient
from qdrant_utils import init_qdrant, insert_data
import json
from agentmistral import get_analysis
import logging
from prometheus_client import Counter, Histogram, start_http_server
import os
import time

QDRANT_HOST = os.getenv('QDRANT_HOST', 'http://qdrant:6333')
KAKFA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = os.getenv('TOPIC_NAME', 'llm-posts')
KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-embeddings-enriched')

start_http_server(8000)  # Start Prometheus metrics server

messages_processed = Counter('enrichment_agent_messages_processed_total', 'Total number of messages processed')
messages_rejected = Counter('enrichment_agent_messages_rejected_total', 'Total number of messages rejected by the LLM')
process_duration = Histogram('enrichment_agent_process_duration_ms', 'Duration of message processing in milliseconds')
tokens_consumed = Histogram('enrichment_agent_tokens_consumed_total', 'Total token consumed')

conf = {
    'bootstrap.servers': f'{KAKFA_BROKER}',
    'group.id': 'enrichment-agent-group'
}

consumer = Consumer(conf)
consumer.subscribe([f'{TOPIC_NAME}'])

producer = Producer(conf)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
client = QdrantClient(url=f"{QDRANT_HOST}")

init_qdrant(client) # Initialize Qdrant collection if it doesn't exist

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")

try:

    while True:
        msg = consumer.poll(1.0)  # Waits 1 second
        if msg is None:
            continue
        if msg.error():
            logging.error(f"Error: {msg.error()}")
            continue
        
        messages_processed.inc()
        start = time.time()

        data = json.loads(msg.value().decode('utf-8'))
        
        translated_message = data.get("text")
        did = data.get("did")
        uuid = data.get("uuid")
        date = data.get("date")
        lang = data.get("lang")

        # Generate embedding with MiniLM
        embeddings = model.encode(translated_message)

        # Prepare the payload for Qdrand metadata
        payload_qdrant = {
            "did": did,
            "uuid": uuid,
            "date": date,
            "text": translated_message,
            "lang": lang
        }


        # Compute sentiments with AgentGemini
        sentiments, tokens_count = get_analysis(translated_message)
        if sentiments is None: # If no sentiments are returned, skip this message
            messages_rejected.inc()
            continue

        # Insert in Qdrant
        insert_data(client, embeddings, uuid, payload_qdrant)

        # Prepare the payload for Kafka message
        payload_kafka = {
            "did": did,
            "uuid": uuid,
            "text": translated_message,
            "time": date,
            "sentiments": sentiments
        }
        data = json.dumps(payload_kafka)

        # Produce message to Kafka output topic
        producer.produce(
            f"{KAFKA_OUTPUT_TOPIC}",
            data.encode('utf-8'),
            callback=delivery_report
        )
        producer.poll(0)  # Poll to trigger delivery report
        end = time.time()
        process_duration.observe(end - start)

except KeyboardInterrupt:
    pass
finally:
    consumer.close()