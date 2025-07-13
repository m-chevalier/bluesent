import asyncio
import json
import logging
import os
import signal
import aiohttp
import cbor2
from langdetect import detect, LangDetectException
from langdetect.detector_factory import DetectorFactory
from websockets.exceptions import ConnectionClosedError
import websockets
from confluent_kafka import Producer

from utils import generate_uuid_from_string

# -------- Configuration ---------
DetectorFactory.seed = 0

KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-posts')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')

URI = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

MIN_POST_LENGTH = 20
LLM_CLASSIFIER_API_URL = 'http://post-filter:8002/classify'


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        logging.error(f'Message delivery failed: {err}')
    else:
        logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')


# -------- Producer ---------

class BlueskyProducer:
    def __init__(self, bluesky_uri=URI, kafka_broker=KAFKA_BROKER, kafka_output_topic=KAFKA_OUTPUT_TOPIC):
        self.bluesky_uri = bluesky_uri
        self.kafka_broker = kafka_broker
        self.kafka_output_topic = kafka_output_topic
        self.shutdown_event = asyncio.Event()

        kafka_conf = {
            'bootstrap.servers': self.kafka_broker,
            'client.id': 'posts-producer'
        }

        self.conf = kafka_conf

        self.producer = Producer(self.conf)
        logging.info("Kafka broker initialized. Broker: %s", self.kafka_broker)

    async def _connect_and_listen(self, session: aiohttp.ClientSession):
        """Connects to the Bluesky Firehose and listens for messages."""
        logging.info(f"Attempting to connect to Bluesky Firehose at {self.bluesky_uri}...")

        async with websockets.connect(self.bluesky_uri) as websocket:

            logging.info("Successfully connected to Bluesky Firehose.")

            async for message in websocket:
                await self._process_message(message, session)

    async def _get_prediction(self, session: aiohttp.ClientSession, text: str) -> str | None:

        try:
            payload = {"text": text}
            async with session.post(LLM_CLASSIFIER_API_URL, json=payload, timeout=5) as response:
                if response.status == 200:
                    result = await response.json()
                    label = result.get('label')
                    score = result.get('score')

                    logging.debug(f'Post classified as: {label} with score: {score}')
                    return label
                else:
                    logging.error(f"Failed to classify post. Status code: {response.status}")

                return None
        except asyncio.TimeoutError:
            logging.error("Request timed out.")
        except aiohttp.ClientError as e:
            logging.error(f"An error occurred while making the request: {e}")

        return None


    async def _process_message(self, message: str | bytes, session: aiohttp.ClientSession) -> None:
        try:
            message_json = json.loads(message)
        except json.JSONDecodeError:
            logging.warning("Failed to decode JSON message.")
            return

        if message_json.get('kind') != 'commit':
            return

        commit = message_json.get('commit')
        if not commit or commit.get('operation') != 'create':
            return

        record = commit.get('record')
        if not record:
            return

        content = record.get('text', '').strip()
        if not content:
            return
        else:
            content = content.lower()

        if len(content) < MIN_POST_LENGTH:
            logging.debug(f"Post dropped: too short ({len(content)} chars).")
            return

        try:
            lang = detect(content)
            if lang != 'en':
                logging.debug(f"Post dropped: not English (detected: {lang}).")
                return
        except LangDetectException:
            logging.debug("Post dropped: language could not be detected.")
            return

        found_llm = await self._get_prediction(session, content)
        if not found_llm:
            logging.debug("Post dropped: LLM classification failed.")
            return

        data = {
            "uuid": generate_uuid_from_string(message_json.get("did")),
            "did": message_json.get("did"),
            "llm_name": found_llm,
            "text": content,
            "lang": lang,
            "date": str(message_json.get("time_us"))
        }

        self.producer.produce(
            self.kafka_output_topic,
            key=data["uuid"],
            value=json.dumps(data).encode('utf-8'),
            callback=delivery_report
        )
        self.producer.poll(0)

        logging.info(f"Post from {data['did']} about '{found_llm}' sent to Kafka.")


    def _setup_signal_handlers(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.shutdown_event.set)


    async def _run_async(self):
        """Manages the async resources (like aiohttp session) and the main loop."""
        async with aiohttp.ClientSession() as session:
            while not self.shutdown_event.is_set():
                try:
                    # Use asyncio.wait to handle the shutdown signal while listening
                    listen_task = asyncio.create_task(self._connect_and_listen(session))
                    shutdown_task = asyncio.create_task(self.shutdown_event.wait())
                    await asyncio.wait(
                        [listen_task, shutdown_task],
                            return_when=asyncio.FIRST_COMPLETED
                        )

                    if not listen_task.done():
                        listen_task.cancel() # Cancel the listener if it's still running

                except ConnectionClosedError as e:
                    logging.warning(f"Connection closed: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)
                except Exception as e:
                    logging.error(f"An error occurred: {e}. Reconnecting in 5s...")
                    await asyncio.sleep(5)


    def run(self):
        """The main entry point. Runs the producer in a loop with reconnection logic."""
        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            logging.info("Producer shutting down...")
        finally:
            logging.info("Flushing final Kafka messages...")
            self.producer.flush()

if __name__ == "__main__":
    producer_instance = BlueskyProducer()
    try:
        producer_instance.run()
    except KeyboardInterrupt:
        logging.info("Producer stopped by user.")