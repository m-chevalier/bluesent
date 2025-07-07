import os
import pandas as pd
from openai import OpenAI
from pymongo.collection import Collection
from training_producer.data_management.dataloader import DataLoader
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()

# --- Configuration ---
MONGO_DB_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "bluesent_training"
MONGO_COLLECTION_NAME = "posts"
OPENAI_MODEL = "gpt-4.1-mini"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI()


def get_llm_label(post_text: str) -> bool:
    """
    Uses the OpenAI API to determine if a post is about LLMs.
    Returns True if it is, False otherwise.
    """
    if not isinstance(post_text, str) or not post_text.strip():
        return False  # Return False for empty or invalid text

    try:
        reponse = client.responses.create(
            model=OPENAI_MODEL,
            input="You are a text classification model. Given the following text, determine if it is about LLMs. Answer 'yes' or 'no'.\n\n" + post_text
        )
        answer = reponse.output_text.strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"An error occurred with the OpenAI API call: {e}")
        return False  # Default to False on error


def update_database_with_labels(df: pd.DataFrame, collection: Collection):
    """
    Updates the MongoDB collection with the new 'is_llm_related' label from the DataFrame.
    """
    print("Updating database with new labels...")
    update_count = 0
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Generating LLM Labels"):
        # Ensure the document ID and the new label exist for the row
        if '_id' in row and 'is_llm_related' in row:
            collection.update_one(
                {'_id': row['_id']},
                {'$set': {'is_llm_related': row['is_llm_related']}}
            )
            update_count += 1
    print(f"Successfully updated {update_count} documents in the database.")


def main():
    """
    Main script to load data, classify it using OpenAI, and update the database.
    """
    # 1. Load data from MongoDB into a DataFrame
    dataloader = DataLoader(db_uri=MONGO_DB_URI, db_name=MONGO_DB_NAME)
    posts_df = dataloader.get_data_as_dataframe(MONGO_COLLECTION_NAME)

    posts_df = posts_df.head(5000)
    if posts_df.empty:
        print("No data loaded from MongoDB. Exiting.")
        dataloader.close_connection()
        return


    # Filter out posts that already have the 'is_llm_related' label
    unlabeled_df = posts_df[posts_df['is_llm_related'].isnull()].copy()
    
    if unlabeled_df.empty:
        print("No new posts to label. Exiting.")
        dataloader.close_connection()
        return
        
    print(f"Found {len(unlabeled_df)} posts to label.")

    # 2. Extract the text content from each post
    tqdm.pandas(desc="Extracting Post Text")
    unlabeled_df['text'] = unlabeled_df.progress_apply(lambda row: row['text'], axis=1)

    # 3. Run OpenAI API calls to get the labels
    tqdm.pandas(desc="Labeling Posts via OpenAI")
    unlabeled_df['is_llm_related'] = unlabeled_df['text'].progress_apply(get_llm_label)

    # 4. Load the new property to the database
    mongo_collection = dataloader.db[MONGO_COLLECTION_NAME]
    update_database_with_labels(unlabeled_df, mongo_collection)

    # Clean up
    dataloader.close_connection()
    print("Labeling process complete.")


if __name__ == "__main__":
    main()