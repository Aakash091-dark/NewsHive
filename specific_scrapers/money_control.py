import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_moneycontrol(url: str) -> dict:
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    container = soup.find("div", id="contentdata")

    if container:
        paragraphs = container.find_all("p")
        full_content = "\n".join(p.get_text(strip=False) for p in paragraphs)
    else:
        paragraphs = soup.find_all("p")
        full_content = "\n".join(p.get_text(strip=False) for p in paragraphs)
        
    return full_content

if __name__ == "__main__":
    print(scrape_moneycontrol("https://www.moneycontrol.com/india/stockpricequote/computers-software-mediumsmall/b2bsoftwaretechnologies/RFS"))
