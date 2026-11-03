from bs4 import BeautifulSoup
import asyncio
import random
import hashlib
from datetime import datetime
from typing import Optional, Dict, Tuple, Any
import chardet
import sys, re
import os
import httpx
import anyio
from httpx_socks import AsyncProxyTransport
from python_socks import ProxyError
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from logs.json_log import log as logger
from config.settings import Config
from config.models import ScrapingStats
from tor.tor_session_manager import tor_session_manager
from web_scrapping.playwright_scraper import scrape_with_playwright, PageNotFoundError, ScrapingSkippedException

url_cache: Dict[str, Tuple[datetime, str]] = {}

def detect_encoding(content: bytes) -> str:
    try:
        detected = chardet.detect(content)
        encoding = detected.get("encoding", "utf-8")
        confidence = detected.get("confidence", 0)

        if confidence < 0.7:
            logger.warning(
                f"Low confidence ({confidence}) for detected encoding: {encoding}"
            )
            return "utf-8"

        return encoding
    except Exception as e:
        logger.error(f"Error detecting encoding: {e}")
        return "utf-8"

def extract_enhanced_title(soup: BeautifulSoup) -> str:
    title_selectors = [
        "h1.headline",
        "h1[data-testid='headline']",
        "h1.article-title",
        "h1.story-title",
        ".article-headline h1",
        "h1",
        "title",
        ".headline",
        ".article-title",
        ".post-title",
        ".entry-title",
        ".story-headline",
        ".main-title",
        "[data-testid='headline']",
        ".title",
        "meta[property='og:title']",
        "meta[name='twitter:title']",
    ]

    for selector in title_selectors:
        try:
            if selector.startswith("meta"):
                element = soup.select_one(selector)
                if element:
                    title = element.get("content", "").strip()
            else:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)

            if title and len(title) > 10 and len(title) < 50:
            
                title = re.sub(r"\s+", " ", title)
                title = re.sub(r"[|\-–—]\s*.*$", "", title)  
                return title.strip()

        except Exception as e:
            logger.debug(f"Title extraction failed for selector {selector}: {e}")

    return "Untitled Article"

async def get_page_content(
    url: str, scraping_stats: ScrapingStats, max_retries: int = Config.MAX_RETRIES
) -> Optional[Tuple[BeautifulSoup, str]]:
    if not tor_session_manager.get_session():
        logger.error("Failed to start Tor session. Aborting request.")
        return None, url

    scraping_stats.total_attempted += 1

    cache_key = hashlib.md5(url.encode()).hexdigest()
    if cache_key in url_cache:
        cache_time, cached_content = url_cache[cache_key]
        if (datetime.now() - cache_time).total_seconds() < Config.CACHE_DURATION_HOURS * 3600:
            return BeautifulSoup(cached_content, "html.parser"), url
    try:
        content = await scrape_with_playwright(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            url_cache[cache_key] = (datetime.now(), str(soup))
            scraping_stats.successful += 1
            return soup, url
        else:
            logger.warning(f"Playwright failed to fetch content for {url}. Falling back to requests.")
    except PageNotFoundError:
        logger.warning(f"404 Not Found for {url} (Playwright). Skipping fallback.")
        scraping_stats.failed += 1
        return None, url
    except ScrapingSkippedException as e:
        logger.info(f"Skipping fallback for {url}: {e}")
        scraping_stats.failed += 1
        return None, url
    except Exception as e:
        logger.error(f"Error scraping with Playwright for {url}: {e}. Falling back to requests.")
    
    # Check binary extensions again before fallback
    if url.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar", ".exe", ".mp3", ".mp4")):
        logger.info(f"Skipping fallback for binary file: {url}")
        scraping_stats.failed += 1
        return None, url

    transport = AsyncProxyTransport.from_url("socks5://127.0.0.1:9050")
    
    async with httpx.AsyncClient(transport=transport) as client:
        for attempt in range(max_retries):
            try:
                headers = {
                    "User-Agent": random.choice(Config.USER_AGENTS)
                }
                # Use stream to check headers before downloading body
                async with client.stream("GET", url, headers=headers, timeout=60.0) as response:
                    if response.status_code == 404:
                        logger.warning(f"404 Not Found for {url} (HTTPX). Skipping retries.")
                        scraping_stats.failed += 1
                        return None, url

                    if response.status_code == 200:
                        content_type = response.headers.get("Content-Type", "").lower()
                        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                            logger.info(f"Skipping non-HTML content type {content_type} for {url}")
                            # Stop retrying for this URL
                            break
                        
                        # Check size limit (e.g., 10MB)
                        content_length = response.headers.get("Content-Length")
                        if content_length and int(content_length) > 10 * 1024 * 1024:
                            logger.info(f"Skipping large file ({content_length} bytes) for {url}")
                            break

                        # Read content safely
                        content = await response.read()
                        if content:
                            encoding = detect_encoding(content)
                            soup = BeautifulSoup(content, "html.parser", from_encoding=encoding)
                            final_url = str(response.url)
                            url_cache[cache_key] = (datetime.now(), str(soup))
                            scraping_stats.successful += 1
                            delay = random.uniform(20, 40)
                            logger.info(f"Waiting for {delay:.2f} seconds before next request.")
                            await asyncio.sleep(delay)
                            return soup, final_url
            except (httpx.RequestError, anyio.EndOfStream, ProxyError) as e:
                logger.warning(f"Request failed for {url} on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(Config.RETRY_DELAY * (2 ** attempt))

    scraping_stats.failed += 1
    return None, url


def extract_metadata(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    metadata = {}
    date_selectors = [
        "time[datetime]",
        "meta[property='article:published_time']",
        "meta[name='date']",
        "meta[name='pubdate']",
        "meta[name='timestamp']",
        "span[class*='date']",
        "p[class*='date']",
        "div[class*='date']",
        "[data-testid='publish-date']",
        ".publish-date",
        ".article-date",
        ".story-date",
    ]

    author_selectors = [
        "[data-testid='author']",
        ".author",
        ".byline",
        ".story-author",
        "meta[name='author']",
        "meta[property='article:author']",
    ]

    for selector in author_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                if selector.startswith("meta"):
                    author = element.get("content", "")
                else:
                    author = element.get_text(strip=True)

                if author and len(author) < 50:
                    metadata["author"] = author
                    break
        except Exception:
            continue

    tag_selectors = [
        ".tags a",
        ".categories a",
        ".article-tags a",
        "[data-testid='tags'] a",
    ]

    tags = []
    for selector in tag_selectors:
        try:
            elements = soup.select(selector)
            for element in elements[:10]: 
                tag = element.get_text(strip=True)
                if tag and tag not in tags:
                    tags.append(tag)
        except Exception:
            continue

    if tags:
        metadata["tags"] = tags

    return metadata
