import logging
from ..getDatabase import wait_for_connection
from logs.json_log import log as logging

def insert_keywords(article_id, keywords):
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            logging.error("Database connection could not be established.")
            return False

        with conn.cursor() as cursor:
            if isinstance(keywords, str):
                keywords_list = [k.strip() for k in keywords.split(',')]
            else:
                keywords_list = keywords

            for keyword in keywords_list:
                cleaned_keyword = keyword.strip().lower().strip('"')
                if cleaned_keyword:
                    cursor.execute(
                        """
                        INSERT INTO KEYWORDS_TABLE (ARTICLE_ID, KEYWORD)
                        VALUES (%s, %s);
                        """,
                        (article_id, cleaned_keyword),
                    )
        conn.commit()
        return True

    except Exception as e:
        logging.error(f"Failed to insert keywords for article_id: {article_id}. Error: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()
