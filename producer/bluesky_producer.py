import asyncio
import logging
import os

import websockets
from confluent_kafka import Producer

KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-posts')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')

URI = "wss://jetstream2.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

conf = {
    'bootstrap.servers': f'{KAFKA_BROKER}',
    'client.id': f'posts-producer'
}


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BlueskyProducer:
    def __init__(self, bluesky_uri=URI, kafka_broker=KAFKA_BROKER, kafka_output_topic=KAFKA_OUTPUT_TOPIC, conf=conf):
        self.bluesky_uri = bluesky_uri
        self.kafka_broker = kafka_broker
        self.kafka_output_topic = kafka_output_topic
        self.conf = conf

        self.producer = Producer(self.conf)
        logging.info("Kafka broker initialized. Broker: %s", self.kafka_broker)

    async def _connect_and_listen(self):
        """
        Connects to the Bluesky Firehose and listens for messages.
        """
        logging.info(f"Attempting to connect to Bluesky Firehose at {self.bluesky_uri}...")

        async with websockets.connect(self.bluesky_uri) as ws:
            logging.info(f"Successfully connected to Bluesky Firehose at {self.bluesky_uri}")

            async for message in ws:
                logging.info(f"Received message: {message}")


    def run(self):
        while True:
            try:
                # asyncio.run() starts the async event loop and runs our function
                asyncio.run(self._connect_and_listen())
            except websockets.exceptions.ConnectionClosedError as e:
                logging.warning(f"Connection closed unexpectedly: {e}. Reconnecting in 5 seconds...")
            except Exception as e:
                # Catch other potential exceptions (e.g., network issues)
                logging.error(f"An error occurred: {e}. Reconnecting in 5 seconds...")

            # Wait for a few seconds before trying to reconnect
            asyncio.sleep(5)


if __name__ == "__main__":
    producer_instance = BlueskyProducer()
    try:
        producer_instance.run()
    except KeyboardInterrupt:
        logging.info("Producer stopped by user.")