from confluent_kafka import Consumer
import json

conf = {
    'bootstrap.servers': 'IPOFTHEMACHINE:9092',
    'group.id': 'filter-group',
    'auto.offset.reset': 'earliest'}

consumer = Consumer(conf)
consumer.subscribe([f'llm-posts'])

data = []

try:
    while True:
        msg = consumer.poll(1.0)  # Waits 1 second
        if msg is None:
            print("No message received in this poll cycle")
            continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue        
        
        headers = {}
        if msg.headers():
            for key, value in msg.headers():
                headers[key] = value.decode('utf-8') if value else None        
        translated_message = headers["translated_message"]

        print(f"Received message: {translated_message}")
        isllm = int(input("Is it an LLM post? (1/0)"))
        data.append({
            "translated_message": translated_message,
            "is_llm": isllm
        })
except KeyboardInterrupt:
    # Save data to file on interrupt
    with open('filtered_data.json', 'w+') as f:
        json.dump(data, f, indent=4)
finally:
    consumer.close()