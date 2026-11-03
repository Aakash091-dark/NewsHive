from datetime import datetime
from typing import Optional, Dict, List
import json
import re
from logs.json_log import log
import requests
from bs4 import BeautifulSoup

def parse_iso_date(text: str):
    """Parse ISO format dates and return YYYY-MM-DD"""
    if not text:
        return None
    try:
        cleaned = text.replace("Z", "").replace("T", " ").split("+")[0].split(".")[0].strip()
        return datetime.fromisoformat(cleaned).strftime("%Y-%m-%d")
    except:
        return None


def parse_date_from_url(url: str) -> Optional[str]:
    """Enhanced URL date extraction with site-specific patterns"""
    if not url:
        return None
    
    # Site-specific patterns
    site_patterns = {
        'timesofindia.indiatimes.com': [
            # /articleshow/118215562.cms - extract from URL structure or article ID
            r'/articleshow/(\d+)\.cms',  # Will need to parse the article ID
        ],
        'freepressjournal.in': [
            # URLs don't have dates, will need scraping
        ],
        'economictimes.indiatimes.com': [
            # Similar to TOI
        ],
        'news18.com': [
            r'/news-(\d+)\.html',  # article ID
        ],
        'zeenews.india.com': [
            r'-(\d{7})\.html',  # article ID at end
        ],
        'livemint.com': [
            r'-(\d{13})\.html',  # timestamp in URL
        ],
    }
    
    # Generic patterns (try these first)
    generic_patterns = [
        # Standard formats: /2024/03/15/ or /2024-03-15/
        r'[/\-]+(20\d{2})[/\-]+(\d{1,2})[/\-]+(\d{1,2})[/\-]+',
        # Compact: /20240315/
        r'[/\-]+(20\d{2})(\d{2})(\d{2})[/\-]+',
        # Story format: story-2024-08-20 or 2024-08-20-story
        r'[\-/](20\d{2})[\-/](\d{1,2})[\-/](\d{1,2})',
        # Reversed: /15/03/2024/
        r'[/\-]+(\d{1,2})[/\-]+(\d{1,2})[/\-]+(20\d{2})[/\-]+',
        # In filename: 20241223061858_ (timestamp format)
        r'(20\d{2})(\d{2})(\d{2})\d{6}',
        # Separated by underscores: 2024_03_15
        r'[\-_/](20\d{2})[\-_](\d{2})[\-_](\d{2})',
    ]
    
    all_patterns = generic_patterns
    
    for pattern in all_patterns:
        try:
            m = re.search(pattern, url)
            if m:
                groups = m.groups()
                
                # Determine if year is first or last
                if len(groups[0]) == 4:  # Year first
                    y, m_, d = groups
                elif len(groups[2]) == 4:  # Year last
                    d, m_, y = groups
                else:
                    continue
                
                month = int(m_)
                day = int(d)
                
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return f"{y}-{month:02d}-{day:02d}"
        except (ValueError, IndexError):
            continue
    
    return None


def extract_date_from_text(text: str) -> Optional[str]:
    """Enhanced text date extraction with more patterns"""
    if not text:
        return None

    months = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12
    }

    patterns = [
        # "June 26, 2024" or "Jun 26, 2024"
        r'([A-Za-z]+)\s+(\d{1,2}),?\s+(20\d{2})',
        # "26 June 2024" or "26 Jun 2024"
        r'(\d{1,2})\s+([A-Za-z]+),?\s+(20\d{2})',
        # ISO format: "2024-06-26"
        r'(20\d{2})[-/\.](\d{1,2})[-/\.](\d{1,2})',
        # "26/06/2024" or "26.06.2024"
        r'(\d{1,2})[-/\.](\d{1,2})[-/\.](20\d{2})',
        # "Updated: Jun 26, 2024" or "Published: Jun 26, 2024"
        r'(?:updated|published|posted|date)[\s:]+([A-Za-z]+)\s+(\d{1,2}),?\s+(20\d{2})',
        # "2024, June 26"
        r'(20\d{2}),?\s+([A-Za-z]+)\s+(\d{1,2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                groups = match.groups()
                
                g1, g2, g3 = groups

                if g1.isalpha():
                    month = months.get(g1.lower())
                    if not month:
                        continue
                    day = int(g2)
                    year = int(g3)
                elif g2.isalpha():
                    day = int(g1)
                    month = months.get(g2.lower())
                    if not month:
                        continue
                    year = int(g3)
                else:
                    if len(g1) == 4:
                        year = int(g1)
                        month = int(g2)
                        day = int(g3)
                    else:
                        day = int(g1)
                        month = int(g2)
                        year = int(g3)

                if 1 <= month <= 12 and 1 <= day <= 31 and 2000 <= year <= 2030:
                    return f"{year}-{month:02d}-{day:02d}"

            except (ValueError, AttributeError):
                continue

    return None


def scrape_date_from_page(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch actual page and extract date from HTML"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try meta tags first
        date_meta_tags = [
            'article:published_time', 'datePublished', 'publishdate',
            'date', 'og:published_time', 'publish_date', 'pubdate',
            'article.published', 'publish-date'
        ]
        
        for tag_name in date_meta_tags:
            tag = soup.find('meta', property=tag_name) or soup.find('meta', {'name': tag_name})
            if tag and tag.get('content'):
                date = parse_iso_date(tag.get('content'))
                if date:
                    return date
        
        # Try structured data (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    for field in ['datePublished', 'dateCreated', 'uploadDate']:
                        if data.get(field):
                            date = parse_iso_date(data.get(field))
                            if date:
                                return date
            except:
                continue
        
        # Try common date classes/IDs in HTML
        date_selectors = [
            {'class': 'publish-date'}, {'class': 'article-date'},
            {'class': 'post-date'}, {'class': 'entry-date'},
            {'id': 'publish-date'}, {'itemprop': 'datePublished'},
            {'class': 'story-date'}, {'class': 'date'},
        ]
        
        for selector in date_selectors:
            element = soup.find(attrs=selector)
            if element:
                text = element.get_text()
                date = extract_date_from_text(text)
                if date:
                    return date
        
        # Try searching in first 2000 characters of text
        page_text = soup.get_text()[:2000]
        date = extract_date_from_text(page_text)
        if date:
            return date
            
    except Exception as e:
        log.debug(f"Failed to scrape date from {url}: {e}")
    
    return None


def extract_snippets_text(data: Dict) -> List[str]:
    """Extract snippet text from snippets field"""
    snippets = []
    
    # Try getting snippets from the 'snippets' field
    snippets_field = data.get("snippets", [])
    if isinstance(snippets_field, list):
        for snippet_item in snippets_field:
            if isinstance(snippet_item, dict):
                snippet_text = snippet_item.get("snippet")
                if snippet_text:
                    snippets.append(snippet_text)
                
                html_snippet = snippet_item.get("htmlSnippet")
                if html_snippet:
                    clean_snippet = re.sub(r'<[^>]+>', '', html_snippet)
                    if clean_snippet and clean_snippet not in snippets:
                        snippets.append(clean_snippet)
    
    # Also check direct 'snippet' field (singular)
    if data.get("snippet"):
        snippet_text = data.get("snippet")
        if snippet_text not in snippets:
            snippets.append(snippet_text)
    
    # Check htmlSnippet field directly
    if data.get("htmlSnippet"):
        clean_snippet = re.sub(r'<[^>]+>', '', data.get("htmlSnippet"))
        if clean_snippet and clean_snippet not in snippets:
            snippets.append(clean_snippet)
    
    return snippets


def extract_comprehensive_description(data: Dict, pagemap: Dict, snippets: List[str]) -> str:
    """Extract description from all possible sources"""
    descriptions = []
    
    # Direct description field
    if data.get("description"):
        descriptions.append(data.get("description"))
    
    # Snippets (high priority - often most accurate)
    for snippet in snippets:
        if snippet and snippet not in descriptions:
            descriptions.append(snippet)
    
    # Meta tags
    metatags = pagemap.get("metatags", [])
    if metatags and len(metatags) > 0:
        tags = metatags[0]
        desc_fields = [
            "og:description",
            "twitter:description",
            "description",
            "dc.description",
            "summary",
        ]
        for field in desc_fields:
            val = tags.get(field)
            if val and val not in descriptions:
                descriptions.append(val)
    
    # Return longest non-empty description
    descriptions = [d.strip() for d in descriptions if d and len(d.strip()) > 10]
    return max(descriptions, key=len) if descriptions else None


def extract_comprehensive_date(
    data: Dict, 
    pagemap: Dict, 
    link: str, 
    snippets: List[str], 
    title: str = None, 
    debug: bool = False,
    enable_scraping: bool = True
) -> Optional[str]:
    """Enhanced date extraction from all available sources with web scraping fallback"""
    
    if debug:
        log.info(f"=== DEBUG DATE EXTRACTION ===")
        log.info(f"Link: {link}")
        log.info(f"Snippets count: {len(snippets)}")
    
    # Priority 1: Check all text content (snippets, descriptions, etc.)
    text_sources = []
    
    # Add snippets
    if snippets:
        text_sources.extend(snippets)
    
    # Add various description fields
    if data.get("snippet"):
        text_sources.append(data.get("snippet"))
    
    if data.get("htmlSnippet"):
        clean = re.sub(r'<[^>]+>', '', data.get("htmlSnippet"))
        text_sources.append(clean)
    
    if data.get("description"):
        text_sources.append(data.get("description"))
    
    # Check all text sources for dates
    for text in text_sources:
        if text:
            date = extract_date_from_text(text)
            if date:
                if debug:
                    log.info(f"✓ Date found in text content: {date}")
                return date
    
    # Priority 2: Metatags (comprehensive list)
    metatags = pagemap.get("metatags", [])
    if metatags and len(metatags) > 0:
        tags = metatags[0]
        
        if debug:
            log.info(f"Metatag keys: {list(tags.keys())}")
        
        # Comprehensive date field list
        date_fields = [
            'article:published_time', 'datePublished', 'publish_date', 
            'publishdate', 'pubdate', 'date', 'og:published_time',
            'publish-date', 'last-modified-time', 'article.published',
            'article.created', 'created-date', 'og:article:published_time',
            'updated_date', 'dateModified', 'article:modified_time',
            'modified-date', 'last-modified-date', 'lastmod',
        ]
        
        for field in date_fields:
            val = tags.get(field)
            if val:
                parsed = parse_iso_date(str(val))
                if parsed:
                    if debug:
                        log.info(f"✓ Date found in metatag '{field}': {parsed}")
                    return parsed
        
        # Check all keys for date-related content
        for k, v in tags.items():
            if any(keyword in k.lower() for keyword in ['date', 'time', 'publish', 'created', 'modified']):
                parsed = parse_iso_date(str(v))
                if parsed:
                    if debug:
                        log.info(f"✓ Date found in metatag '{k}': {parsed}")
                    return parsed
    
    # Priority 3: JSON-LD in pagemap
    jsonld = pagemap.get("jsonld", [])
    if jsonld:
        for item in jsonld:
            if isinstance(item, dict):
                date_fields = ['datePublished', 'dateCreated', 'dateModified', 'uploadDate', 'date']
                for field in date_fields:
                    val = item.get(field)
                    if val:
                        parsed = parse_iso_date(str(val))
                        if parsed:
                            if debug:
                                log.info(f"✓ Date found in JSON-LD '{field}': {parsed}")
                            return parsed
    
    # Priority 4: NewsArticle in pagemap
    newsarticle = pagemap.get("newsarticle", [])
    if newsarticle:
        for item in newsarticle:
            if isinstance(item, dict):
                date_fields = ['datepublished', 'datecreated', 'datemodified']
                for field in date_fields:
                    val = item.get(field)
                    if val:
                        parsed = parse_iso_date(str(val))
                        if parsed:
                            if debug:
                                log.info(f"✓ Date found in newsarticle '{field}': {parsed}")
                            return parsed
    
    # Priority 5: Enhanced URL parsing
    url_date = parse_date_from_url(link or "")
    if url_date:
        if debug:
            log.info(f"✓ Date found in URL: {url_date}")
        return url_date
    
    # Priority 6: Direct data fields
    direct_date_fields = ['publishDate', 'publishdate', 'date', 'datePublished']
    for field in direct_date_fields:
        val = data.get(field)
        if val:
            parsed = parse_iso_date(str(val))
            if parsed:
                if debug:
                    log.info(f"✓ Date found in data.{field}: {parsed}")
                return parsed
    
    # Priority 7: Title
    if title:
        date = extract_date_from_text(title)
        if date:
            if debug:
                log.info(f"✓ Date found in title: {date}")
            return date
    
    # Priority 8: HTML title field
    html_title = data.get("htmlTitle")
    if html_title:
        clean_title = re.sub(r'<[^>]+>', '', html_title)
        date = extract_date_from_text(clean_title)
        if date:
            if debug:
                log.info(f"✓ Date found in htmlTitle: {date}")
            return date
    
    # Priority 9: Web scraping fallback (LAST RESORT)
    if enable_scraping and link:
        if debug:
            log.info(f"Attempting to scrape date from page...")
        scraped_date = scrape_date_from_page(link)
        if scraped_date:
            if debug:
                log.info(f"✓ Date scraped from page: {scraped_date}")
            return scraped_date
    
    if debug:
        log.info(f"✗ No date found anywhere")
    
    return None