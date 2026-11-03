import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from bedrock.bedrock_process import call_bedrock_structured, KeywordResponse
from logs.json_log import log as logger


async def extract_keywords(text: str, cat_file_path: str, top_n: int = 5):
    if not os.path.exists(cat_file_path):
        logger.error("Category file not found", extra={"cat_file_path": cat_file_path, "module": "extract_keywords"})
        return []
    
    all_keywords = set()
    with open(cat_file_path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" not in line:
                continue
            _, kw_str = line.strip().split(":", 1)
            keywords = [kw.strip().lower() for kw in kw_str.split(",") if kw.strip()]
            all_keywords.update(keywords)

    if not all_keywords:
        logger.warn("No candidate keywords found in file", extra={"cat_file_path": cat_file_path, "module": "extract_keywords"})
        return []

    # Pre-filter keywords found in text to reduce prompt size
    text_lower = text.lower()
    candidate_keywords = [kw for kw in all_keywords if kw in text_lower]

    if not candidate_keywords:
        logger.info("No matching keywords found in text via pre-filtering", extra={"module": "extract_keywords"})
        return []

    system_role = "You are a business keyword extraction assistant."
    prompt = f"""
    Extract up to {top_n} relevant keywords from the following text that match the candidate list.
    Candidate list: {candidate_keywords}

    Text: {text}

    Focus on keywords that are related to business impact, revenue, sales, leads, profit, loss, operations, or market insights.
    Only return keywords that are present in the candidate list.
    """

    try:
        result = await call_bedrock_structured(system_role, prompt, KeywordResponse)
    except Exception as e:
        logger.error("Bedrock call failed", extra={"error": str(e), "module": "extract_keywords"}, exc_info=True)
        return []

    keywords = []
    if result and hasattr(result, "keywords"):
        keywords = result.keywords
    elif result and isinstance(result, dict) and "keywords" in result:
        keywords = result["keywords"]

    cleaned_keywords = [kw.strip().lower().strip('"') for kw in keywords]
    keywords = list(dict.fromkeys([kw for kw in cleaned_keywords if kw in all_keywords]))


    if len(keywords) > top_n:
        keywords = keywords[:top_n]

    return keywords
