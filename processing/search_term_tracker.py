import json
import os
from typing import Set
from logs.json_log import log

TRACKER_FILE = "data/processed_terms.json"

def load_processed_terms() -> Set[str]:
    if not os.path.exists(TRACKER_FILE):
        return set()
    try:
        with open(TRACKER_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return set(data.get("processed_terms", []))
            elif isinstance(data, list): 
                return set(data)
            return set()
    except Exception as e:
        log.error(f"Error loading processed terms: {e}")
        return set()

def save_processed_terms(terms: Set[str]):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(TRACKER_FILE), exist_ok=True)
        with open(TRACKER_FILE, "w") as f:
            json.dump({"processed_terms": list(terms)}, f, indent=4)
    except Exception as e:
        log.error(f"Error saving processed terms: {e}")

def mark_search_term_processed(term: str):
    try:
        terms = load_processed_terms()
        if term not in terms:
            terms.add(term)
            save_processed_terms(terms)
    except Exception as e:
        log.error(f"Error marking search term as processed: {e}")

def is_search_term_processed(term: str) -> bool:
    try:
        terms = load_processed_terms()
        return term in terms
    except Exception as e:
        log.error(f"Error checking if search term is processed: {e}")
        return False
