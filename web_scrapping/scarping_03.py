import sys
import os
import asyncio
import json
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logs.json_log import log as logger
from config.models import ScrapingStats
from web_scrapping.get_content import extract_metadata, get_page_content
from .scrap_specific_04 import get_scraper_for_source
from DATABASE.fetch import check_url_in_second_table


class ScraperManager:
    def __init__(self, config_overrides: Dict[str, Any] = None):
        self.failed_urls: List[str] = []
        self.failed_articles: List[Dict[str, Any]] = []
        self.duplicate_articles: List[Dict[str, Any]] = []
        self.results: List[Dict[str, Any]] = []
        self.scraping_stats = ScrapingStats()
        self.reset_state()

    def reset_state(self):
        self.failed_urls = []
        self.failed_articles = []
        self.duplicate_articles = []
        self.results = []
        self.scraping_stats = ScrapingStats()

    def get_results(self) -> List[Dict[str, Any]]:
        return self.results
    
    def get_failed_articles(self) -> List[Dict[str, Any]]:
        return self.failed_articles
    
    def get_duplicate_articles(self) -> List[Dict[str, Any]]:
        return self.duplicate_articles

    async def scrape(self, items: List[Any] | str, search_term: str, source_type: str):
        if isinstance(items, str):
            items = [{"link": items}]
        elif isinstance(items, list) and items and isinstance(items[0], str):
            items = [{"link": url} for url in items]
        elif isinstance(items, list) and not items:
            items = []

        if source_type == "rss":
            logger.info(f"Scraping {len(items)} new items for RSS category")
        else:
            logger.info(f"Scraping {len(items)} items for search term")
        
        tasks = [self._scrape_single(item, self.scraping_stats, search_term, source_type) for item in items]
        scraped_results = await asyncio.gather(*tasks)
        self.results = [res for res in scraped_results if res and res.get("raw_content")]
        logger.info("Scraping completed.")

    async def _scrape_single(
        self, item: Dict[str, Any], scraping_stats: ScrapingStats, search_term: str, source_type: str
    ) -> Dict[str, Any]:

        url = item.get("link")
        if not url:
            return {}

        if check_url_in_second_table(url):
            logger.info(f"Duplicate URL found in SECOND_TABLE, skipping: {url}")
            self.duplicate_articles.append({
                "url": url,
                "reason": "Duplicate URL in SECOND_TABLE",
                "source": urlparse(url).netloc
            })
            return {}
            
        try:
            parsed_url = urlparse(url)
            if "edge.prnewswire.com" in parsed_url.netloc and "/c/link/" in parsed_url.path:
                logger.info(f"Skipping PRN redirect link: {url}")
                self.failed_articles.append({
                    "url": url,
                    "reason": "PRN redirect skipped",
                    "source": "edge.prnewswire.com"
                })
                return {}

            soup, final_url = await get_page_content(url, scraping_stats)
            if not soup or not getattr(soup, "text", None):
                logger.error(f"Empty or invalid HTML for {url}")
                self.failed_articles.append({
                    "url": url,
                    "reason": "Empty or invalid HTML",
                    "source": urlparse(url).netloc
                })
                return {}
            metadata = extract_metadata(soup, final_url) or {}
            title = (metadata.get("title") or "").strip() or (item.get("title") or "").strip()
            pubDate = str(metadata.get("article:published_time") or "").strip() or str(item.get("pubDate") or "").strip()
            if not pubDate:
                pubDate = None
            scraper = await get_scraper_for_source(final_url)

            if asyncio.iscoroutinefunction(scraper):
                content = await scraper(final_url)
            else:
                content = scraper(final_url)

            if not content or len(content.strip()) < 20:
                logger.warning(f"No meaningful content extracted from {url}")
                self.failed_articles.append({
                    "url": final_url,
                    "reason": "No meaningful content extracted",
                    "source": urlparse(final_url).netloc
                })
                return {}

            news_item = {
                "url": final_url,
                "raw_content": content,
                "title": title,
                "source": metadata.get("og:site_name") or urlparse(final_url).netloc,
                "pubDate": pubDate,
                "metadata": metadata,
                "search_term": search_term,
                "source_type": source_type,
            }
            return news_item

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            self.failed_urls.append(url)
            self.failed_articles.append({
                "url": url,
                "reason": str(e),
                "source": urlparse(url).netloc
            })
            return {}

    def save_results(self):
        if not self.failed_urls:
            return

        try:
            with open("failed_urls.json", "w", encoding="utf-8") as f:
                json.dump(list(set(self.failed_urls)), f, indent=4)
            logger.info("Saved failed URLs.")
        except Exception:
            pass
