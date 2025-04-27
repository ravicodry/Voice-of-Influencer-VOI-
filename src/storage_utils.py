import os
import json
import psycopg2
from psycopg2 import sql

DATABASE_URL = os.environ.get('DATABASE_URL') # Get connection string from environment variable

def create_table_if_not_exists():
    """Creates the product_reviews table if it doesn't exist."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_reviews (
                video_url TEXT,
                video_title TEXT,
                start_time FLOAT,
                end_time FLOAT,
                text TEXT,
                sentiment TEXT,
                keywords JSON,
                good_aspect JSON,
                bad_aspect JSON,
                product_name TEXT
            )
        """)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while creating table: {error}")
    finally:
        if conn:
            conn.close()

def save_segment_product_analysis(analyzed_segments):
    """Saves the analyzed segments to the PostgreSQL database."""
    create_table_if_not_exists()
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for segment in analyzed_segments:
            query = sql.SQL("""
                INSERT INTO product_reviews (video_url, video_title, start_time, end_time, text, sentiment, keywords, good_aspect, bad_aspect, product_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
            cur.execute(query, (
                segment['video_url'],
                segment['video_title'],
                segment['start_time'],
                segment['end_time'],
                segment['text'],
                segment['sentiment'],
                json.dumps(segment['keywords']),
                json.dumps(segment['good_aspect']),
                json.dumps(segment['bad_aspect']),
                segment['product_name']
            ))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while saving to database: {error}")
    finally:
        if conn:
            conn.close()

def load_segment_product_analysis():
    """Loads the analyzed segments from the PostgreSQL database."""
    conn = None
    results = []
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT * FROM product_reviews")
        rows = cur.fetchall()
        for row in rows:
            results.append({
                'video_url': row[0],
                'video_title': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'text': row[4],
                'sentiment': row[5],
                'keywords': json.loads(row[6]),
                'good_aspect': json.loads(row[7]),
                'bad_aspect': json.loads(row[8]),
                'product_name': row[9]
            })
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while loading from database: {error}")
    finally:
        if conn:
            conn.close()
    return results

if __name__ == '__main__':
    pass