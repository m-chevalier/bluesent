from confluent_kafka import Producer
import time
import string

import os

KAFKA_OUTPUT_TOPIC = os.getenv('KAFKA_OUTPUT_TOPIC', 'llm-posts')
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')


# Kafka Producer configuration
conf = {
    'bootstrap.servers': f'{KAFKA_BROKER}',  # Adjust with your Kafka broker address
    'client.id': f'alphabet-producer'
}

# Initialize the Kafka Producer
producer = Producer(conf)

# Function to send message to Kafka
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Send each letter of the alphabet to a Kafka topic
topic = f'{KAFKA_OUTPUT_TOPIC}'
for letter in string.ascii_lowercase:  # Loop through 'a' to 'z'
    producer.produce(topic, letter.encode('utf-8'), callback=delivery_report)
    producer.poll(0)  # Poll to trigger delivery report
    time.sleep(1)  # Wait for 1 second

# Wait for any remaining messages to be delivered
producer.flush()