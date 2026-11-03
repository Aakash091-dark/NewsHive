import requests
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse
import re
import time

def fetch_page(url, headers, retries=3, timeout=15):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[Retry {attempt+1}] Failed to fetch {url}: {e}")
            time.sleep(1.5)
    return ""

def extract_text_from_soup(soup):
    selectors = [
        "div.Normal",
        "div.article_content",
        "div.artText",
        "div._3YYSt.clearfix",
        "div#content",
        "section#content",
        "div.story",
        "div.section1",
        "div#app",
        "article",
        "div#storydiv",
        "div#contentwrapper",
    ]

    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            for tag in node.find_all(["script", "style", "aside", "figure", "noscript", "iframe"]):
                tag.decompose()

            for comment in node.find_all(string=lambda t: isinstance(t, Comment)):
                comment.extract()

            text_parts = []
            for el in node.find_all(["p", "div", "span"]):
                text = el.get_text(" ", strip=True)
                if len(text.split()) > 3 and not re.search(
                    r"(also\s+read|read\s+more|watch\s+video)", text, re.I
                ):
                    text_parts.append(text)
            if text_parts:
                return " ".join(text_parts)
    return ""

def scrape_times_of_india(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    html = fetch_page(url, headers)
    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    text = extract_text_from_soup(soup)

    if len(text.split()) < 60:
        print("[Info] Trying AMP/mobile fallback...")
        parsed = urlparse(url)
        article_id = parsed.path.split("/")[-1]
        amp_urls = [
            f"{parsed.scheme}://timesofindia.indiatimes.com/amp_articleshow/{article_id}",
            f"{parsed.scheme}://timesofindia.indiatimes.com/amp_articleshow/{article_id.replace('.cms','')}.cms",
            f"{parsed.scheme}://timesofindia.indiatimes.com/business/india-business/amp_articleshow/{article_id}",
        ]

        for amp_url in amp_urls:
            amp_html = fetch_page(amp_url, headers)
            if amp_html:
                amp_soup = BeautifulSoup(amp_html, "html.parser")
                amp_text = extract_text_from_soup(amp_soup)
                if len(amp_text.split()) > 60:
                    print(f"[OK] Extracted from AMP: {amp_url}")
                    return amp_text
        print("[Warning] AMP fallback also failed.")
    else:
        print(f"[OK] Extracted {len(text.split())} words from main page.")
    return text

# if __name__ == "__main__":
#     url = "https://timesofindia.indiatimes.com/business/india-business/ascendas-india-trust-to-acquire-warehouse-project-for-rs-70-cr/articleshow/70178926.cms"
#     content = scrape_times_of_india(url)
#     print("\n--- Extracted Content ---\n")
#     print(content)
