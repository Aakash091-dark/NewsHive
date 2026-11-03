import requests
from bs4 import BeautifulSoup
import json

def scrape_economic_times(url: str) -> str:
    print(f"[INFO] Fetching URL via requests: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    possible_selectors = [
        'div.article-body',
        'div.artText',
        'section.article-content',
        'div#content',
        'section.container-mid.article-section',
        'div.storyDetails',
        'div.stryMain',
        'div#articleContent',
        'div.articleSection',
    ]

    article_body = None
    for selector in possible_selectors:
        article_body = soup.select_one(selector)
        if article_body:
            break

    if article_body and article_body.has_attr("data-news"):
        try:
            data_news = json.loads(article_body["data-news"])
            if "body" in data_news and data_news["body"]:
                inner_html = data_news["body"]
                inner_soup = BeautifulSoup(inner_html, "html.parser")
                article_body = inner_soup
        except Exception:
            pass

    if not article_body:
        article_body = soup.find("article")
    if not article_body:
        article_body = soup.find("div", {"class": lambda c: c and "article" in c})

    if not article_body:
        return ""

    for tag in article_body.find_all([
        'script', 'style', 'aside', 'figure', 'iframe', 'noscript',
        'footer', 'form', 'button', 'ul', 'ol', 'header', 'nav'
    ]):
        tag.decompose()

    unwanted_classes = [
        'ad-container', 'social-share-buttons', 'related-articles',
        'share-bar', 'subscribe', 'newsletter', 'article__related',
        'liveblog-updates', 'storyTags', 'top-stories', 'adblock',
        'paywall', 'moreFromSection', 'comments'
    ]

    for unwanted in article_body.find_all(True, class_=lambda c: c and any(u in c for u in unwanted_classes)):
        unwanted.decompose()

    text_elements = []
    for elem in article_body.find_all(['p', 'h2', 'h3']):
        txt = elem.get_text(" ", strip=True)
        if txt and len(txt.split()) > 3:
            text_elements.append(txt)

    content = " ".join(text_elements).strip()

    if not content:
        content = article_body.get_text(" ", strip=True)

    return content

if __name__ == "__main__":
    test_url = "https://cfo.economictimes.indiatimes.com/news/economy/resilient-msmes-in-india-insights-from-the-sidbi-outlook-survey/124846777"
    article = scrape_economic_times(test_url)

    print("\n========== 📰 EXTRACTED ARTICLE ==========\n")
    print(article[:3000])  # limit for readability
    print("\n==========================================")
