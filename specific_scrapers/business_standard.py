import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_business_standard(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    container = soup.find(id="between_article_content-1-0")
    if container:
        full_content = container.get_text(separator="\n", strip=False)
    else:
        full_content = soup.get_text(separator="\n", strip=False)
    return full_content

if __name__ == "__main__":
    test_url ="https://www.business-standard.com/india-news/vaishnaw-inspects-bullet-train-track-slab-manufacturing-factory-in-gujarat-124113000549_1.html"
    print(scrape_business_standard(test_url))