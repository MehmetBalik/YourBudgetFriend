# -*- coding: utf-8 -*-
"""
This module handles the core web crawling logic for YourBudgetFriend.

It includes functionality for:
- Checking and respecting `robots.txt` rules.
- Making polite HTTP requests with delays.
- Crawling multi-page websites and handling pagination.
- Orchestrating the parsing of product data from HTML content.
"""

import requests
import time
import random
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from parser import parse_products

USER_AGENT = "YourBudgetFriendBot/2.0 (CCSU Project for Computer Science Class) Academic-Polite-Crawler"

def check_robots_txt(base_url):
    """
    Checks the robots.txt file for the given base_url.
    Returns a RobotFileParser object.
    """
    rp = RobotFileParser()
    rp.set_url(urljoin(base_url, "/robots.txt"))
    try:
        rp.read()
    except Exception as e:
        print(f"Error reading robots.txt for {base_url}: {e}")
        return None
    return rp

def polite_request(url, robot_parser):
    """
    Fetches HTML content from a URL with a polite delay, respecting robots.txt rules.
    """
    # Check if crawling is allowed by robots.txt
    if robot_parser and not robot_parser.can_fetch(USER_AGENT, url):
        print(f"Robots.txt disallows crawling of {url}")
        return None

    headers = {"User-Agent": USER_AGENT}
    try:
        print(f"Attempting to fetch: {url}")
        # Introduce a random delay to be polite to the server
        time.sleep(random.uniform(1.5, 3.5))
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Successfully fetched HTML from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def crawl_site(config, max_pages=10):
    """
    Crawls a multi-page site using a specific configuration, with an optional page limit.
    """
    all_products = []
    base_url = config["base_url"]
    start_url = urljoin(base_url, config["start_path"])
    current_page_url = start_url
    page_count = 0

    # Initialize robots.txt parser for the site
    robot_parser = check_robots_txt(base_url)
    if not robot_parser:
        print(f"Could not read robots.txt for {base_url}. Abandoning crawl for this site.")
        return []

    while current_page_url:
        page_count += 1
        
        # Stop if the maximum page limit is reached
        if page_count > max_pages:
            print(f"Page limit ({max_pages}) reached for {base_url}. Stopping crawl.")
            break

        print(f"\n--- Crawling Page {page_count}: {current_page_url} ---")
        html_content = polite_request(current_page_url, robot_parser)
        
        # If fetching HTML fails, stop the crawl for this site
        if not html_content:
            print(f"Stopping crawl: Failed to get HTML for {current_page_url}")
            break

        # Parse products from the fetched HTML
        products_on_page, soup = parse_products(html_content, config)
        all_products.extend(products_on_page)
        
        # Determine the next page to crawl for pagination
        next_page_link = None
        if "pagination_next_link_rel" in config["selectors"]:
            next_link_tag = soup.find("link", rel=config["selectors"]["pagination_next_link_rel"])
            if next_link_tag and next_link_tag.get("href"):
                next_page_link = next_link_tag["href"]
        elif "pagination" in config["selectors"]: # Fallback to a conventional selector if defined
            next_link_tag = soup.select_one(config["selectors"]["pagination"])
            if next_link_tag and next_link_tag.get("href"):
                next_page_link = next_link_tag["href"]

        # Update current_page_url for the next iteration or end crawl if no next link is found
        if next_page_link:
            current_page_url = urljoin(current_page_url, next_page_link)
        else:
            print("No next page link found. Ending crawl for this site.")
            current_page_url = None

    return all_products
