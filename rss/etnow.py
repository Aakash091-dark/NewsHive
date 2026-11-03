import feedparser
import json
import csv
import os
from datetime import datetime

def ensure_directories():
    os.makedirs("log", exist_ok=True)
    os.makedirs("data", exist_ok=True)

def log_statistics(
    new_count: int,
    duplicate_count: int,
    csv_file: str = "log/rss_statistics_etnow.csv",
):
    ensure_directories()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    file_exists = os.path.exists(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["Timestamp", "New Titles", "Duplicate Titles", "Total Processed"]
            )
        writer.writerow(
            [timestamp, new_count, duplicate_count, new_count + duplicate_count]
        )

def etnow_rss(rss_url: str, json_file: str, csv_file: str, source: str, source_category: str):
    ensure_directories()

    existing_titles = set()
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                existing_titles = {item["title"] for item in existing_data}
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = []
    else:
        existing_data = []

    feed = feedparser.parse(rss_url)

    new_items = []
    new_count = 0
    duplicate_count = 0

    for entry in feed.entries:
        title = entry.get("title", "")

        if title in existing_titles:
            duplicate_count += 1
        else:
            new_count += 1
            item = {
                "title": title,
                "link": entry.get("link", ""),
                "description": entry.get("description", ""),
                "pubDate": entry.get("published", ""),
                "source": source,
                "source_category": source_category,
                "source_type": "rss",
            }
            new_items.append(item)
            existing_titles.add(title)

    all_items = existing_data + new_items

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=4, ensure_ascii=False)

    log_statistics(new_count, duplicate_count, csv_file)
    return new_count
