import json
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class DataLoader:
    """
    A class to load data from a JSON file into a MongoDB database and
    retrieve data as a pandas DataFrame.
    """
    def __init__(self, db_uri="mongodb://localhost:27017/", db_name="mydatabase"):
        """
        Initializes the DataLoader with the MongoDB connection details.

        :param db_uri: The MongoDB connection string.
        :param db_name: The name of the database to use.
        """
        self.client = MongoClient(db_uri)
        self.db_name = db_name
        self.db = self.client[self.db_name]
        self.check_connection()

    def check_connection(self):
        """Checks if the connection to MongoDB is successful."""
        try:
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            print("MongoDB connection successful.")
        except ConnectionFailure:
            print("MongoDB connection failed.")
            raise

    def write_json_to_mongodb(self, file_path, collection_name):
        """
        Loads data from a JSON file into a specified MongoDB collection.

        :param file_path: The path to the JSON file.
        :param collection_name: The name of the collection to load data into.
        """
        collection = self.db[collection_name]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                if data:
                    collection.insert_many(data)
                    print(f"Successfully inserted {len(data)} documents into '{collection_name}'.")
                else:
                    print("JSON file is empty. No data inserted.")
            else:
                print("JSON file content is not a list. No data inserted.")

        except FileNotFoundError:
            print(f"Error: The file at {file_path} was not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from the file at {file_path}.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_data_as_dataframe(self, collection_name):
        """
        Retrieves data from a specified MongoDB collection and returns it as a pandas DataFrame.

        :param collection_name: The name of the collection to retrieve data from.
        :return: A pandas DataFrame containing the data, or an empty DataFrame on error.
        """
        collection = self.db[collection_name]
        try:
            cursor = collection.find()
            df = pd.DataFrame(list(cursor))
            print(f"Successfully retrieved {len(df)} documents from '{collection_name}' and created a DataFrame.")
            
            # MongoDB adds an '_id' column, which you might not need for training.
            # You can uncomment the following line to drop it.
            # df = df.drop('_id', axis=1, errors='ignore')

            return df
        except Exception as e:
            print(f"An error occurred while retrieving data from MongoDB: {e}")
            return pd.DataFrame()

    def close_connection(self):
        """Closes the MongoDB connection."""
        self.client.close()
        print("MongoDB connection closed.")

if __name__ == "__main__":
    loader = DataLoader(db_name="bluesent_training")
    loader.write_json_to_mongodb("scraped_bluesky_nonllm_posts.json", "random_posts")
    df = loader.get_data_as_dataframe("random_posts")
    print(df.head())
    loader.close_connection()