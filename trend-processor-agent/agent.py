
from confluent_kafka import Consumer
import json
import os
import logging
from postgres_utils import insert_post

KAKFA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = os.getenv('INPUT_TOPIC', 'llm-embeddings-enriched')

conf = {
    'bootstrap.servers': f'{KAKFA_BROKER}',
    'group.id': 'trend-processor-agent-group'}

consumer = Consumer(conf)
consumer.subscribe([f'{TOPIC_NAME}'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            logging.info("No message received in this poll cycle")
            continue
        if msg.error():
            logging.error(f"Message received with error: {msg.error()}")
            continue
        
        post = json.loads(msg.value().decode('utf-8'))
        
        sentiments = post.get('sentiments', {})
        uuid = post.get('uuid', None)
        content = post.get('text', None)
        date = int(post.get('time', None))

        if not uuid or not content or not date:
            logging.error("Missing required fields in the post data")
            continue
        try:
            insert_post(uuid, content, date, sentiments)
        except Exception as e:
            logging.error(f"Error inserting post into database: {e}")
            pass
except KeyboardInterrupt:
    pass
finally:
    consumer.close()