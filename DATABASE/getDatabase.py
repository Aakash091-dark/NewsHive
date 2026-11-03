from logs.json_log import log as logger
import psycopg2
import psycopg2.extras  
import time
from psycopg2 import OperationalError, Error
from config .settings import DATABASE_URL, DB_CONN_TIMEOUT, MAX_RETRIES, RETRY_DELAY

def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=DB_CONN_TIMEOUT)
        psycopg2.extras.register_uuid(conn_or_curs=conn)  
        return conn
    except (OperationalError, Error) as e:
        logger.error(
            f"Connection attempt failed: {e}",
            extra={"module": "DATABASE.getDatabase", "function": "get_connection"},
        )
        return None

def wait_for_connection():
    retries = 0
    conn = None

    while retries < MAX_RETRIES:
        conn = get_connection()
        if conn:

            return conn

        retries += 1
        logger.warning(
            f"Retrying in {RETRY_DELAY} sec... ({retries}/{MAX_RETRIES})",
            extra={"module": "DATABASE.getDatabase", "function": "wait_for_connection"},
        )
        time.sleep(RETRY_DELAY)

    logger.critical(
        "Could not connect to the database after multiple retries.",
        extra={"module": "DATABASE.getDatabase", "function": "wait_for_connection"},
    )
    raise ConnectionError(
        "Could not connect to the database after multiple retries."
    )
