from .getDatabase import wait_for_connection
from logs.json_log import log as logger

def build_DB():
    conn = None
    try:
        conn = wait_for_connection()
        with conn.cursor() as cursor:

            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating extensions: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS PRIMARY_TABLE(
                        PRIMARY_ARTICLE_ID UUID PRIMARY KEY,
                        TITLE TEXT NOT NULL,
                        URL TEXT UNIQUE,
                        DESCRIPTION TEXT,
                        NEWS_SOURCE TEXT,
                        SOURCE_TYPE TEXT,
                        PUBLISH_DATE DATE
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating PRIMARY_TABLE: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS SECOND_TABLE (
                        PRIMARY_ARTICLE_ID UUID,
                        ARTICLE_ID UUID PRIMARY KEY,
                        TITLE TEXT NOT NULL,
                        URL TEXT UNIQUE,
                        DESCRIPTION TEXT,
                        PUBLISH_DATE DATE,
                        ARTICLE_SOURCE TEXT,
                        SOURCE_TYPE TEXT,
                        SCRAPED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        SCRAP_VERSION TEXT
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating SECOND_TABLE: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS VECTORS_TABLE (
                        ARTICLE_ID UUID PRIMARY KEY,
                        EMBEDDINGS VECTOR(768) NOT NULL,
                        METADATA TEXT UNIQUE NOT NULL
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating VECTORS_TABLE: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS CATEGORY_TABLE (
                        ARTICLE_ID UUID NOT NULL,
                        CATEGORY_ARTICLE_ID UUID PRIMARY KEY NOT NULL,
                        CATEGORY TEXT NOT NULL,
                        SUBCATEGORY TEXT NOT NULL
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating CATEGORY_TABLE: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS FULL_NEWS_TABLE (
                        ARTICLE_ID UUID PRIMARY KEY,
                        TITLE TEXT NOT NULL,
                        FULL_NEWS TEXT NOT NULL
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating FULL_NEWS_TABLE: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS KEYWORDS_TABLE (
                    ARTICLE_ID UUID NOT NULL,
                    KEYWORD TEXT[] NOT NULL
                );

                    """
                )
                conn.commit()
            except Exception as e:
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS search_term_table (
                        sid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                        user_id TEXT,
                        search_term TEXT UNIQUE NOT NULL,
                        article_id UUID[]
                    );
                    """
                )
                conn.commit()

            except Exception as e:
                logger.error(
                    f"Error creating search_term_table: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS news_scraped_data (
                        id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                        search_term TEXT,
                        raw_data TEXT,
                        url TEXT,
                        scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        article_id UUID
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating news_scraped_data: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

            try:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scraping_reports (
                        report_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
                        source_identifier TEXT,
                        source_type TEXT,
                        total_links_found INT,
                        total_links_scraped INT,
                        scraped_url TEXT[],
                        total_duplicate_links INT,
                        duplicate_url TEXT[],
                        total_links_failed INT,
                        reason JSONB,
                        processing_time FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                conn.commit()
            except Exception as e:
                logger.error(
                    f"Error creating scraping_reports: {e}",
                    extra={"module": "DATABASE.create", "function": "build_DB"},
                )
                conn.rollback()

    except Exception as e:
        logger.critical(
            f"Error connecting to database: {e}",
            extra={"module": "DATABASE.create", "function": "build_DB"},
        )

    finally:
        if conn:
            conn.close()
            
if __name__ == "__main__":
    build_DB()
