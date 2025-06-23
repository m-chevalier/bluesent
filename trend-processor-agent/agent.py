
from confluent_kafka import Consumer
import json
import os
import logging
from postgres_utils import insert_post

KAKFA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
TOPIC_NAME = os.getenv('TOPIC_NAME', 'llm-posts')

conf = {
    'bootstrap.servers': f'{KAKFA_BROKER}',
    'group.id': 'trend-processor-agent-group',
    'auto.offset.reset': 'earliest'
}

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
        
        print(f"Received message: {msg.value()}")
        post = json.loads(msg.value().decode('utf-8'))
        
        headers = {}
        if msg.headers():
            for key, value in msg.headers():
                headers[key] = value.decode('utf-8') if value else None
        
        sentiments = post.get('sentiments', {})
        id = post.get('did', None)
        content = post.get('text', None)
        date = post.get('time', None)

        if not id or not content or not date:
            logging.error("Missing required fields in the post data")
            continue

        insert_post(id, content, date, sentiments)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()