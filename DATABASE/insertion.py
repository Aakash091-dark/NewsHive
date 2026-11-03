import uuid
import numpy as np
from .getDatabase import wait_for_connection
from DATABASE.INSERT.search_term_table import append_article_id_to_search_term
from logs.json_log import log as logging

def insertUniqueNewsInDB(news, vector_embeddings, article_category, FULL_NEWS, source_type=None):
    print("\n--- Starting insertUniqueNewsInDB ---")
    print(f"Processing URL: {news.get('link')}")
    
    # Ensure vector_embeddings is a list, not a numpy array
    if isinstance(vector_embeddings, np.ndarray):
        vector_embeddings = vector_embeddings.tolist()

    conn = None
    primary_article_id = str(uuid.uuid4())
    article_id = str(uuid.uuid4())
    try:
        print("Attempting to establish database connection...")
        conn = wait_for_connection()
        if not conn:
            print("!!! Database connection failed.")
            logging.error("Database connection could not be established.")
            return False
        print("Database connection successful.")

        with conn:
            with conn.cursor() as cursor:
                conn.autocommit = False

                # ---------------- Check for duplicates in SECOND_TABLE ----------------
                print("Checking for duplicates in SECOND_TABLE...")
                cursor.execute(
                    "SELECT 1 FROM SECOND_TABLE WHERE URL = %s;",
                    (news["link"],)
                )
                if cursor.fetchone():
                    print(f"Duplicate found in SECOND_TABLE for URL: {news['link']}. Halting insertion.")
                    logging.warning(f"URL already exists in SECOND_TABLE: {news['link']}. Halting insertion.")
                    return None
                print("No duplicate found in SECOND_TABLE.")

                # ---------------- PRIMARY_TABLE ----------------
                print("Inserting into PRIMARY_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO PRIMARY_TABLE (
                        PRIMARY_ARTICLE_ID, TITLE, URL, DESCRIPTION, NEWS_SOURCE, PUBLISH_DATE, SOURCE_TYPE
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (URL) DO NOTHING;
                    """,
                    (
                        primary_article_id,
                        news["title"],
                        news["link"],
                        news["description"],
                        news["source"],
                        news["pubDate"],
                        source_type,
                    ),
                )

                if cursor.rowcount == 0:
                    print(f"URL already exists in PRIMARY_TABLE: {news['link']}")
                    logging.warning(f"URL already exists in PRIMARY_TABLE: {news['link']} (continuing inserts anyway)")
                else:
                    print(f"Successfully inserted into PRIMARY_TABLE.")
                    logging.info(f"Inserted unique article {primary_article_id} into PRIMARY_TABLE")

                # ---------------- SECOND_TABLE ----------------
                print("Inserting into SECOND_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO SECOND_TABLE (
                        PRIMARY_ARTICLE_ID, ARTICLE_ID, TITLE, URL, DESCRIPTION,
                        PUBLISH_DATE, ARTICLE_SOURCE, SCRAPED_DATE, SCRAP_VERSION, SOURCE_TYPE
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
                    ON CONFLICT (URL) DO NOTHING;
                    """,
                    (
                        primary_article_id,
                        article_id,
                        news["title"],
                        news["link"],
                        news["description"],
                        news["pubDate"],
                        news["source"],
                        "SNAP-v1",
                        source_type,
                    ),
                )

                if cursor.rowcount == 0:
                    print(f"URL already exists in SECOND_TABLE: {news['link']}")
                    logging.warning(f"URL already exists in SECOND_TABLE: {news['link']} (continuing inserts for other tables)")
                else:
                    print("Successfully inserted into SECOND_TABLE.")
                    logging.info(f"Inserted article {article_id} into SECOND_TABLE")

                # ---------------- VECTORS_TABLE ----------------
                print("Inserting into VECTORS_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO VECTORS_TABLE (ARTICLE_ID, EMBEDDINGS, METADATA)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (METADATA) DO NOTHING;
                    """,
                    (article_id, vector_embeddings, news["link"]),
                )
                print("Successfully inserted into VECTORS_TABLE.")
                logging.info(f"Inserted vector for {article_id} into VECTORS_TABLE")

                # ---------------- FULL_NEWS_TABLE ----------------
                print("Inserting into FULL_NEWS_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO FULL_NEWS_TABLE (ARTICLE_ID, TITLE, FULL_NEWS)
                    VALUES (%s, %s, %s)
                    """,
                    (article_id, news["title"], FULL_NEWS),
                )
                print("Successfully inserted into FULL_NEWS_TABLE.")
                logging.info(f"Inserted full news for {article_id} into FULL_NEWS_TABLE")

                # ---------------- KEYWORDS_TABLE ----------------
                print("Inserting into KEYWORDS_TABLE...")
                keywords = news.get("keywords")
                if keywords:
                    # Ensure keywords are in a list format
                    keywords_list = []
                    if isinstance(keywords, str):
                        # Handle comma-separated strings and single-word strings
                        keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
                    elif isinstance(keywords, list):
                        keywords_list = keywords

                    if keywords_list:
                        cursor.execute(
                            """
                            INSERT INTO KEYWORDS_TABLE (ARTICLE_ID, KEYWORD)
                            VALUES (%s, %s);
                            """,
                            (article_id, keywords_list),
                        )
                        print(f"Successfully inserted keywords into KEYWORDS_TABLE.")
                        logging.info(f"Inserted keywords {keywords_list} for article {article_id} into KEYWORDS_TABLE")
                else:
                    print("No keywords to insert.")

                # ---------------- CATEGORY_TABLE ----------------
                print("Inserting into CATEGORY_TABLE...")
                if not article_category:
                    print("No categories to insert.")
                for cat in article_category:
                    category_id = str(uuid.uuid4())
                    cursor.execute(
                        """
                        INSERT INTO CATEGORY_TABLE (
                            ARTICLE_ID, CATEGORY_ARTICLE_ID, CATEGORY, SUBCATEGORY
                        ) VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                        """,
                        (
                            article_id,
                            category_id,
                            cat.get("category"),
                            cat.get("subcategory"),
                        ),
                    )
                    print(f"Successfully inserted category into CATEGORY_TABLE.")
                    logging.info(f"Inserted category {category_id} for {article_id} into CATEGORY_TABLE")

                print("Committing transaction...")
                conn.commit()
                print("Transaction committed.")

        # ---------------- SEARCH_TERM_TABLE ----------------
        print("Updating SEARCH_TERM_TABLE...")
        search_term = news.get("search_term")
        if search_term:
            append_article_id_to_search_term(search_term, article_id)
            print("Successfully updated SEARCH_TERM_TABLE.")
        else:
            print("No search term to update.")

        print("--- Finished insertUniqueNewsInDB ---")
        return article_id

    except Exception as e:
        print(f"!!! An error occurred: {e}")
        logging.error(f"Error inserting article {primary_article_id}: {e}")
        if conn:
            print("Rolling back transaction...")
            conn.rollback()
            print("Transaction rolled back.")
        return None

    finally:
        if conn:
            conn.close()
            
def insertDuplicateNewsInDB(primary_article_id, news, article_category, vector_embeddings, FULL_NEWS, source_type=None):
    print("\n--- Starting insertDuplicateNewsInDB ---")
    print(f"Processing URL: {news.get('link')}")
    
    # Ensure vector_embeddings is a list, not a numpy array
    if isinstance(vector_embeddings, np.ndarray):
        vector_embeddings = vector_embeddings.tolist()

    conn = None
    article_id = str(uuid.uuid4())
    try:
        print("Attempting to establish database connection...")
        conn = wait_for_connection()
        if not conn:
            print("!!! Database connection failed.")
            logging.error("Database connection could not be established.")
            return False
        print("Database connection successful.")

        with conn:
            with conn.cursor() as cursor:
                # ---------------- Check for duplicates in SECOND_TABLE ----------------
                print("Checking for duplicates in SECOND_TABLE...")
                cursor.execute(
                    "SELECT 1 FROM SECOND_TABLE WHERE URL = %s;",
                    (news["link"],)
                )
                if cursor.fetchone():
                    print(f"Duplicate found in SECOND_TABLE for URL: {news['link']}. Halting insertion.")
                    logging.warning(f"URL already exists in SECOND_TABLE: {news['link']}. Halting insertion.")
                    return None
                print("No duplicate found in SECOND_TABLE.")
                
                # ---------------- SECOND_TABLE ----------------
                print("Inserting into SECOND_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO SECOND_TABLE (
                        PRIMARY_ARTICLE_ID, ARTICLE_ID, TITLE, URL, DESCRIPTION,
                        PUBLISH_DATE, ARTICLE_SOURCE, SCRAPED_DATE, SCRAP_VERSION, SOURCE_TYPE
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
                    ON CONFLICT (URL) DO NOTHING;
                    """,
                    (
                        primary_article_id,
                        article_id,
                        news["title"],
                        news["link"],
                        news["description"],
                        news["pubDate"],
                        news["source"],
                        "SNAP-v1",
                        source_type,
                    ),
                )

                if cursor.rowcount == 0:
                    print(f"URL already exists in SECOND_TABLE: {news['link']}")
                    logging.warning(f"URL already exists in SECOND_TABLE: {news['link']} (continuing with other inserts)")
                else:
                    print("Successfully inserted into SECOND_TABLE.")
                    logging.info(f"Inserted duplicate article {article_id} with primary_article_id {primary_article_id} into SECOND_TABLE")

                # ---------------- VECTORS_TABLE ----------------
                print("Inserting into VECTORS_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO VECTORS_TABLE (ARTICLE_ID, EMBEDDINGS, METADATA)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (METADATA) DO NOTHING;
                    """,
                    (article_id, vector_embeddings, news["link"]),
                )
                print("Successfully inserted into VECTORS_TABLE.")
                logging.info(f"Inserted vector for duplicate article {article_id} into VECTORS_TABLE")

                # ---------------- FULL_NEWS_TABLE ----------------
                print("Inserting into FULL_NEWS_TABLE...")
                cursor.execute(
                    """
                    INSERT INTO FULL_NEWS_TABLE (ARTICLE_ID, TITLE, FULL_NEWS)
                    VALUES (%s, %s, %s)
                    """,
                    (article_id, news["title"], FULL_NEWS),
                )
                print("Successfully inserted into FULL_NEWS_TABLE.")
                logging.info(f"Inserted full news for duplicate article {article_id} into FULL_NEWS_TABLE")

                # ---------------- KEYWORDS_TABLE ----------------
                print("Inserting into KEYWORDS_TABLE...")
                keywords = news.get("keywords")
                if keywords:
                    # Ensure keywords are in a list format
                    keywords_list = []
                    if isinstance(keywords, str):
                        # Handle comma-separated strings and single-word strings
                        keywords_list = [k.strip() for k in keywords.split(',') if k.strip()]
                    elif isinstance(keywords, list):
                        keywords_list = keywords

                    if keywords_list:
                        cursor.execute(
                            """
                            INSERT INTO KEYWORDS_TABLE (ARTICLE_ID, KEYWORD)
                            VALUES (%s, %s);
                            """,
                            (article_id, keywords_list),
                        )
                        print("Successfully inserted keywords into KEYWORDS_TABLE.")
                        logging.info(f"Inserted keywords {keywords_list} for duplicate article {article_id} into KEYWORDS_TABLE")
                else:
                    print("No keywords to insert.")

                # ---------------- CATEGORY_TABLE ----------------
                print("Inserting into CATEGORY_TABLE...")
                if not article_category:
                    print("No categories to insert.")
                for cat in article_category:
                    category_id = str(uuid.uuid4())
                    cursor.execute(
                        """
                        INSERT INTO CATEGORY_TABLE (ARTICLE_ID, CATEGORY_ARTICLE_ID, CATEGORY, SUBCATEGORY)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT DO NOTHING;
                        """,
                        (
                            article_id,
                            category_id,
                            cat.get("category"),
                            cat.get("subcategory"),
                        ),
                    )
                    print("Successfully inserted category into CATEGORY_TABLE.")
                    logging.info(f"Inserted category {category_id} for duplicate article {article_id} into CATEGORY_TABLE")

                print("Committing transaction...")
                conn.commit()
                print("Transaction committed.")

        # ---------------- SEARCH_TERM_TABLE ----------------
        print("Updating SEARCH_TERM_TABLE...")
        search_term = news.get("search_term")
        if search_term:
            append_article_id_to_search_term(search_term, article_id)
            print("Successfully updated SEARCH_TERM_TABLE.")
        else:
            print("No search term to update.")

        print("--- Finished insertDuplicateNewsInDB ---")
        return article_id

    except Exception as e:
        print(f"!!! An error occurred: {e}")
        logging.error(f"Error inserting duplicate article {article_id}: {e}")
        if conn:
            print("Rolling back transaction...")
            conn.rollback()
            print("Transaction rolled back.")
        return None

    finally:
        if conn:
            conn.close()
