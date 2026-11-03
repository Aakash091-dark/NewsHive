from dotenv import load_dotenv
from config.bossenv import load_aws_secrets
load_dotenv()
load_aws_secrets()
import os 
from typing import List
import random

project_id = os.getenv("GOOGLE_PROJECT_ID")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
engine_id = os.getenv("NEWSHIVE_GOOGLE_ENGINE_ID")
api_key = os.getenv("GOOGLE_API_KEY")
AWS_REGION = os.getenv("AWS_MODEL_REGION")
LLM_MODEL = os.getenv("LLM_MODEL_NEWSHIVE")
DATABASE_URL = os.getenv("DATABASE_URL")
SPECIFIC_ENGINES = {
    "Business Standard": os.getenv("BS_ENGINE_ID"),
    "Economic Times": os.getenv("ECO_ENGINE_ID"),
    "Free Press Journal": os.getenv("FREE_ENGINE_ID"),
    "The Hindu": os.getenv("HINDU_ENGINE_ID"),
    "India Today": os.getenv("INDIA_ENGINE_ID"),
    "India TV": os.getenv("INDIA_TV_ENGINE_ID"),
    "Live Mint": os.getenv("LIVE_ENGINE_ID"),
    "Money Control": os.getenv("MC_ENGINE_ID"),
    "News18": os.getenv("NEW18_ENGINE_ID"),
    "PR Newswire": os.getenv("PRNEWS_ENGINE_ID"),
    "Times of India": os.getenv("TOI_ENGINE_ID"),
    "Zee News": os.getenv("ZEE_ENGINE_ID"),
}

class Config:
    REQUEST_DELAY = (1, 4) 
    TIMEOUT = 45  
    MAX_RETRIES = 5
    MAX_WORKERS = 4
    RETRY_DELAY = 5
    MIN_CONTENT_LENGTH = 200 
    MAX_CONTENT_LENGTH = 50000  
    QUALITY_THRESHOLD = 0.6 
    CACHE_DURATION_HOURS = 24

    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0",
    ]

    PROXIES: List[str] = []

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
]

def get_random_header():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1", 
    }

OUTPUT_FOLDER = "data"
INPUT_FOLDER = "data"
SEARCH_RESULTS_FILE = os.path.join(INPUT_FOLDER, "search_results.json")
SIMILARITY_THRESHOLD = 0.85
SOMEWHAT_SIMILAR_THRESHOLD = 0.75
MAX_RETRIES = int(os.getenv("MAX_DB_RETRIES", 5))
RETRY_DELAY = float(os.getenv("RETRY_DELAY_SECONDS", 2))
DB_CONN_TIMEOUT = int(os.getenv("DB_CONN_TIMEOUT", 10))  