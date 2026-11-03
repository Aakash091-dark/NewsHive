from logs.json_log import log as logger
import os
import json
import time
from web_scrapping.scrap_specific_04 import rss_functions
from web_scrapping.scarping_03 import ScraperManager
from processing.processing_flow import process_scraped_data
from DATABASE.INSERT.reports import insert_scraping_report
import asyncio

async def process_rss_source(key, value):
    logger.info(f"Starting RSS processing for source: {key}")
    try:
        parts = key.split("_")
        if len(parts) < 2:
            full_name = source = source_category = key
        else:
            full_name = key
            source, source_category = parts[0], parts[1]

        json_file = os.path.join("data", f"{full_name}.json")
        csv_file = os.path.join("data", f"{full_name}.csv")

        rss_function = rss_functions.get(full_name, rss_functions.get("all_rss"))

        new_count = rss_function(
            rss_url=value,
            json_file=json_file,
            csv_file=csv_file,
            source=source,
            source_category=source_category,
        )

        if not os.path.exists(json_file):
            logger.warning(f"JSON file not found for source: {full_name}")
            return 0

        if new_count > 0:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load JSON for {full_name}: {e}")
                return new_count

            if not isinstance(json_data, list):
                logger.warning(f"Unexpected JSON structure in {json_file}")
                return new_count

            items_to_process = json_data[-new_count:]
            items_with_links = [item for item in items_to_process if item.get("link")]

            if items_with_links:
                logger.info(f"Scraping {len(items_with_links)} new articles for {full_name}...")
                scraper_manager = ScraperManager()
                
                start_time = time.time()
                await scraper_manager.scrape(items_with_links, source_category, "rss")
                scraped_results = scraper_manager.get_results()

                scraped_urls = [item.get("url") for item in scraped_results if item.get("url")]

                failed_articles = scraper_manager.get_failed_articles()
                duplicate_articles = scraper_manager.get_duplicate_articles()

                total_duplicate_links = len(duplicate_articles)
                duplicate_urls = [item.get("url") for item in duplicate_articles]

                total_links_failed = len(failed_articles)

                if scraped_results:
                    logger.info(f"Processing {len(scraped_results)} scraped articles...")
                    tasks = [process_scraped_data(data) for data in scraped_results]
                    await asyncio.gather(*tasks)
                    logger.info(f"Finished processing scraped articles for {full_name}.")
                else:
                    logger.warning(f"No content scraped for {full_name}.")
                
                end_time = time.time()
                processing_time = end_time - start_time

                insert_scraping_report(
                    source_identifier=full_name,
                    source_type="rss",
                    total_links_found=len(items_with_links),
                    total_links_scraped=len(scraped_results),
                    scraped_urls=scraped_urls,
                    total_duplicate_links=total_duplicate_links,
                    duplicate_urls=duplicate_urls,
                    total_links_failed=total_links_failed,
                    reason={"failed_articles": failed_articles},
                    processing_time=processing_time
                )
            else:
                logger.info(f"No valid URLs found in new items for {full_name}.")

        logger.info(f"Finished processing RSS source: {key}")
        return new_count

    except Exception as e:
        logger.error(f"Error processing RSS source {key}: {e}")
        return 0
