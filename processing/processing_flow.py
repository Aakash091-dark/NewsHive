import re
from bs4 import BeautifulSoup
from bedrock.summary import get_summary
from bedrock.keyword_extractor import extract_keywords
from bedrock.news_classifier import classify_news
from config.taxonomy_parser import parse_taxonomy
from processing.embedding_similarity import get_gte_embedder, check_bi_encoder_similarity
from DATABASE.insertion import insertUniqueNewsInDB, insertDuplicateNewsInDB
from DATABASE.INSERT.scraped_data_db import insert_scraped_data
from DATABASE.fetch import get_all_rss_embeddings

def clean_content(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

async def process_scraped_data(scraped_data):
    print("\n--- Starting process_scraped_data ---")
    print(f"Processing URL: {scraped_data.get('url')}")

    if not scraped_data.get("pubDate"):
        print(f"Skipping article: {scraped_data.get('url')} due to missing pubDate")
        return

    # 1. Clean the scraped content
    print("Cleaning scraped content...")
    cleaned_content = clean_content(scraped_data.get("raw_content"))
    if not cleaned_content:
        print("!!! No content after cleaning. Skipping.")
        return
    print("Content cleaned successfully.")

    # 2. Bedrock Processing
    print("Starting Bedrock processing...")
    summary = await get_summary(cleaned_content)
    print(f"Summary generated: {summary}")
    
    # Use title + summary for keyword extraction as per requirement
    extraction_text = f"{scraped_data.get('title', '')} {summary}"
    keywords = await extract_keywords(extraction_text, 'config/cat.txt')
    print(f"Keywords extracted: {keywords}")
    taxonomy = parse_taxonomy('config/cat.txt')
    classified_cat, classified_subcat = await classify_news(cleaned_content, taxonomy)
    category = [{"category": classified_cat, "subcategory": classified_subcat}]
    print(f"Category classified: {category}")
    print("Bedrock processing complete.")

    # Prepare data for insertion
    news_item = {
        "title": scraped_data.get("title", ""),
        "link": scraped_data.get("url"),
        "description": summary,
        "source": scraped_data.get("source"),
        "pubDate": scraped_data.get("pubDate"),
        "keywords": keywords,
        "search_term": scraped_data.get("search_term")
    }

    # 3. Similarity Check
    print("Starting similarity check...")
    embedder = get_gte_embedder()
    # Use title + description for embedding as per requirement
    combined_text = f"{news_item['title']} {news_item['description']}"
    current_embedding = embedder.embed_text([combined_text])[0]
    
    all_embeddings = get_all_rss_embeddings()
    candidate_ids = [item['article_id'] for item in all_embeddings]
    
    similar_id, somewhat_similar_id = check_bi_encoder_similarity(
        combined_text,
        candidate_ids
    )
    print(f"Similarity check complete. Similar ID: {similar_id}, Somewhat similar ID: {somewhat_similar_id}")

    # 4. Conditional Database Insertion
    print("Performing conditional database insertion...")
    source_type = scraped_data.get("source_type")
    article_id = None
    
    if similar_id:
        # Found a similar article, insert as a duplicate
        print(f"Found similar article with ID: {similar_id}. Inserting as duplicate.")
        article_id = insertDuplicateNewsInDB(similar_id, news_item, category, current_embedding, cleaned_content, source_type)
    elif somewhat_similar_id:
        # Found a somewhat similar article, also insert as a duplicate
        print(f"Found somewhat similar article with ID: {somewhat_similar_id}. Inserting as duplicate.")
        article_id = insertDuplicateNewsInDB(somewhat_similar_id, news_item, category, current_embedding, cleaned_content, source_type)
    else:
        # No similar article found, insert as unique
        print("No similar article found. Inserting as unique.")
        article_id = insertUniqueNewsInDB(news_item, current_embedding, category, cleaned_content, source_type)

    # 5. Insert Raw Scraped Data
    if article_id:
        print(f"Inserting raw scraped data for article ID: {article_id}")
        insert_scraped_data(
            search_term=scraped_data.get("search_term"),
            raw_data=scraped_data.get("raw_content"),
            url=scraped_data.get("url"),
            article_id=article_id
        )
        print("Raw scraped data inserted successfully.")
    else:
        print("Skipping raw data insertion because article_id was not returned (possibly duplicate or error).")

    print("--- Finished process_scraped_data ---")
