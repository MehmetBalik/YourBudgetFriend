# -*- coding: utf-8 -*-
"""
This script is the main entry point for the YourBudgetFriend web crawler.

It orchestrates the crawling process by:
- Initializing the environment.
- Reading site configurations.
- Calling the crawler for each site.
- Aggregating the data.
- Saving the data to a JSON file for the UI and creating a log.
"""

import os
import json
from datetime import datetime
from crawler import crawl_site
from config import SITE_CONFIGS
from utils import save_json

if __name__ == "__main__":
    # Ensure the 'logs' directory exists.
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Maximum number of pages to crawl per site.
    MAX_PAGES_PER_SITE = 10

    all_collected_products = []

    # Iterate through all configured sites and crawl them.
    for site_name, config in SITE_CONFIGS.items():
        print(f"Starting crawler for {site_name}...")
        collected_products = crawl_site(config, max_pages=MAX_PAGES_PER_SITE)

        if collected_products:
            all_collected_products.extend(collected_products)
            print(f"Collected {len(collected_products)} products from {site_name}.")
        else:
            print(f"No products were extracted during the crawl for {site_name}.")
        
        print(f"Crawl for {site_name} completed!\n")

    # Save the collected products to a JSON file for the UI.
    output_path = os.path.join("crawler", "UI", "clothing_data.json")
    if all_collected_products:
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_to_save = {
            "lastUpdated": current_timestamp,
            "products": all_collected_products
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(all_collected_products)} products to {output_path} with timestamp {current_timestamp}")

        # Save a timestamped log of the crawl.
        save_json(all_collected_products, file_prefix="logs")
    else:
        print("No products were extracted from any site.")

    print("All crawls completed!")
