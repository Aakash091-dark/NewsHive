from dotenv import load_dotenv
from config.bossenv import load_aws_secrets
load_dotenv()
load_aws_secrets()
import time
import asyncio
import atexit
from web_scrapping.scrap_specific_04 import rss_websites
from DATABASE.create import build_DB
from processing.process_rss import process_rss_source
from web_scrapping.scarping_03 import ScraperManager
from web_scrapping.playwright_scraper import playwright_manager
from DATABASE.fetch import get_all_search_terms
from fetch.google_search import run_search_and_save
from tor.tor_session_manager import tor_session_manager
from processing.processing_flow import process_scraped_data
from DATABASE.INSERT.reports import insert_scraping_report
from processing.search_term_tracker import is_search_term_processed, mark_search_term_processed
from logs.json_log import log

DELAY = 60

async def main():
    atexit.register(tor_session_manager.close_session)

    if not tor_session_manager.get_session():
        log.critical("❌ Tor session failed. Exiting.")
        return

    await playwright_manager.start()
    scraper_manager = ScraperManager()

    cycle = 1
    rss_sources = list(rss_websites.items())

    while True:
        try:
            log.info(f"🚀 Starting cycle {cycle}")

            build_DB()

            search_terms = get_all_search_terms()
            if not search_terms:
                log.warning("⚠ No search terms found. Sleeping and retrying...")
                time.sleep(DELAY)
                continue

            for search_term in search_terms:
                if is_search_term_processed(search_term):
                    log.info(f"Skipping already processed search term: {search_term}")
                    continue

                log.info(f"Running Google search for: {search_term}")

                google_urls_count = 0

                google_data = run_search_and_save(
                        query = search_term
                )

                if google_data and "results" in google_data:
                    articles = [
                        article for article in google_data["results"]
                        if article.get("link")
                    ]
                    google_urls_count = len(articles)

                    if articles:
                        start_time = time.time()

                        await scraper_manager.scrape(
                            articles,
                            search_term,
                            "google"
                        )

                        scraper_manager.save_results()
                        scraped_data = scraper_manager.get_results()

                        scraped_urls = [
                            item.get("url") for item in scraped_data if item.get("url")
                        ]

                        failed_articles = scraper_manager.get_failed_articles()
                        duplicate_articles = scraper_manager.get_duplicate_articles()

                        total_duplicate_links = len(duplicate_articles)
                        duplicate_urls = [item.get("url") for item in duplicate_articles]

                        total_links_failed = len(failed_articles)

                        if scraped_data:
                            tasks = [process_scraped_data(data) for data in scraped_data]
                            await asyncio.gather(*tasks)

                        end_time = time.time()
                        processing_time = end_time - start_time

                        insert_scraping_report(
                            source_identifier=search_term,
                            source_type="google_search",
                            total_links_found=google_urls_count,
                            total_links_scraped=len(scraped_data) if scraped_data else 0,
                            scraped_urls=scraped_urls,
                            total_duplicate_links=total_duplicate_links,
                            duplicate_urls=duplicate_urls,
                            total_links_failed=total_links_failed,
                            reason={"failed_articles": failed_articles},
                            processing_time=processing_time
                        )
                
                mark_search_term_processed(search_term)
                scraper_manager.reset_state()

            if rss_sources:
                for rss_name, rss_url in rss_sources:
                    log.info(f"Processing RSS source: {rss_name}")
                    await process_rss_source(rss_name, rss_url)

            log.info(f"✅ Cycle {cycle} completed. Sleeping {DELAY} seconds...")
            time.sleep(DELAY)

            cycle += 1

        except KeyboardInterrupt:
            log.warning("🛑 Stopped by user.")
            break

        except Exception as e:
            log.critical(
                f"💥 Error in cycle {cycle}: {e}",
                extra={"error": str(e)},
            )
            time.sleep(DELAY)

    if scraper_manager.active_tasks:
        log.info(f"Waiting for {len(scraper_manager.active_tasks)} active tasks to finish...")
        await asyncio.gather(
            *scraper_manager.active_tasks,
            return_exceptions=True,
        )
    await playwright_manager.stop()
    log.info("🧹 Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.warning("🛑 Exited manually.")
    except Exception as e:
        log.critical(f"💥 Fatal error: {e}", extra={"error": str(e)})
