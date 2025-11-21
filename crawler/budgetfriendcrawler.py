import requests
import time
import random
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

BASE_URL = "https://exampleclothing.com"  # <<< change this
START_URL = BASE_URL + "/collections/all"  # <<< change this

HEADERS = {
    "User-Agent": "BenignClothingCrawler/1.0 (email@example.com)"
}

# ----------------------------
# 1. Check robots.txt
# ----------------------------
def check_robots_txt(url):
    rp = RobotFileParser()
    rp.set_url(urljoin(url, "/robots.txt"))
    rp.read()
    return rp

robots = check_robots_txt(BASE_URL)
if not robots.can_fetch(HEADERS["User-Agent"], START_URL):
    print("❌ Crawling disallowed by robots.txt")
    exit()

# ----------------------------
# 2. Polite Request Function
# ----------------------------
def polite_request(url):
    # Random polite delay (human-like)
    time.sleep(random.uniform(1.0, 3.0))

    response = requests.get(url, headers=HEADERS, timeout=10)

    # Respect Retry-After header if present
    if response.status_code == 429:
        wait = int(response.headers.get("Retry-After", 5))
        print(f"Rate-limited. Waiting {wait} seconds...")
        time.sleep(wait)
        return requests.get(url, headers=HEADERS, timeout=10)

    response.raise_for_status()
    return response

# ----------------------------
# 3. Parse a Single Product Card
# ----------------------------
def parse_product(card):
    try:
        name = card.select_one(".product-card-title").get_text(strip=True)
        price = card.select_one(".product-card-price").get_text(strip=True)
        link = urljoin(BASE_URL, card.select_one("a")["href"])

        return {
            "name": name,
            "price": price,
            "link": link
        }
    except:
        return None

# ----------------------------
# 4. Crawl Clothing Page
# ----------------------------
def crawl_clothing_page(url):
    print(f"Crawling: {url}")
    html = polite_request(url).text
    soup = BeautifulSoup(html, "html.parser")

    product_cards = soup.select(".product-card")   # <<< change selector

    items = []
    for card in product_cards:
        item = parse_product(card)
        if item:
            items.append(item)

    return items

# ----------------------------
# 5. Main Crawl Function
# ----------------------------
def crawl_site(start_url):
    all_items = []
    
    next_page = start_url

    while next_page:
        if not robots.can_fetch(HEADERS["User-Agent"], next_page):
            print(f"Skipping disallowed page: {next_page}")
            break

        items = crawl_clothing_page(next_page)
        all_items.extend(items)

        # find next page button
        soup = BeautifulSoup(requests.get(next_page, headers=HEADERS).text, "html.parser")
        next_link = soup.select_one("a.next")  # <<< update this selector if needed

        next_page = urljoin(BASE_URL, next_link["href"]) if next_link else None

    return all_items

# ----------------------------
# 6. Save Data
# ----------------------------
def save_json(data, file="clothing_data.json"):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} items to {file}")

# ----------------------------
# Run Crawler
# ----------------------------
if __name__ == "__main__":
    data = crawl_site(START_URL)
    save_json(data)

    print("Crawling completed successfully!")
