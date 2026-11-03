import re
from bs4 import BeautifulSoup
from .fallback_utils import extract_content_with_fallback


def scrape_india_tv_news(soup: BeautifulSoup) -> str:
    try:
        paragraph_selectors = [
            "div#articleContent p",
            "div.storyParagraph p",
            "div#storyData p",
            "div#storyContent p",
            "div.itv-article-text p",
            "div.article_text p",
            "div.newsDescription p",
            "div.content-area p",
            "div.textDiv p",
            "div.clearfix > p",
        ]

        paragraphs = []
        seen = set()

        for selector in paragraph_selectors:
            for tag in soup.select(selector):
                for noise in tag.select(
                    ".ad, .advertisement, .social-share, .related-news, .tags, script, style"
                ):
                    noise.decompose()

                text = tag.get_text(strip=True)
                text = re.sub(r"\s+", " ", text)
                text = re.sub(
                    r"(India TV News Desk|PTI|ANI)", "", text, flags=re.IGNORECASE
                )
                text = re.sub(r"Also read:.*$", "", text, flags=re.IGNORECASE)
                text = text.strip()

                if text and len(text) > 30 and text not in seen:
                    paragraphs.append(text)
                    seen.add(text)

        if len(paragraphs) >= 3 and sum(len(p.split()) for p in paragraphs) > 100:
            return "\n\n".join(paragraphs)

        # Container fallback selectors
        container_selectors = [
            "div#articleContent",
            "div.storyParagraph",
            "div#storyData",
            "div#storyContent",
            "div.itv-article-text",
            "div.article_text",
            "div.newsDescription",
            "div.content-area",
            "div.textDiv",
            "div.clearfix",
        ]

        for selector in container_selectors:
            container = soup.select_one(selector)
            if container:
                for noise in container.select(
                    ".ad, .advertisement, .social-share, .related-news, .tags, script, style"
                ):
                    noise.decompose()

                content = container.get_text(strip=True)
                content = re.sub(r"\s+", " ", content)
                content = re.sub(
                    r"(India TV News Desk|PTI|ANI)", "", content, flags=re.IGNORECASE
                )
                content = re.sub(r"Also read:.*$", "", content, flags=re.IGNORECASE)
                content = content.strip()

                if content and len(content.split()) > 100:
                    return content

        # Final fallback to generic extraction
        return extract_content_with_fallback(
            soup, container_selectors, site_name="India TV News"
        )

    except Exception:
        return extract_content_with_fallback(
            soup,
            ["div#articleContent", "div#storyContent", "div.itv-article-text"],
            site_name="India TV News",
        )
