import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_rss_count_before_date(check_date="2025-11-29"):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT COUNT(*) AS rss_count
            FROM second_table
            WHERE source_type = 'rss'
            AND publish_date > %s;
        """

        cursor.execute(query, (check_date,))
        result = cursor.fetchone()

        print(f"RSS articles before {check_date}: {result['rss_count']}")

        cursor.close()
        conn.close()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    get_rss_count_before_date()
