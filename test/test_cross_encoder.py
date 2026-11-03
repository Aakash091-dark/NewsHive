from sentence_transformers import CrossEncoder

def test_cross_encoder():
    print("Loading CrossEncoder model...")
    # Using a general purpose semantic similarity cross-encoder
    model = CrossEncoder('cross-encoder/stsb-distilroberta-base') 

    # 1. Similar Articles
    text_s1 = "Apple launches iPhone 15 featuring a new USB-C charging port."
    text_s2 = "The new iPhone 15 from Apple comes with a USB-C connector replacing Lightning."
    
    # 2. Somewhat Similar Articles
    text_ss1 = "Google releases new Pixel 8 with AI capabilities."
    text_ss2 = "Samsung unveils Galaxy S24 Ultra with advanced camera features."
    
    # 3. Lookalike Articles
    text_l1 = "The river bank was flooded after heavy rains."
    text_l2 = "The bank robbery took place on Main Street yesterday."

    pairs = [
        (text_s1, text_s2),
        (text_ss1, text_ss2),
        (text_l1, text_l2),
        (text_s1, text_l1) # Unrelated
    ]

    print("\n--- Cross-Encoder Similarity Test Results ---")
    scores = model.predict(pairs)

    print(f"\n1. Similar Articles:\n   Score: {scores[0]:.4f}")
    print(f"   Expected: High (e.g. > 0.6)")

    print(f"\n2. Somewhat Similar Articles:\n   Score: {scores[1]:.4f}")
    print(f"   Expected: Medium/Low depending on task")

    print(f"\n3. Lookalike Articles:\n   Score: {scores[2]:.4f}")
    print(f"   Expected: Very Low (should be much lower than Similar)")

    print(f"\n4. Unrelated Articles:\n   Score: {scores[3]:.4f}")

if __name__ == "__main__":
    test_cross_encoder()
