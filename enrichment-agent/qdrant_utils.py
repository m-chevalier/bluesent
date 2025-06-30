from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

COLLECTION_NAME = "llm-posts"

def init_qdrant(client):

    if not client.collection_exists(collection_name=f"{COLLECTION_NAME}"):  
        client.create_collection(
        collection_name=f"{COLLECTION_NAME}",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def insert_data(client, data, uuid, payload):
    client.upsert(
        collection_name=f"{COLLECTION_NAME}",
        points=[
            PointStruct(
                id=uuid,
                vector=data.tolist(),
                payload=payload
            )
        ]
    )