from DATABASE.getDatabase import wait_for_connection
from logs.json_log import log as logger
import json

def insert_scraping_report(
    source_identifier,
    source_type,
    total_links_found,
    total_links_scraped,
    scraped_urls,
    total_duplicate_links,
    duplicate_urls,
    total_links_failed,
    reason,
    processing_time
):
    conn = None
    try:
        conn = wait_for_connection()
        with conn.cursor() as cursor:
            
            query = """
            INSERT INTO scraping_reports (
                source_identifier,
                source_type,
                total_links_found,
                total_links_scraped,
                scraped_url,
                total_duplicate_links,
                duplicate_url,
                total_links_failed,
                reason,
                processing_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            
            cursor.execute(
                query,
                (
                    source_identifier,
                    source_type,
                    total_links_found,
                    total_links_scraped,
                    scraped_urls,            
                    total_duplicate_links,
                    duplicate_urls,          
                    total_links_failed,
                    json.dumps(reason),      
                    processing_time
                )
            )
            
            conn.commit()
            logger.info("Successfully inserted scraping report.")

    except Exception as e:
        logger.error(
            f"Error inserting scraping report: {e}",
            extra={
                "module": "DATABASE.INSERT.reports",
                "function": "insert_scraping_report"
            },
        )
        if conn:
            conn.rollback()

    finally:
        if conn:
            conn.close()
