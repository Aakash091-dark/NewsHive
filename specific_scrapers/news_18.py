import requests
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_news18(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    paras = soup.find_all(id=re.compile(r"story_para_\d+"))

    full_content = "\n".join(p.get_text(strip=False) for p in paras)

    if not full_content.strip():
        fallback = soup.find_all("p")
        full_content = "\n".join(p.get_text(strip=False) for p in fallback)

    return full_content

if __name__ == "__main__":
    print(scrape_news18("https://www.news18.com/tech/amazon-explains-why-it-is-late-in-the-ai-race-and-what-happens-to-alexa-now-9189307.html"))
