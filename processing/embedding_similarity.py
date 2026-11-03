import numpy as np
from sentence_transformers import SentenceTransformer
import ast
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from DATABASE.fetch import get_articles_text_by_ids

_gte_embedder = None

def get_gte_embedder():
    global _gte_embedder
    if _gte_embedder is None:
        _gte_embedder = GTE_LARGE_EMBEDDINGS()
    return _gte_embedder

class GTE_LARGE_EMBEDDINGS:
    def __init__(self):
        print("DEBUG: Initializing GTE_LARGE_EMBEDDINGS...")
        try:
            self.embed_model = SentenceTransformer(
                "Alibaba-NLP/gte-large-en-v1.5",
                trust_remote_code=True
            )
            print("DEBUG: gte-large-en-v1.5 loaded successfully")
        except Exception as e:
            print(f"DEBUG: Error loading embedding model: {e}")
            raise e

        self.target_dim = 1024

    def embed_text(self, texts: list[str]) -> np.ndarray:
        print(f"DEBUG: embed_text called with {len(texts)} texts")
        if not texts:
            return np.empty((0, self.target_dim), dtype=np.float32)

        try:
            embeddings = self.embed_model.encode(
                texts,
                normalize_embeddings=True
            )
            print("DEBUG: Embeddings generated")
        except Exception as e:
            print(f"DEBUG: Error during embedding: {e}")
            raise e

        return np.array(embeddings, dtype=np.float32)


def check_bi_encoder_similarity(
    news_text,
    candidate_ids,
    similarity_threshold=0.5,
    somewhat_threshold=0.3
):
    """
    Checks similarity by re-embedding candidate articles.
    candidate_ids: list of article IDs (strings or UUIDs)
    """

    if not candidate_ids:
        return None, None

    print(f"DEBUG: Running Bi-Encoder similarity for {len(candidate_ids)} articles")

    # -------------------------
    # 1. Embed query/news text
    # -------------------------
    embedder = get_gte_embedder()
    query_embedding = embedder.embed_text([news_text])[0]

    # -------------------------------
    # 2. Fetch DB article full texts
    # -------------------------------
    # Ensure IDs are strings
    candidate_ids_str = [str(cid) for cid in candidate_ids]
    candidate_text_map = get_articles_text_by_ids(candidate_ids_str)

    # Prepare texts in same order
    db_texts = []
    valid_ids = []

    for cid in candidate_ids_str:
        if cid in candidate_text_map and candidate_text_map[cid]:
            db_texts.append(candidate_text_map[cid])
            valid_ids.append(cid)

    if not db_texts:
        return None, None

    # ---------------------------------
    # 3. Embed all DB article texts
    # ---------------------------------
    db_embeddings = embedder.embed_text(db_texts)

    # ---------------------------------
    # 4. Dot-product similarity
    # ---------------------------------
    scores = np.dot(db_embeddings, query_embedding)

    # Best score
    best_idx = np.argmax(scores)
    best_score = float(scores[best_idx])
    best_id = valid_ids[best_idx]

    # -----------------------------
    # 5. Apply similarity threshold
    # -----------------------------
    similar_news_id = None
    somewhat_similar_news_id = None

    if best_score >= similarity_threshold:
        similar_news_id = best_id
    elif best_score >= somewhat_threshold:
        somewhat_similar_news_id = best_id

    print(f"DEBUG: Best Match → ID={best_id}, Score={best_score}")

    return similar_news_id, somewhat_similar_news_id
