import os
import sys
from typing import Dict, Set, Tuple
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from bedrock.bedrock_process import call_bedrock_structured
from logs.json_log import log as logger
from config.schema import TaxonomyClassificationResponse

async def classify_news(news_text: str, taxonomy: Dict[str, Dict[str, Set[str]]]) -> Tuple[str, str]:
    categories = list(taxonomy.keys())
    categories_str = ", ".join(categories)
    subcategories_str = {cat: ", ".join(subcats.keys()) for cat, subcats in taxonomy.items()}

    system_role = "You are a news classification assistant."

    prompt = f"""
    Classify the following news text into a category and subcategory based on this taxonomy.

    Categories: {categories_str}
    Subcategories (per category): {subcategories_str}

    News text:
    {news_text}

    Return a JSON object like this:
    {{
        "category": "<category name>",
        "subcategory": "<subcategory name>"
    }}
    """

    try:
        result = await call_bedrock_structured(system_role, prompt, TaxonomyClassificationResponse)
    except Exception as e:
        logger.error(
            "Bedrock call failed during classification",
            extra={"error": str(e), "module": "classify_news"},
            exc_info=True
        )
        return "general", "general"

    category = None
    subcategory = None
    if result and hasattr(result, "category") and hasattr(result, "subcategory"):
        category = result.category
        subcategory = result.subcategory
    elif isinstance(result, dict):
        category = result.get("category", "general")
        subcategory = result.get("subcategory", "general")
    else:
        category, subcategory = "general", "general"

    return category, subcategory
