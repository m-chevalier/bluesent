from confluent_kafka import Producer
from prometheus_client import Counter, Histogram, start_http_server
import websockets
import time
import logging
import asyncio
import os
import json
import re
from translation import translate_to_english_from_lang, download_packages, detect_language_fasttext
from utils import generate_uuid_from_string

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

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
        logging.error(f"Message delivery failed: {err}")
    
def check_post(post):
    """
    Validates a post object and extracts the "text" field if the post meets specific criteria.

    Args:
        post (dict): A dictionary representing the post. Expected keys include:
            - "kind" (str): Should be "commit".
            - "commit" (dict): Should contain:
                - "operation" (str): Should be "create".
                - "record" (dict): Should contain the "text" field.

    Returns:
        str or bool: The "text" field from the "record" if the post is valid, otherwise False.

    Edge Cases:
        - Returns False if any of the expected keys are missing or have unexpected values.
        - Assumes the "text" field in "record" is optional and may return None if it is absent.
    """
    if post.get("kind") != "commit":
        return False
    
    commit = post.get("commit")
    if not commit or commit.get("operation") != "create":
        return False
    
    record = commit.get("record")
    if not record:
        return False
    return record.get("text")

def translate_to_english(content):
    content = content.replace("\n", " ")
    lang = detect_language_fasttext(content)
    if lang and lang != "en":
        try:
            content = translate_to_english_from_lang(lang, content)[0]
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return content, lang
    
    return content, lang

def detect_llm(content):
    found_llm = None
    
    for llm in allowed_words:
        pattern = r'(^|\s)' + re.escape(llm.lower()) + r'($|\s)'
        if re.search(pattern, content):
            found_llm = llm
            break
    return found_llm

async def listen_to_websocket():
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                start = time.time()
                message_json = json.loads(message)

                content = check_post(message_json)
                if content:
                    content = content.lower()
                    
                    found_llm = detect_llm(content)
                    if found_llm:
                        translation = translate_to_english(content)     
                        content = translation[0]
                        lang = translation[1]

                        data = {
                            "uuid": generate_uuid_from_string(message_json.get("did")),
                            "did": message_json.get("did"),
                            "llm_name": found_llm,
                            "text": content,
                            "lang": (lang if lang else ""),
                            "date": str(message_json.get("time_us"))
                        }
                        
                        producer.produce(
                            f"{KAFKA_OUTPUT_TOPIC}",
                            json.dumps(data).encode('utf-8'),
                            callback=delivery_report
                        )
                        producer.poll(0)  # Poll to trigger delivery report
                        messages_processed.inc()
                    else:
                        messages_deleted.inc()

            except websockets.ConnectionClosed as e:
                logging.error(f"Connection closed: {e}")
                break
            except Exception as e:
                logging.error(f"Error: {e}")
            finally:
                end = time.time()
                process_duration.observe(end - start)

download_packages()

asyncio.get_event_loop().run_until_complete(listen_to_websocket())

# Wait for any remaining messages to be delivered
producer.flush()