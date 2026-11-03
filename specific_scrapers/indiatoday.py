import re
import requests
from bs4 import BeautifulSoup
from typing import Union
from .fallback_utils import extract_content_with_fallback
from logs.json_log import log as logger

def scrape_india_today(url_or_soup: Union[str, BeautifulSoup]) -> str:
    soup = None
    if isinstance(url_or_soup, str):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url_or_soup, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.error(f"Error fetching India Today URL {url_or_soup}: {e}")
            return ""
    elif isinstance(url_or_soup, BeautifulSoup):
        soup = url_or_soup

    if not soup:
        return ""

    try:
        paragraph_selectors = [
            "div#story-left p",
            "div.story-details p",
            "div#story p",
            "div.itg-article-content p",
            "div.article_content p",
            "div.article-body p",
            "div#Content p",
            "div.clearfix p",
            "div.article p",
            "div#container > div > div > div > p",
        ]

        paragraphs = []
        seen = set()

        for selector in paragraph_selectors:
            for tag in soup.select(selector):
                for noise in tag.select(
                    ".ad, .advertisement, .social-share, .tags, .metadata, .related-news, script, style"
                ):
                    noise.decompose()

                text = tag.get_text(strip=True)
                text = re.sub(r"\s+", " ", text)
                text = re.sub(
                    r"(India Today Web Desk|PTI|ANI)", "", text, flags=re.IGNORECASE
                )
                text = re.sub(r"Also read:.*$", "", text, flags=re.IGNORECASE)
                text = text.strip()

                if text and len(text) > 50 and text not in seen:
                    paragraphs.append(text)
                    seen.add(text)

        if len(paragraphs) >= 3 and sum(len(p.split()) for p in paragraphs) > 100:
            return "\n\n".join(paragraphs)

        # If paragraph extraction failed, fallback to container-level logic
        container_selectors = [
            "div#story-left",
            "div.story-details",
            "div#story",
            "div.itg-article-content",
            "div.article_content",
            "div.article-body",
            "div#Content",
            "div.clearfix",
            "div.article",
        ]

        for selector in container_selectors:
            container = soup.select_one(selector)
            if container:
                for noise in container.select(
                    ".ad, .advertisement, .social-share, .tags, .metadata, .related-news, script, style"
                ):
                    noise.decompose()

                content = container.get_text(strip=True)
                content = re.sub(r"\s+", " ", content)
                content = re.sub(
                    r"(India Today Web Desk|PTI|ANI)", "", content, flags=re.IGNORECASE
                )
                content = re.sub(r"Also read:.*$", "", content, flags=re.IGNORECASE)
                content = content.strip()

                if content and len(content.split()) > 50:
                    return content

        # Final fallback
        return extract_content_with_fallback(
            soup, container_selectors, site_name="India Today"
        )

    except Exception as e:
        logger.error(f"Error extracting India Today content: {e}")
        return extract_content_with_fallback(
            soup,
            ["div#story-left", "div.story-details", "div.article-body"],
            site_name="India Today",
        )
