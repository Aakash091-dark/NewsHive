import requests
from bs4 import BeautifulSoup

def scrape_indian_express(url: str) -> str:
    print(f"[INFO] Fetching URL via requests: {url}")
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    possible_selectors = [
        'div.full-details',           
        'div.native_story',           
        'div.story_details',          
        'div.article_body',           
        'section.fullDetails',        
    ]

    article_body = None
    for selector in possible_selectors:
        article_body = soup.select_one(selector)
        if article_body:
            break

    if not article_body:
        article_body = soup.find('article')

    if not article_body:
        return ""


    for tag in article_body.find_all([
        'script', 'style', 'aside', 'figure', 'iframe',
        'noscript', 'footer', 'form', 'button', 'ul', 'ol'
    ]):
        tag.decompose()

    unwanted_classes = [
        'ad-container', 'social-share-buttons', 'related-articles',
        'share-bar', 'subscribe', 'newsletter', 'storyTags',
        'top-stories', 'express-ads', 'more-from-section', 'read-also'
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


# if __name__ == "__main__":
#     test_url = "https://indianexpress.com/article/business/rbi-monetary-policy-meet-live-updates-mpc-repo-rate-cut-gst-10281510/"
#     article = scrape_indian_express(test_url)

#     print("\n========== 📰 EXTRACTED ARTICLE ==========\n")
#     print(article[:3000])
#     print("\n==========================================")
