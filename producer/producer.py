from confluent_kafka import Producer
from prometheus_client import Counter, Histogram, start_http_server
import websockets
import time
import string
import asyncio
import os

messages_processed = Counter('messages_processed_total', 'Total number of messages processed')
messages_deleted = Counter('messages_deleted_total', 'Total number of messages deleted')
process_duration = Histogram('process_duration_ms', 'Duration of message processing in milliseconds')

KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-posts')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')

uri = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

# Kafka Producer configuration
conf = {
    'bootstrap.servers': f'{KAFKA_BROKER}',
    'client.id': f'posts-producer'
}

start_http_server(8000)

# Load allowed words from file
with open('allowed-list.txt', 'r') as f:
    allowed_words = set(f.read().lower().splitlines())

producer = Producer(conf)


# Callback function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        #TODO: better logging
        print(f"Message delivery failed: {err}")
    

async def listen_to_websocket():
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                start = time.time()
                # Check if the message contains at least one allowed word
                if any(word in message.lower() for word in allowed_words):
                    producer.produce(f"{KAFKA_OUTPUT_TOPIC}", message.encode('utf-8'), callback=delivery_report)
                    producer.poll(0)  # Poll to trigger delivery report
                    messages_processed.inc()
                else:
                    messages_deleted.inc()

            except websockets.ConnectionClosed as e:
                print(f"Connection closed: {e}")
                break
            except Exception as e:
                print(f"Error: {e}")
            finally:
                end = time.time()
                process_duration.observe(end - start)


asyncio.get_event_loop().run_until_complete(listen_to_websocket())

# Wait for any remaining messages to be delivered
producer.flush()