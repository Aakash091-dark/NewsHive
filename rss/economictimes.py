from .rss_processor import process_rss_feed
from typing import Dict, Any
from datetime import datetime

# ----------------------------------------------
# Custom date parser for Economic Times RSS dates
# ----------------------------------------------
def parse_economic_times_date(date_str: str) -> str:
    """
    Parses Economic Times RSS pubDate formats.
    Returns YYYY-MM-DD or empty string on failure.
    """

    if not date_str:
        return ""

    # Common RSS formats
    possible_formats = [
        "%a, %d %b %Y %H:%M:%S %Z",   # Tue, 19 Nov 2024 12:23:00 IST
        "%a, %d %b %Y %H:%M:%S %z",   # Tue, 19 Nov 2024 12:23:00 +0530
        "%Y-%m-%dT%H:%M:%S%z",        # ISO with timezone
        "%Y-%m-%dT%H:%M:%S",          # ISO without timezone
    ]

    for fmt in possible_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%Y-%m-%d")
        except:
            continue

    return ""


# ----------------------------------------------
# Item Processor
# ----------------------------------------------
def economictimes_item_processor(entry: Dict[str, Any]) -> Dict[str, Any]:
    pub_date = entry.get("published", "")

    return {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "description": entry.get("description", ""),
        "pubDate": parse_economic_times_date(entry.get("published", "")),
        "source_type": "rss",
    }


# ----------------------------------------------
# Main Economic Times RSS Function
# ----------------------------------------------
def economictimes_rss(rss_url, json_file, csv_file, source, source_category) -> int:
    new_count = process_rss_feed(
        rss_url=rss_url,
        json_file=json_file,
        csv_file=csv_file,
        source=source,
        source_category=source_category,
        item_processor=economictimes_item_processor,
    )
    return new_count


# ----------------------------------------------
# Test
# ----------------------------------------------
if __name__ == "__main__":
    url = "https://manufacturing.economictimes.indiatimes.com/rss/industry"
    json_data = economictimes_rss(
        url,
        "data/economictimes_industry.json",
        "log/rss_statistics_economictimes_industry.csv",
        "economictimes",
        "industry",
    )
