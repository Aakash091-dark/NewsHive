import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_free_press_journal(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    article = soup.find("article", id="fp-article")

    if article:
        paragraphs = article.find_all("p")
        full_content = "\n".join(p.get_text(strip=False) for p in paragraphs)
    else:
        paragraphs = soup.find_all("p")
        full_content = "\n".join(p.get_text(strip=False) for p in paragraphs)

    return full_content

if __name__ == "__main__":
    print(scrape_free_press_journal("https://www.freepressjournal.in/business/dallas-venture-capital-llc-announces-closing-of-80-mn-early-stage-b2b-saas-fund-ii-in-us"))
