import asyncio
import re
import requests
import warnings
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)
from logs.json_log import log as logger


class PageNotFoundError(Exception):
    pass


class ScrapingSkippedException(Exception):
    pass


# ----------------------------------------------------------
#  SIMPLE REQUEST FIRST
# ----------------------------------------------------------

def simple_request_fetch(url: str) -> str:
    # Skip known binary extensions before even requesting
    if url.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar", ".exe", ".mp3", ".mp4")):
        return ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        # Stream the request to check headers first
        with requests.get(url, headers=headers, timeout=10, stream=True) as r:
            if r.status_code == 200:
                content_type = r.headers.get("Content-Type", "").lower()
                if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                    return ""
                
                # Check size limit (e.g., 5MB) to avoid memory issues
                if int(r.headers.get("Content-Length", 0)) > 5 * 1024 * 1024:
                    return ""

                content = r.text
                if len(content) > 500:
                    return content
    except:
        pass
    return ""


# ----------------------------------------------------------
#  PLAYWRIGHT MANAGER
# ----------------------------------------------------------

class PlaywrightManager:
    def __init__(self):
        self.browser = None
        self.playwright = None

    async def start(self):
        """Start Playwright & Chromium."""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ]
            )

    async def stop(self):
        """Clean shutdown."""
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")

        finally:
            if self.playwright:
                await self.playwright.stop()

            self.browser = None
            self.playwright = None

    async def get_page_content(
        self,
        url: str,
        timeout: int = 120000,
        block_resources=True
    ):
        """Load page & return HTML."""

        # Skip binary resources
        if url.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar")):
            raise ScrapingSkippedException(f"Non-HTML resource: {url}")

        # Ensure browser ready
        if not self.browser:
            await self.start()

        page, context = None, None

        try:
            context = await self.browser.new_context()

            # Block heavy assets
            if block_resources:
                await context.route(
                    "**/*",
                    lambda route, request: route.abort()
                    if request.resource_type in {"image", "font", "media"}
                    else route.continue_()
                )

            page = await context.new_page()

            response = await page.goto(
                url,
                timeout=timeout,
                wait_until="domcontentloaded"
            )

            if response and response.status == 404:
                raise PageNotFoundError(f"404 Not Found: {url}")

            # Try waiting for content
            try:
                await page.wait_for_selector("article, p", timeout=4000)
            except Exception:
                pass

            html = await page.content()
            return html

        except PlaywrightTimeoutError:
            logger.error(f"Timeout scraping {url}")
            return None

        except PlaywrightError as e:
            if "Download is starting" in str(e):
                raise ScrapingSkippedException(f"Download detected: {url}")
            logger.error(f"Playwright error scraping {url}: {e}")
            raise

        except Exception as e:
            logger.error(f"General scraping error for {url}: {e}")
            raise

        finally:
            try:
                if page and not page.is_closed():
                    await page.close()
                if context:
                    await context.close()
            except Exception as e:
                logger.warning(f"Failed closing page/context: {e}")


playwright_manager = PlaywrightManager()


# ----------------------------------------------------------
#  EXTRACTOR (GENERIC)
# ----------------------------------------------------------

def clean_content(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def extract_generic_content(html: str) -> str:
    if not html:
        return ""

    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup.select(
        "script, style, nav, footer, header, aside, .ad, .ads, "
        ".sponsored, .related, .share"
    ):
        tag.decompose()

    # Main selectors
    selectors = [
        "article",
        "main",
        "div.article-body",
        "div.story-content",
        "div.entry-content",
        "div.post-content",
        "div#content",
        "div.content",
    ]

    main_content = None
    for sel in selectors:
        element = soup.select_one(sel)
        if element:
            main_content = element
            break

    if not main_content:
        main_content = soup.body

    if not main_content:
        return ""

    parts = []
    for p in main_content.find_all("p"):
        text = p.get_text(strip=True)
        if len(text.split()) > 5:
            parts.append(text)

    return clean_content("\n\n".join(parts))

async def scrape_with_playwright(
    url: str,
    max_retries: int = 3,
    timeout: int = 120000
) -> str:
    
    if url.lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".gif", ".zip", ".rar", ".exe", ".mp3", ".mp4")):
        raise ScrapingSkippedException(f"Non-HTML resource: {url}")

    simple_html = await asyncio.to_thread(simple_request_fetch, url)
    if simple_html:
        content = extract_generic_content(simple_html)
        if content and len(content.split()) > 30:
            return content

    for attempt in range(1, max_retries + 1):

        try:
            html = await playwright_manager.get_page_content(url=url, timeout=timeout)

            if html:
                return extract_generic_content(html)

        except (ScrapingSkippedException, PageNotFoundError):
            raise

        except Exception as e:
            logger.error(f"Attempt {attempt}/{max_retries} failed for {url}: {e}")

            # If browser crashed → restart
            if "browser has been closed" in str(e) or "Connection closed" in str(e):
                await playwright_manager.stop()

            if attempt < max_retries:
                await asyncio.sleep(2)

    return ""
