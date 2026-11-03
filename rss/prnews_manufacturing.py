import feedparser
import json
import csv
import os
from datetime import datetime
from .economictimes import parse_economic_times_date
from urllib.parse import urlparse, parse_qs


def get_actual_url(url: str) -> str:
    """
    Extracts the actual URL from PR Newswire's redirect link.
    """
    try:
        parsed_url = urlparse(url)
        if "prnewswire.com" in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            if "u" in query_params:
                return query_params["u"][0]
    except Exception:
        pass 
    return url


def ensure_directories():
    os.makedirs("log", exist_ok=True)
    os.makedirs("data", exist_ok=True)


def log_statistics(new_count: int, duplicate_count: int, csv_file: str):
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


def prnewswire_rss(rss_url, json_file, csv_file, source, source_category):
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
        if entry.get("language", "") == "en-US":
            title = entry.get("title", "")

            if title in existing_titles:
                duplicate_count += 1
            else:
                new_count += 1
                item = {
                    "title": title,
                    "link": get_actual_url(entry.get("link", "")),
                    "description": entry.get("description", ""),
                    "pubDate": parse_economic_times_date(entry.get("published", "")),
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


if __name__ == "__main__":
    url = "https://www.prnewswire.com/rss/heavy-industry-manufacturing-latest-news/heavy-industry-manufacturing-latest-news-list.rss"
    json_data = prnewswire_rss(url)
