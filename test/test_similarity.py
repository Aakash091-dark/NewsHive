import sys
import os
import numpy as np

# Add current directory to path
sys.path.append(os.getcwd())

from processing.embedding_similarity import NOMIC_EMBEDDINGS, cosine_similarity

def test_similarity():
    print("Initializing NOMIC_EMBEDDINGS...")
    embedder = NOMIC_EMBEDDINGS()

    # 1. Similar Articles (Same event, different wording)
    text_s1 = "Apple launches iPhone 15 featuring a new USB-C charging port."
    text_s2 = "The new iPhone 15 from Apple comes with a USB-C connector replacing Lightning."
    
    # 2. Somewhat Similar Articles (Related topic, different specifics)
    text_ss1 = "Google releases new Pixel 8 with AI capabilities."
    text_ss2 = "Samsung unveils Galaxy S24 Ultra with advanced camera features."
    
    # 3. Lookalike Articles (High lexical overlap or structure, different meaning/context)
    # Using the "bank" polysemy example as "lookalike" in terms of word usage but different context
    text_l1 = "The river bank was flooded after heavy rains."
    text_l2 = "The bank robbery took place on Main Street yesterday."

    texts = [text_s1, text_s2, text_ss1, text_ss2, text_l1, text_l2]
    
    print("Generating embeddings...")
    # The embed_text method now internally adds 'search_document: ' prefix
    embeddings = embedder.embed_text(texts)
    
    vec_s1 = embeddings[0]
    vec_s2 = embeddings[1]
    
    vec_ss1 = embeddings[2]
    vec_ss2 = embeddings[3]
    
    vec_l1 = embeddings[4]
    vec_l2 = embeddings[5]

    print("\n--- Cosine Similarity Test Results ---")

    score_s = cosine_similarity(vec_s1, vec_s2)
    print(f"\n1. Similar Articles:\n   A: '{text_s1}'\n   B: '{text_s2}'\n   Score: {score_s:.4f}")
    print(f"   Expected: High (> 0.8)")

    score_ss = cosine_similarity(vec_ss1, vec_ss2)
    print(f"\n2. Somewhat Similar Articles:\n   A: '{text_ss1}'\n   B: '{text_ss2}'\n   Score: {score_ss:.4f}")
    print(f"   Expected: Medium (0.5 - 0.7)")

    score_l = cosine_similarity(vec_l1, vec_l2)
    print(f"\n3. Lookalike/Different Articles:\n   A: '{text_l1}'\n   B: '{text_l2}'\n   Score: {score_l:.4f}")
    print(f"   Expected: Low (< 0.5)")
    
    # Additional Check: Totally Unrelated
    score_u = cosine_similarity(vec_s1, vec_l1)
    print(f"\n4. Unrelated (iPhone vs River Bank):\n   Score: {score_u:.4f}")

if __name__ == "__main__":
    test_similarity()
