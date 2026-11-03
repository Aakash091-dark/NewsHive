import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

# -----------------------------
# 1) SIMPLE REQUEST FIRST
# -----------------------------
def get_page_source_with_requests(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.text
    except Exception:
        pass
    return ""

# -----------------------------
# 2) PLAYWRIGHT FALLBACK
# -----------------------------
def get_page_source_with_playwright(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle")
            html = page.content()
            browser.close()
            return html
    except Exception:
        return ""

# -----------------------------
# 3) CONTENT EXTRACTOR
# -----------------------------
def extract_the_hindu_content(soup: BeautifulSoup) -> str:
    selectors = [
        "div.article p",
        "div.articlebodycontent p",
        "div#content-body p",
        "div.story p",
        "div#articleContent p",
        "div.content-body p",
        "div.content p",
        "div.articleContent p",
        "div#content p",
        "article p",
    ]

    paragraphs, seen = [], set()

    for selector in selectors:
        for tag in soup.select(selector):

            # Remove noise
            for noise in tag.select("script, style, .ad, .social, .related, .footer"):
                noise.decompose()

            text = tag.get_text(strip=True)
            if not text or len(text) < 50:
                continue

            # Skip promotional junk
            if re.search(r"also\s+read", text, re.IGNORECASE):
                continue

            text = re.sub(r"\s+", " ", text).strip()

            if text not in seen:
                paragraphs.append(text)
                seen.add(text)

    return "\n\n".join(paragraphs).strip()

# -----------------------------
# 4) MAIN SCRAPER
# -----------------------------
def scrape_the_hindu(url: str) -> str:

    # Step 1: TRY SIMPLE REQUEST
    html = get_page_source_with_requests(url)

    # Step 2: IF FAILED → TRY PLAYWRIGHT
    if not html or len(html) < 500:
        html = get_page_source_with_playwright(url)

    if not html:
        return ""

    soup = BeautifulSoup(html, "html.parser")
    content = extract_the_hindu_content(soup)

    # Basic validation
    if not content or len(content.split()) < 80:
        return ""

    return content


# -----------------------------
# Standalone test
# -----------------------------
if __name__ == "__main__":
    url = "https://www.thehindu.com/business/Industry/bharti-airtel-to-approach-government-for-recalculation-of-agr-following-sc-order-on-vodafone-idea-vittal/article70240495.ece"
    print(scrape_the_hindu(url))
