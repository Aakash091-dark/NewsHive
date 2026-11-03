from bs4 import BeautifulSoup
from typing import Optional
from logs.json_log import log as logger

def extract_content_with_fallback(
    soup: BeautifulSoup, selectors: list, site_name: str = ""
) -> Optional[str]:
    if not soup:
        return None

    # 1. Preferred selectors
    for selector in selectors:
        try:
            content = soup.select_one(selector)
            if content:
                text = content.get_text(strip=True, separator=" ")
                text = text.strip()
                if (
                    len(text) >= 10
                    and "not found" not in text.lower()
                    and "404" not in text.lower()
                    and "please enable javascript" not in text.lower()
                ):
                    return text
        except Exception as e:
            logger.debug(f"Selector '{selector}' failed: {e}")

    try:
        paragraphs = soup.find_all("p")
        cleaned = []
        for p in paragraphs:
            txt = p.get_text(strip=True)
            if len(txt) >= 10 and not txt.lower().startswith("read also"):
                cleaned.append(txt)
        text = " ".join(cleaned)
        if (
            len(text) >= 10
            and "content not found" not in text.lower()
            and "404" not in text.lower()
            and "please enable javascript" not in text.lower()
        ):

            return text
    except Exception as e:
        logger.error(f"Paragraph aggregation failed for {site_name}: {e}")

    for tag in ["article", "main"]:
        try:
            tag_obj = soup.find(tag)
            if tag_obj:
                text = tag_obj.get_text(strip=True, separator=" ")
                text = text.strip()
                if len(text) >= 10:
                    return text
        except Exception as e:
            logger.debug(f"Failed to extract from {tag}: {e}")

    try:
        blocks = soup.find_all(['div', 'section'])
        largest = None
        for block in blocks:
            txt = block.get_text(separator=" ", strip=True)
            if not largest or len(txt) > len(largest):
                largest = txt
        if largest and len(largest) >= 30:
            return largest
    except Exception as e:
        logger.debug(f"Largest block extraction failed: {e}")

    try:
        for level in range(1, 4): 
            for h in soup.find_all(f'h{level}'):
                heading = h.get_text(separator=" ", strip=True)
                next_paras = []
                sib = h.find_next_sibling()
                while sib and sib.name == 'p':
                    txt = sib.get_text(strip=True)
                    if len(txt) >= 10:
                        next_paras.append(txt)
                    sib = sib.find_next_sibling()
                if heading and next_paras:
                    result = heading + " " + " ".join(next_paras)
                    if len(result) > 40:
                        return result
    except Exception as e:
        logger.debug(f"Heading + sibling paragraphs failed: {e}")

    try:
        lists = soup.find_all(['ul', 'ol'])
        for l in lists:
            items = [li.get_text(separator=" ", strip=True) for li in l.find_all('li')]
            content = " ".join(items)
            if len(content) > 55 and len(items) >= 3:
                return content
    except Exception as e:
        logger.debug(f"List extraction failed: {e}")

    try:
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content") and len(og_desc["content"].strip()) > 20:
            return og_desc["content"].strip()
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content") and len(meta_desc["content"].strip()) > 20:
            return meta_desc["content"].strip()
    except Exception as e:
        logger.debug(f"Meta extraction failed: {e}")
        
    return None
