from bs4 import BeautifulSoup
import re

def scrape_etnow(soup: BeautifulSoup) -> str:
    possible_selectors = [
        'div.story-content',
        'div.article-body',
        'div#storyContent',
        'div#contentData',
        'div.story-container',
        'article'
    ]

    story_content = None
    for selector in possible_selectors:
        story_content = soup.select_one(selector)
        if story_content:
            break

    if not story_content:
        print("[Warning] No primary content block found.")
        return ""

    for tag in story_content.find_all([
        'script', 'style', 'aside', 'figure', 'iframe', 'noscript', 
        'footer', 'form', 'button', 'ul', 'ol', 'video', 'nav'
    ]):
        tag.decompose()

    unwanted_classes = [
        'ad-container', 'social-share-buttons', 'related-articles', 
        'share-bar', 'subscribe', 'newsletter', 'comments', 
        'storyTags', 'comment-section', 'top-stories', 'article-tags'
    ]
    for unwanted in story_content.find_all(True, class_=lambda c: c and any(u in c for u in unwanted_classes)):
        unwanted.decompose()

    text_blocks = []
    for elem in story_content.find_all(['p', 'h2', 'h3']):
        txt = elem.get_text(" ", strip=True)
        if txt and '.' in txt and len(txt.split()) > 5:
            text_blocks.append(txt)

    content = " ".join(text_blocks).strip()

    if not content:
        content = story_content.get_text(" ", strip=True)

    content = re.sub(r'#\S+', '', content)
    content = re.sub(r'@\S+', '', content)
    content = re.sub(r'(?i)(add your comment|write a comment|leave a comment).*', '', content)

    content = re.sub(r'\s+', ' ', content).strip()
    return content

# if __name__ == "__main__":
#     test_url = "https://www.etnownews.com/markets/sensex-today-stock-market-live-updates-10-november-2025-sensex-nifty-movement-top-gainers-losers-sectoral-trends-liveblog-153126039"
#     scrape_etnow(test_url)
