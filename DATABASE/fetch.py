import psycopg2
from .getDatabase import wait_for_connection
import logging

def get_primary_article_id_by_url(url):
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return None

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT PRIMARY_ARTICLE_ID FROM PRIMARY_TABLE WHERE URL = %s",
                (url,),
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return get_primary_article_id_by_url(url)
        else:
            return None
    except Exception as e:
        logging.error(f"Error checking URL in PRIMARY_TABLE: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_scraped_data_by_url(url):
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return None

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT article_id FROM news_scraped_data WHERE URL = %s",
                (url,),
            )
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return get_scraped_data_by_url(url)
        else:
            return None
    except Exception as e:
        logging.error(f"Error checking URL in news_scraped_data: {e}")
        return None
    finally:
        if conn:
            conn.close()

def check_url_in_second_table(url):
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return False

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ARTICLE_ID FROM SECOND_TABLE WHERE URL = %s",
                (url,),
            )
            result = cursor.fetchone()
            return bool(result)

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return check_url_in_second_table(url)
        else:
            return False
    except Exception as e:
        logging.error(f"Error checking URL in SECOND_TABLE: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_rss_embeddings():
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return []

        with conn.cursor() as cursor:
            cursor.execute("SELECT article_id, embeddings FROM VECTORS_TABLE")
            results = cursor.fetchall()
            return [{"article_id": row[0], "embeddings": row[1]} for row in results]

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return get_all_rss_embeddings()
        else:
            return []
    except Exception as e:
        logging.error(f"Error fetching embeddings from VECTORS_TABLE: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_search_terms():
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return []

        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT search_term FROM SEARCH_TERM_TABLE")
            results = cursor.fetchall()
            unique_terms = [row[0] for row in results]
            print(f"Fetched {unique_terms} unique search terms from database.")
            return unique_terms

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return get_all_search_terms()
        else:
            return []
    
    except Exception as e:
        logging.error(f"Error fetching search terms from SEARCH_TERM_TABLE: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_articles_text_by_ids(article_ids):
    if not article_ids:
        return {}
        
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return {}

        with conn.cursor() as cursor:
            # Construct a tuple string for the IN clause
            ids_tuple = tuple(article_ids)
            query = """
                SELECT ARTICLE_ID, TITLE, DESCRIPTION 
                FROM SECOND_TABLE 
                WHERE ARTICLE_ID IN %s
            """
            cursor.execute(query, (ids_tuple,))
            results = cursor.fetchall()
            
            # Combine title and description
            text_map = {}
            for row in results:
                article_id = str(row[0]) # Ensure article_id is string
                title = row[1] if row[1] else ""
                description = row[2] if row[2] else ""
                combined_text = f"{title} {description}".strip()
                text_map[article_id] = combined_text
                
            return text_map

    except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
        logging.error(f"Database connection error: {e}")
        conn = wait_for_connection()
        if conn:
            return get_articles_text_by_ids(article_ids)
        else:
            return {}
    except Exception as e:
        logging.error(f"Error fetching article text by IDs: {e}")
        return {}
    finally:
        if conn:
            conn.close()
