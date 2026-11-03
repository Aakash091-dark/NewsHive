from .rss_processor import process_rss_feed
from typing import Dict, Any
from dateutil import parser as date_parser


# -----------------------------------------------------------
# Internal date formatter (independent & self-contained)
# -----------------------------------------------------------
def format_rss_date(date_string: str):
    """
    Parses RSS published dates safely.
    Returns ISO format date (YYYY-MM-DD) or None.
    """
    if not date_string or not isinstance(date_string, str):
        return None

    try:
        dt = date_parser.parse(date_string, fuzzy=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


# -----------------------------------------------------------
# RSS item processor (uses internal date formatter)
# -----------------------------------------------------------
def generic_item_processor(entry: Dict[str, Any]) -> Dict[str, Any]:

    raw_pub = entry.get("published") or entry.get("pubDate") or ""

    return {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "description": entry.get("description", ""),
        "pubDate": format_rss_date(raw_pub),
        "source_type": "rss",
    }


# -----------------------------------------------------------
# Universal RSS handler
# -----------------------------------------------------------
def all_rss(rss_url: str, json_file: str, csv_file: str, source: str, source_category: str):

    new_count = process_rss_feed(
        rss_url=rss_url,
        json_file=json_file,
        csv_file=csv_file,
        source=source,
        source_category=source_category,
        item_processor=generic_item_processor,
    )

    return new_count
