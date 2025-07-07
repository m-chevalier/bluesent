import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
def connect_to_mongodb_and_load_data(label: str):
    """
    Connects to the MongoDB database, loads the data that has the specified label,
    and returns a DataFrame with the 'text' and label columns.
    :param label: The name of the label column to filter by.
    :return: A pandas DataFrame with 'text' and label columns.
    """
    # --- Configuration ---
    db_uri = "mongodb://localhost:27017/"
    db_name = "bluesent_training"
    collection_name = "posts"
    client = None

    try:
        # Connect to MongoDB
        client = MongoClient(db_uri)
        client.admin.command('ismaster')
        db = client[db_name]
        collection = db[collection_name]

        # Load data with the specified label
        query = {
            label:
                      {"$exists": True,
                       "$ne": None}
                  }
        cursor = collection.find(query)

        # Create a DataFrame from the cursor
        df = pd.DataFrame(list(cursor))

        if df.empty:
            print(f"No documents found with the label '{label}'.")
            return pd.DataFrame()

        # Select the 'text' and label columns
        if 'text' in df.columns and label in df.columns:
            result_df = df[['text', label]]
            print(f"Successfully loaded {len(result_df)} documents with label '{label}'.")
            return result_df
        else:
            missing_cols = []
            if 'text' not in df.columns:
                missing_cols.append('text')
            if label not in df.columns:
                missing_cols.append(label)
            print(f"Columns {missing_cols} not found in the DataFrame.")
            return pd.DataFrame()

    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()
    finally:
        if client:
            client.close()
            print("MongoDB connection closed.")



if __name__ == "__main__":
    label = "is_llm_related"
    df = connect_to_mongodb_and_load_data(label)
    print(df.head())
