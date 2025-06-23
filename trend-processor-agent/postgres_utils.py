import psycopg2
from psycopg2.extras import execute_batch
import os

# Import environment variables for database connection
DATABASE_NAME = os.getenv("DATABASE_NAME", "bluesent")
DATABASE_HOST = os.getenv("DATABASE_HOST", "postgres")
DATABASE_USER = os.getenv("DATABASE_USER", "bluesent-user")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

conn_ = None

def get_connection():
    global conn_
    if conn_ is None:
        conn_ = psycopg2.connect(database=DATABASE_NAME, host=DATABASE_HOST, user=DATABASE_USER, password=os.getenv("DATABASE_PASSWORD", "password"), port=DATABASE_PORT)
    return conn_

def insert_post(id, content, date, sentiment_analysis):
    conn = get_connection()
    with conn.cursor() as cur:
        
        query_post = """INSERT INTO posts (uuid, content, date) VALUES (%s, %s, %s)"""
        query_dimension = """INSERT INTO sentiment (post_uuid, sentiment_name, sentiment_analysis) VALUES (%s, %s, %s)"""

        data = []

        cur.execute(query_post, (id, content, date))

        for sentiment in sentiment_analysis:
            data.append((id, sentiment['sentiment_name'], sentiment['sentiment_analysis']))

        execute_batch(cur, query_dimension, data)
        conn.commit()