import { QdrantClient } from '@qdrant/js-client-rest';

// Initialize Qdrant client
export const qdrantClient = new QdrantClient({
  url: process.env.QDRANT_HOST ? `http://${process.env.QDRANT_HOST}:${process.env.QDRANT_PORT || '6333'}` : 'http://localhost:6333',
});

// Example function to create a collection
export async function createCollection(collectionName: string, vectorSize: number) {
  try {
    await qdrantClient.createCollection(collectionName, {
      vectors: {
        size: vectorSize,
        distance: 'Cosine',
      },
    });
    console.log(`Collection ${collectionName} created successfully`);
  } catch (error) {
    console.error('Error creating collection:', error);
  }
}

// Example function to search vectors
export async function searchVectors(collectionName: string, vector: number[], limit: number = 10) {
  try {
    const searchResult = await qdrantClient.search(collectionName, {
      vector,
      limit,
    });
    return searchResult;
  } catch (error) {
    console.error('Error searching vectors:', error);
    return null;
  }
}

// Example function to insert vectors
export async function insertVectors(collectionName: string, points: any[]) {
  try {
    const result = await qdrantClient.upsert(collectionName, {
      wait: true,
      points,
    });
    return result;
  } catch (error) {
    console.error('Error inserting vectors:', error);
    return null;
  }
}
