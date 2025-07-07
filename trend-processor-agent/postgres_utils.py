import psycopg2
from psycopg2.extras import execute_batch
import os
from datetime import datetime, timedelta

# Import environment variables for database connection
DATABASE_NAME = os.getenv("DATABASE_NAME", "bluesent")
DATABASE_HOST = os.getenv("DATABASE_HOST", "postgres")
DATABASE_USER = os.getenv("DATABASE_USER", "bluesent-user")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

conn_ = None

def convert_to_timestamp(date_str):
    timestamp = datetime(1970, 1, 1) + timedelta(microseconds=date_str)
    return timestamp

def get_connection():
    global conn_
    if conn_ is None:
        conn_ = psycopg2.connect(database=DATABASE_NAME, host=DATABASE_HOST, user=DATABASE_USER, password=os.getenv("DATABASE_PASSWORD", "password"), port=DATABASE_PORT)
    return conn_

def insert_post(id, content, date, sentiment_analysis):
    conn = get_connection()
    with conn.cursor() as cur:
        
        query_post = """INSERT INTO posts (uuid, content, date) VALUES (%s, %s, %s)"""
        query_dimension = """INSERT INTO sentiment (post_uuid, llm_name, sentiment_name, sentiment_analysis) VALUES (%s, %s, %s, %s)"""

        data = []

        for llm, analysis in sentiment_analysis.items():
            for sentiment in analysis:
                data.append((id, llm, sentiment['sentiment_name'], sentiment['sentiment_analysis']))
        try:
            cur.execute(query_post, (id, content, convert_to_timestamp(date)))
            execute_batch(cur, query_dimension, data)
            conn.commit()
        except Exception as e:
            print(f"Error inserting sentiment data: {e}")
            conn.rollback()
            return
