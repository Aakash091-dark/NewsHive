import requests
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def extract_from_soup(soup: BeautifulSoup) -> str:
    selectors = [
        "div.textwrap p",
        "div[data-module='ArticleBody'] p",
        ".story-content p",
        ".article-content p",
        ".mainSectionHolder p",
        "article p",
        "section p",
        "div.txt-holder p",          # LiveMint fallback
        "div[id='mainArea'] p",      # LiveMint fallback
    ]

    paragraphs, seen = [], set()

    for selector in selectors:
        for tag in soup.select(selector):
            text = tag.get_text(strip=True)
            text = re.sub(r"\s+", " ", text)

            if text and len(text) > 30 and text not in seen:
                paragraphs.append(text)
                seen.add(text)

    return "\n\n".join(paragraphs).strip()


def simple_request_fetch(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)

        # Some pages return JS shell → skip early
        if "enable-javascript" in resp.text.lower():
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")
        return extract_from_soup(soup)

    except Exception:
        return ""


def playwright_fetch(url: str) -> str:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1366, "height": 768},
            )

            # Stealth patch
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """)

            page = context.new_page()

            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1500)

            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        return extract_from_soup(soup)

    except Exception:
        return ""


def scrape_livemint(url: str) -> str:
    # 1️⃣ First attempt → simple HTML request
    content_simple = simple_request_fetch(url)

    if len(content_simple.split()) > 80:
        return content_simple

    # 2️⃣ Fallback → Playwright stealth render
    content_pw = playwright_fetch(url)

    # Return whichever is longer
    return content_pw if len(content_pw.split()) > len(content_simple.split()) else content_simple


# Example usage
if __name__ == "__main__":
    test_url = "https://www.livemint.com/companies/people/investbae-nippon-india-mutual-fund-kaiyomurz-daver-passive-advertising-gen-z-slang-brand-identity-atms-hnis-epfo-lic-sip-11762430879387.html"
    article_text = scrape_livemint(test_url)
    print(article_text)
