from sentence_transformers import SentenceTransformer
from confluent_kafka import Consumer, Producer
from qdrant_client import QdrantClient
from qdrant_utils import init_qdrant, insert_data, generate_uuid_from_string
import json
from agentgemini import get_analysis
import logging

import os
QDRANT_HOST = os.getenv('QDRANT_HOST', 'http://qdrant:6333')
KAKFA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = os.getenv('TOPIC_NAME', 'llm-posts')
KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-embeddings-enriched')


conf = {
    'bootstrap.servers': f'{KAKFA_BROKER}',
    'group.id': 'enrichment-agent-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe([f'{TOPIC_NAME}'])

producer = Producer(conf)

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
client = QdrantClient(url=f"{QDRANT_HOST}")

init_qdrant(client) # Initialize Qdrant collection if it doesn't exist

def get_text(post):
    if post.get("kind") != "commit":
        return None
    
    commit = post.get("commit")
    if not commit or commit.get("operation") != "create":
        return None
    
    record = commit.get("record")
    if not record:
        return None
        
    return record.get("text")

def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed: {err}")

try:

    while True:
        msg = consumer.poll(1.0)  # Waits 1 second
        if msg is None:
            print("No message received in this poll cycle")
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue
        
        print(f"Received message: {msg.value()}")
        post = json.loads(msg.value().decode('utf-8'))
        
        headers = {}
        if msg.headers():
            for key, value in msg.headers():
                headers[key] = value.decode('utf-8') if value else None
        
        translated_message = headers["translated_message"]

        embeddings = model.encode(translated_message)
        did = post.get("did")
        time_us = post.get("time_us")
        lang = headers["lang"]
        
        payload = {
            "did": did,
            "time_us": time_us,
            "text": translated_message,
            "lang": lang
        }
        insert_data(client, embeddings, did, payload)

        # Compute sentiments

        sentiments = get_analysis(translated_message)
        if sentiments is None:
            continue
        data = {
            "did": generate_uuid_from_string(did),
            "text": translated_message,
            "time": time_us,
            "sentiments": sentiments
        }

        data = json.dumps(data)

        producer.produce(
            f"{KAFKA_OUTPUT_TOPIC}",
            data.encode('utf-8'),
            headers=headers,
            callback=delivery_report
        )
        producer.poll(0)  # Poll to trigger delivery report
        

except KeyboardInterrupt:
    pass
finally:
    consumer.close()