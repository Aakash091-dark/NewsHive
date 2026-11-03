from typing import Dict, Callable, Awaitable
from urllib.parse import urlparse
import os
import sys
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.json_log import log as logger
from .playwright_scraper import scrape_with_playwright

def safe_import_scraper(module_name: str, function_name: str) -> Callable:
    try:
        module = importlib.import_module(f"specific_scrapers.{module_name}")
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not import {function_name} from {module_name}: {e}")
        return None

SCRAPERS = {
    "livemint": safe_import_scraper("livemint", "scrape_livemint"),
    "timesofindia": safe_import_scraper("timesofindia", "scrape_times_of_india"),
    "prnewswire": safe_import_scraper("prnewswire", "scrape_pr_newswire"),
    "economic_times": safe_import_scraper("economic_times", "scrape_economic_times"),
    "thehindu": safe_import_scraper("thehindu", "scrape_the_hindu"),
    "zeenews": safe_import_scraper("zeenews", "scrape_zeenews"),
    "indiatoday": safe_import_scraper("indiatoday", "scrape_india_today"),
    "indiatvnews": safe_import_scraper("indiatvnews", "scrape_india_tv_news"),
    "etnow": safe_import_scraper("etnow", "scrape_etnow"),
    "indianexpress": safe_import_scraper("indianexpress", "scrape_indian_express"),
    "hindustantimes": safe_import_scraper("hindustantimes", "scrape_hindustan_times"),
    "businesstandard" : safe_import_scraper("business_standard", "scrape_business_standard"),
    "freepressjournal" : safe_import_scraper("free_press_journal", "scrape_free_press_journal"),
    "moneycontrol" : safe_import_scraper("money_control", "scrape_moneycontrol"),
    "news18" : safe_import_scraper("news_18", "scrape_news18"),
}

def build_source_scraper_map() -> Dict[str, callable]:
    base_map = {
        "livemint.com": SCRAPERS["livemint"],
        "timesofindia.com": SCRAPERS["timesofindia"],
        "indiatimes.com": SCRAPERS["timesofindia"],
        "prnewswire.com": SCRAPERS["prnewswire"],
        "economictimes.com": SCRAPERS["economic_times"],
        "economictimes.indiatimes.com": SCRAPERS["economic_times"],
        "thehindu.com": SCRAPERS["thehindu"],
        "zeenews.com": SCRAPERS["zeenews"],
        "zeenews.india.com": SCRAPERS["zeenews"],
        "indiatoday.in": SCRAPERS["indiatoday"],
        "indiatvnews.com": SCRAPERS["indiatvnews"],
        "etnownews.com": SCRAPERS["etnow"],
        "indianexpress.com": SCRAPERS["indianexpress"],
        "hindustantimes.com": SCRAPERS["hindustantimes"],
        "business-standard.com": SCRAPERS["businesstandard"],
        "moneycontrol.com": SCRAPERS["moneycontrol"],
        "freepressjournal.in": SCRAPERS["freepressjournal"],
        "news18.com": SCRAPERS["news18"],

    }

    available_scrapers = {k: v for k, v in base_map.items() if v is not None}
    return available_scrapers

SOURCE_SCRAPER_MAP = build_source_scraper_map()

async def get_scraper_for_source(url: str) -> Awaitable[Callable]:
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower().replace("www.", "").strip()

        if not domain:
            logger.warning(f"Could not extract domain from URL: {url}, using generic scraper.")
            return scrape_with_playwright

        scraper_func = SOURCE_SCRAPER_MAP.get(domain)
        if scraper_func:
            logger.info(f"Using specific scraper for domain: {domain}")
            return scraper_func

        best_match_key = None
        best_match_scraper = None

        for key, scraper in SOURCE_SCRAPER_MAP.items():
            if domain.endswith(key):
                # We want the longest matching key (most specific)
                if best_match_key is None or len(key) > len(best_match_key):
                    best_match_key = key
                    best_match_scraper = scraper
        
        if best_match_scraper:
            logger.info(f"Using specific scraper for subdomain: {domain} (matched with {best_match_key})")
            return best_match_scraper

        logger.info(f"No specific scraper found for domain: {domain}, using generic scraper.")
        return scrape_with_playwright

    except Exception as e:
        logger.error(f"Error resolving scraper for URL '{url}': {e}, using generic scraper.")
        return scrape_with_playwright

from rss import (
    all_rss,
    economictimes_rss,
    prnewswire_rss,
    livemint_rss,
    thehindu_Industry_rss,
    thehindu_Economy_rss,
)
from rss import (
    thehindu_business_rss,
    thehindu_markets_rss,
    zeenews_rss,
    hindustantimes_rss,
    indiatoday_rss,
    indiatvnews_rss,
    timesofindia_business_rss,
)
from rss import (
    indianexpress_rss,
    economictimes_markets_rss,
    economictimes_industry_rss,
    etnow_rss,
    indiatimes_rss,
)


rss_websites = {
    "prnews_manufacturing": "https://www.prnewswire.com/rss/heavy-industry-manufacturing-latest-news/heavy-industry-manufacturing-latest-news-list.rss",
    "economictimes_industry": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
    "economictimes_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "livemint_market": "https://www.livemint.com/rss/markets",
    "livemint_companies": "https://www.livemint.com/rss/companies",
    "thehindu_Industry": "https://www.thehindu.com/business/Industry/feeder/default.rss",
    "thehindu_Economy": "https://www.thehindu.com/business/economy/feeder/default.rss",
    "thehindu_markets": "https://www.thehindu.com/business/markets/feeder/default.rss",
    "thehindu_business": "https://www.thehindu.com/business/feeder/default.rss",
    "znews_business": "http://zeenews.india.com/rss/business.xml",
    "hindustantimes_business": "https://www.hindustantimes.com/feeds/rss/business/rssfeed.xml",
    "indiatoday_economics": "https://www.indiatoday.in/rss/1206513",
    "indiatvnews_business": "https://www.indiatvnews.com/rssnews/topstory-business.xml",
    "timesofindia_business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
    "etnow_infrastructure": "https://www.etnownews.com/feeds/gns-etn-infrastructure.xml",
    "etnow_realestate": "https://www.etnownews.com/feeds/gns-etn-real-estate.xml",
    "etnow_companies": "https://www.etnownews.com/feeds/gns-etn-companies.xml",
    "etnow_market": "https://www.etnownews.com/feeds/gns-etn-markets.xml",
    "indianexpress_companies": "https://indianexpress.com/section/business/companies/feed/",
    "indianexpress_business": "https://indianexpress.com/section/business/feed/",
    "indiatimes_economy": "https://cfo.economictimes.indiatimes.com/rss/economy",

}


rss_functions = {
    "prnews_manufacturing": prnewswire_rss,
    "economictimes": economictimes_rss,
    "economictimes_markets": economictimes_markets_rss,
    "economictimes_industry": economictimes_industry_rss,
    "livemint_market": livemint_rss,
    "livemint_companies": livemint_rss,
    "thehindu_Industry": thehindu_Industry_rss,
    "thehindu_Economy": thehindu_Economy_rss,
    "thehindu_markets": thehindu_markets_rss,
    "thehindu_business": thehindu_business_rss,
    "znews_business": zeenews_rss,
    "hindustantimes_business": hindustantimes_rss,
    "indiatoday_economics": indiatoday_rss,
    "indiatvnews_business": indiatvnews_rss,
    "timesofindia_business": timesofindia_business_rss,
    "etnow_infrastructure": etnow_rss,
    "etnow_realestate": etnow_rss,
    "etnow_companies": etnow_rss,
    "etnow_market": etnow_rss,
    "indianexpress_companies": indianexpress_rss,
    "indianexpress_business": indianexpress_rss,
    "indiatimes_economy": indiatimes_rss,
    "all_rss": all_rss,
}
