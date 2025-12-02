import requests
import time
import random
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from parser import parse_products

USER_AGENT = "YourBudgetFriendBot/1.0 (+your-email@example.com) Academic-Polite-Crawler"

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
    Fetches HTML content from a URL with a polite delay, respecting robots.txt.
    """
    if robot_parser and not robot_parser.can_fetch(USER_AGENT, url):
        print(f"Robots.txt disallows crawling of {url}")
        return None

    headers = {"User-Agent": USER_AGENT}
    try:
        print(f"Attempting to fetch: {url}")
        time.sleep(random.uniform(1.5, 3.5)) # Polite delay
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        print(f"Successfully fetched HTML from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def crawl_site(config):
    """
    Crawls a multi-page site using a specific configuration.
    """
    all_products = []
    base_url = config["base_url"]
    start_url = urljoin(base_url, config["start_path"])
    current_page_url = start_url
    page_count = 0

    # Initialize robots.txt parser for the site
    robot_parser = check_robots_txt(base_url)
    if not robot_parser:
        print(f"Could not read robots.txt for {base_url}. Proceeding without strict adherence.")
        # Ensure robot_parser is explicitly None if reading fails
        robot_parser = None 

    while current_page_url:
        page_count += 1
        print(f"\n--- Crawling Page {page_count}: {current_page_url} ---")
        html_content = polite_request(current_page_url, robot_parser)
        
        if not html_content:
            print(f"Stopping crawl: Failed to get HTML for {current_page_url}")
            break

        products_on_page, soup = parse_products(html_content, config)
        all_products.extend(products_on_page)
        
        # Temporarily disable pagination for debugging purposes
        print("DEBUG MODE: Limiting crawl to one page for debugging.")
        current_page_url = None # Stop after the first page
        # """ ORIGINAL PAGINATION LOGIC:
        # # Check for next page link in <link rel="next"> or <a> tag
        # next_page_link = None
        # if "pagination_next_link_rel" in config["selectors"]:
        #     next_link_tag = soup.find("link", rel=config["selectors"]["pagination_next_link_rel"])
        #     if next_link_tag and next_link_tag.get("href"):
        #         next_page_link = next_link_tag["href"]
        # elif "pagination" in config["selectors"]: # Fallback to a conventional selector if defined
        #     next_link_tag = soup.select_one(config["selectors"]["pagination"])
        #     if next_link_tag and next_link_tag.get("href"):
        #         next_page_link = next_link_tag["href"]

        # if next_page_link:
        #     current_page_url = urljoin(current_page_url, next_page_link) # Use current_page_url for relative links
        # else:
        #     print("No next page link found. Ending crawl for this site.")
        #     current_page_url = None
        # """ # END ORIGINAL PAGINATION LOGIC

    return all_products

    return all_products
