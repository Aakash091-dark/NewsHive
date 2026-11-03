import requests
from bs4 import BeautifulSoup
import re

def scrape_hindustan_times(soup: BeautifulSoup) -> str:
    possible_selectors = [
        'div.storyDetails',              
        'div.storyDetail',                
        'div.articleBody',                
        'div#storyContent',              
        'article',                       
    ]

    story_container = None
    for selector in possible_selectors:
        story_container = soup.select_one(selector)
        if story_container:
            break

    if not story_container:
        print("[Warning] No primary content block found.")
        return ""

    for tag in story_container.find_all(
        ['script', 'style', 'aside', 'figure', 'iframe', 'noscript',
         'footer', 'form', 'button', 'ul', 'section']
    ):
        tag.decompose()

    unwanted_classes = [
        'adv-cont', 'social-media', 'related-topics', 'ht-related-news',
        'ad-container', 'share-bar', 'subscribe', 'newsletter',
        'storyTags', 'trending-box', 'top-stories', 'comments'
    ]

    for unwanted in story_container.find_all(True, class_=lambda c: c and any(u in c for u in unwanted_classes)):
        unwanted.decompose()

    text_elements = []
    for elem in story_container.find_all(['p', 'h2', 'h3']):
        txt = elem.get_text(" ", strip=True)
        if txt and len(txt.split()) > 3 and not txt.startswith("#"):
            text_elements.append(txt)

    content = " ".join(text_elements).strip()

    if not content or len(content) < 100:
        content = story_container.get_text(" ", strip=True)

    content = re.sub(r'#\S+', '', content)     
    content = re.sub(r'@\S+', '', content)      
    content = re.sub(r'(?i)(add your comment|write a comment|leave a comment).*', '', content)
    content = re.sub(r'\s+', ' ', content).strip()

    return content


def simple_request(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        )
    }

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

# if __name__ == "__main__":
#     url = "https://www.hindustantimes.com/business/lenskart-share-price-drops-over-10-below-ipo-price-in-tepid-listing-over-valuation-concerns-101762748005434.html"

#     soup = simple_request(url)
#     print(f"[Scraper] Fetching: {url}")
#     content = scrape_hindustan_times(soup)

#     print("\n--- Extracted Clean Content ---\n")
#     print(content if content else "[No meaningful content extracted]")
