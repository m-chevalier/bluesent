import asyncio
import json
import os
import signal
import websockets
from confluent_kafka import Producer

# --- Configuration ---

KAFKA_BROKER = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_OUTPUT_TOPIC = os.environ.get('KAFKA_OUTPUT_TOPIC', 'llm_training_data_raw')

BLUESKY_WEBSOCKET_URI = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"
WORDLIST_FILE_PATH = "training_wordlist.txt"

running = True

# --- Kafka Producer Setup ---
kafka_producer = None

def load_wordlist(file_path):
    loaded_list = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line:
                    loaded_list.append(stripped_line.lower())
        print(f"Successfully loaded {len(loaded_list)} keywords from {file_path}")
    except FileNotFoundError:
        print(f"ERROR: Wordlist file not found at {file_path}. No keyword filtering will be applied.")
    except Exception as e:
        print(f"ERROR: Could not read wordlist file {file_path}: {e}")
    return loaded_list

LOOSE_WORDLIST = load_wordlist(WORDLIST_FILE_PATH)

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        pass

try:
    producer_conf = {'bootstrap.servers': KAFKA_BROKER}
    kafka_producer = Producer(producer_conf)
    print(f"Kafka Producer initialized. Broker: {KAFKA_BROKER}")
except Exception as e:
    print(f"Error initializing Kafka Producer: {e}")
    running = False

def post_contains_keyword(post_text_content):
    if not post_text_content or not LOOSE_WORDLIST:
        return False

    text_lower = post_text_content.lower()
    for keyword in LOOSE_WORDLIST:
        if keyword in text_lower:
            return True
    return False

def _extract_post_text(message_json):
    post_text = None
    if isinstance(message_json, dict):
        if 'record' in message_json and isinstance(message_json['record'], dict):
            post_text = message_json['record'].get('text')
        elif 'text' in message_json: # Simpler structure
            post_text = message_json.get('text')
    return post_text

async def _handle_websocket_message(message_str):
    try:
        message_json = json.loads(message_str)
        post_text = _extract_post_text(message_json)

        if post_text and isinstance(post_text, str):
            post_text = post_text.strip()
            if post_contains_keyword(post_text):
                if kafka_producer:
                    kafka_producer.produce(
                        KAFKA_OUTPUT_TOPIC,
                        value=message_str.encode('utf-8'),
                        callback=delivery_report
                    )
                    kafka_producer.poll(0)
                    print(f"Produced message to Kafka topic '{KAFKA_OUTPUT_TOPIC}': {post_text[:100]}")
                else:
                    print("ERROR: Kafka producer not available for message.")
    except json.JSONDecodeError:
        print(f"Failed to decode JSON: {message_str[:100]}")
    except Exception as e:
        print(f"Error handling message: {e}. Message: {message_str[:100]}")

async def _websocket_receive_loop(websocket_connection):
    global running
    while running:
        try:
            message_str = await websocket_connection.recv()
            await _handle_websocket_message(message_str)
        except websockets.ConnectionClosed:
            print("WebSocket connection closed by server during receive.")
            return
        except Exception as e:
            print(f"Error during WebSocket receive or message handling: {e}")
            await asyncio.sleep(1) # Brief pause before trying to receive next message

async def listen_and_produce():
    global running
    while running:
        try:
            print(f"Attempting to connect to WebSocket: {BLUESKY_WEBSOCKET_URI}")
            async with websockets.connect(BLUESKY_WEBSOCKET_URI) as websocket:
                print("Successfully connected to WebSocket.")
                await _websocket_receive_loop(websocket) # Enter the dedicated receive loop
                if not running: # If shutdown was triggered during receive loop
                    break
                # If _websocket_receive_loop exited due to connection closed, this outer loop will retry
                print("WebSocket receive loop ended. Attempting to reconnect if still running...")
        except (websockets.exceptions.ConnectionClosedError, ConnectionRefusedError, OSError) as e:
            if running:
                print(f"WebSocket connection failed: {e}. Retrying in 5 seconds...")
                await asyncio.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred in listen_and_produce main loop: {e}")
            running = False # Stop on unexpected major errors
            break
    print("Exiting listen_and_produce loop.")

def shutdown_handler(signum, frame):
    global running
    print(f"Shutdown signal {signum} received. Exiting gracefully...")
    running = False

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    if kafka_producer is None and running:
        print("Kafka producer was not initialized. Exiting.")
        running = False

    if running:
        print("Starting WebSocket listener and Kafka producer...")
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(listen_and_produce())
        except KeyboardInterrupt:
            print("KeyboardInterrupt caught in main. Shutting down...")
            running = False
        finally:
            print("Cleaning up...")
            if kafka_producer:
                print("Flushing Kafka producer...")
                kafka_producer.flush(timeout=10)
                print("Kafka producer flushed.")
            # Ensure loop is stopped before trying to close, if it's still running
            if loop.is_running():
                loop.stop()
            # loop.close() # Closing the loop might still be tricky depending on task cleanup
            print("Shutdown complete.")
    else:
        print("Script did not start due to initialization errors or immediate shutdown signal.")

