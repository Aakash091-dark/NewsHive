import feedparser
import json
import csv
import os
from datetime import datetime
from typing import Callable, Dict, Any, List
def ensure_directories():
    os.makedirs("log", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def log_statistics(
    new_count: int,
    duplicate_count: int,
    csv_file: str,
):
    ensure_directories()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["Timestamp", "New Links", "Duplicate Links", "Total Processed"]
            )
        writer.writerow(
            [timestamp, new_count, duplicate_count, new_count + duplicate_count]
        )

def process_rss_feed(
    rss_url: str,
    json_file: str,
    csv_file: str,
    source: str,
    source_category: str,
    item_processor: Callable[[Dict[str, Any]], Dict[str, Any]],
) -> str:
    ensure_directories()

    existing_links = set()
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                existing_links = {item["link"] for item in existing_data}
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []
    else:
        existing_data = []

    feed = feedparser.parse(rss_url)

    new_items = []
    new_count = 0
    duplicate_count = 0

    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue

        if link in existing_links:
            duplicate_count += 1
        else:
            new_count += 1
            item = item_processor(entry)
            item["source"] = source
            item["source_category"] = source_category
            item["source_type"] = "rss"

            new_items.append(item)
            existing_links.add(link)

    all_items = existing_data + new_items

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=4, ensure_ascii=False)

    log_statistics(new_count, duplicate_count, csv_file)
    return new_count
