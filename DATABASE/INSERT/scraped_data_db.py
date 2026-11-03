from ..getDatabase import wait_for_connection
from logs.json_log import log as logger

def insert_scraped_data(search_term, raw_data, url, article_id):
    conn = None
    try:
        conn = wait_for_connection()
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO news_scraped_data (search_term, raw_data, url, article_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (search_term, raw_data, url, article_id)
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error inserting into news_scraped_data: {e}",
                    extra={"module": "DATABASE.INSERT.scraped_data_db", "function": "insert_scraped_data"},
                )
                conn.rollback()
    except Exception as e:
        logger.critical(
            f"Error connecting to database: {e}",
            extra={"module": "DATABASE.INSERT.scraped_data_db", "function": "insert_scraped_data"},
        )
    finally:
        if conn:
            conn.close()
