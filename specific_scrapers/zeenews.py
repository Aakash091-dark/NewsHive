import requests
from bs4 import BeautifulSoup
import re
import json


def simple_request(url: str) -> str:
    print(f"[Simple Request] Fetching: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[Error] Simple request failed: {e}")
        return ""


def extract_from_json_ld(soup: BeautifulSoup) -> str:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string.strip())
            if isinstance(data, list):
                for obj in data:
                    if "articleBody" in obj:
                        return obj["articleBody"]
            elif "articleBody" in data:
                return data["articleBody"]
        except Exception:
            continue
    return ""


def scrape_zeenews(url: str) -> str:
    print(f"[Scraper] Fetching: {url}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Error] Request failed: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    selectors = [
        "div#contentData",
        "div.tpcst-content",
        "div.articleBody",
        "div.article-content",
        "div#storyContent",
        "section.main-content",
        "div[id*=content]",
        "section[id*=content]",
        "article",
    ]

    article = None
    for sel in selectors:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 50:
            article = node
            break

    if not article:
        print("[Info] Trying JSON-LD extraction...")
        json_body = extract_from_json_ld(soup)
        if json_body and len(json_body.split()) > 50:
            cleaned = json_body 
            print("[OK] Extracted content from JSON-LD.")
            return cleaned

        print("[Warning] No primary content block found.")
        return ""

    for tag in article.find_all(
        ["script", "style", "aside", "figure", "iframe", "footer", "noscript", "form"]
    ):
        tag.decompose()

    for div in article.find_all(True, class_=lambda c: c and re.search(r"ad|share|social|related|promo", c, re.I)):
        div.decompose()

    text_blocks = []
    for elem in article.find_all(["p", "h2", "h3", "span"]):
        text = elem.get_text(" ", strip=True)
        if not text:
            continue
        if re.search(r"(also\s+read|follow\s+us|watch\s+video|click\s+here)", text, re.I):
            continue
        if len(text.split()) > 4:
            text_blocks.append(text)

    content = " ".join(text_blocks).strip()
    cleaned_content = content 

    if len(cleaned_content.split()) < 50:
        print("[Warning] Extracted content too short or empty.")
        return ""

    return cleaned_content

# if __name__ == "__main__":
#     url = "https://zeenews.india.com/economy/cbdt-empowers-cpc-bengaluru-to-expedite-tax-rectifications-and-refunds-2982363.html"

#     html = simple_request(url)
#     print("\n--- Raw HTML snippet (simple request) ---\n")
#     print(html[:500])

#     content = scrape_zeenews(url)
#     print("\n--- Extracted Clean Content ---\n")
#     print(content)
