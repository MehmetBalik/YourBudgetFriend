import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import detect_category


def _clean_price(price_string):
    
    """Cleans a price string to return a numerical value in American format (e.g., "38.40 $"). 
    Assumes prices are always >= $1.00, less than $1000, and uses '.' as the decimal separator."""
    
    if not isinstance(price_string, str):
        return price_string

    # Use regex to find the first sequence of digits, optionally followed by a dot and more digits
    # This directly extracts "14.00" from "Sale price$ 14.00 USD" or "25.00" from "From$ 25.00"
    match = re.search(r'(\d+\.?\d*)', price_string) # Finds "14" or "14.00"

    if match:
        numerical_price_string = match.group(1)
        try:
            # Format to two decimal places and add " $" at the end
            return f"{float(numerical_price_string):.2f} $"
        except ValueError:
            return "N/A" # If the extracted part isn't a valid float
    
    return "N/A" # If no numerical part is found

def _extract_field(card_element, field_config, base_url):
    
    """Helper function to extract data based on field configuration."""
    
    selector = field_config["selector"]
    extract_type = field_config["extract_type"]
    
    selected_element = card_element.select_one(selector)

    if not selected_element:
        # Special handling for availability to return "Available" by default if not found
        if extract_type == "text_contains" or extract_type == "presence_of_child":
            return "Available"
        return "N/A"

    extracted_value = "N/A"

    if extract_type == "text":
        extracted_value = selected_element.get_text(strip=True)
    
    elif extract_type == "attribute":
        attribute_name = field_config.get("attribute")
        if attribute_name:
            value = selected_element.get(attribute_name)
            if value and attribute_name == "href":
                extracted_value = urljoin(base_url, value)
            else:
                extracted_value = value
    
    elif extract_type == "text_contains":
        text_to_check = field_config.get("value", "").lower()
        if text_to_check in selected_element.get_text(strip=True).lower():
            extracted_value = "Sold Out"
        else:
            extracted_value = "Available"
        
    elif extract_type == "presence_of_child":
        child_selector = field_config.get("child_selector")
        if child_selector and selected_element.select_one(child_selector):
            extracted_value = "Sold Out"
        else:
            extracted_value = "Available"

    elif extract_type == "complex_price":
        # Prioritized list of selectors for price
        price_selectors = [
            "sale-price span.price",        # Specific span within sale-price
            "sale-price",                   # Direct sale-price tag
            "compare-at-price span.price",  # Specific span within compare-at-price
            "compare-at-price",             # Direct compare-at-price tag
        ]

        for s in price_selectors:
            price_tag = selected_element.select_one(s)
            if price_tag:
                extracted_value = price_tag.get_text(strip=True)
                break
        
        if extracted_value == "N/A": # Final fallback to general text if specific selectors fail
            extracted_value = selected_element.get_text(strip=True)

    # Apply price cleaning if the field is price-related
    if "price" in selector or extract_type == "complex_price": 
        return _clean_price(extracted_value)
    
    return extracted_value


def parse_products(html_content, config):
    
    """Parses HTML content to extract product information based on the site's config."""
    
    soup = BeautifulSoup(html_content, "html.parser")
    selectors = config["selectors"]
    base_url = config["base_url"]

    product_card_selector_info = selectors["product_card"]
    product_cards = soup.select(product_card_selector_info["selector"])
    products = []

    print(f"Found {len(product_cards)} product cards using selector '{product_card_selector_info['selector']}'")

    for i, card in enumerate(product_cards):
        name = _extract_field(card, selectors["name"], base_url)
        price = _extract_field(card, selectors["price"], base_url)
        availability = _extract_field(card, selectors["availability"], base_url)
        link = _extract_field(card, selectors["link"], base_url)

        # If price is N/A, then it's sold out
        if price == "N/A" and availability == "Available":
            availability = "Sold Out"

        products.append({
            "name": name,
            "price": price,
            "availability": availability,
            "link": link,
            "category": detect_category(name)
        })
        
    return products, soup