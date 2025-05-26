from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
import uuid
import hashlib

COLLECTION_NAME = "llm-posts"


def generate_uuid_from_string(input_string):
    # Create a SHA-1 hash of the input string
    sha1_hash = hashlib.sha1(input_string.encode('utf-8')).hexdigest()

    # Take the first 32 hex digits (128 bits) from the SHA-1 hash
    # and convert it to a UUID
    uuid_str = sha1_hash[:32]

    # Format string as UUID: 8-4-4-4-12
    formatted_uuid = f'{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:32]}'
    return formatted_uuid

def init_qdrant(client):

    if not client.collection_exists(collection_name=f"{COLLECTION_NAME}"):  
        client.create_collection(
        collection_name=f"{COLLECTION_NAME}",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def insert_data(client, data, id, payload):
    client.upsert(
        collection_name=f"{COLLECTION_NAME}",
        points=[
            PointStruct(
                id=generate_uuid_from_string(id),
                vector=data.tolist(),
                payload=payload
            )
        ]
    )