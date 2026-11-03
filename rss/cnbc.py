from .rss_processor import process_rss_feed
from typing import Dict, Any

def cnbc_item_processor(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "description": entry.get("description", ""),
        "pubDate": entry.get("published", ""),
        "source_type": "rss",
    }

def cnbc_rss(rss_url: str, output_file: str = "data/cnbc.json"):
    return process_rss_feed(
        rss_url=rss_url,
        json_file=output_file,
        csv_file="log/rss_statistics_cnbc.csv",
        source="cnbc",
        source_category="default",
        item_processor=cnbc_item_processor,
    )

if __name__ == "__main__":
    url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    json_data = cnbc_rss(url)
