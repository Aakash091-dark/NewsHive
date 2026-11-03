from ..getDatabase import wait_for_connection
from typing import List

def insert_search_term(user_ids: List[str], search_term: str, article_ids: List[str]) -> bool:
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:

            return False

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO search_term_table (user_id, search_term, article_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (search_term) DO NOTHING;
                """,
                (user_ids, search_term, article_ids)
            )
        conn.commit()

        return True

    except Exception as e:

        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def insert_search_term_for_article(search_term: str, article_id: str) -> bool:
    if not search_term or not article_id:
        return False
    return append_article_id_to_search_term(search_term, article_id)


def append_article_id_to_search_term(search_term: str, article_id: str) -> bool:
    conn = None
    try:
        conn = wait_for_connection()
        if not conn:
            return False

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO search_term_table (search_term, article_id)
                VALUES (%s, ARRAY[%s]::uuid[])
                ON CONFLICT (search_term) DO UPDATE
                SET article_id =
                    CASE
                        WHEN search_term_table.article_id IS NULL THEN EXCLUDED.article_id
                        WHEN NOT (search_term_table.article_id @> EXCLUDED.article_id) THEN array_cat(search_term_table.article_id, EXCLUDED.article_id)
                        ELSE search_term_table.article_id
                    END;
                """,
                (search_term, article_id)
            )

        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
