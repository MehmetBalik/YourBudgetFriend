# -*- coding: utf-8 -*-
"""
This module is responsible for parsing HTML content and extracting product
information based on predefined CSS selectors.

It provides functions for:
- Cleaning and formatting price strings.
- Dynamically extracting various fields (name, price, availability, link)
  from product cards using BeautifulSoup and site-specific configurations.
- Detecting product categories based on their names.
"""

import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import detect_category


def _clean_price(price_string):
    """
    Cleans a price string to return a numerical value in American format (e.g., "38.40 $").
    Assumes prices are always >= .00, less than 000, and uses '.' as the decimal separator.
    """
    if not isinstance(price_string, str):
        return price_string

    # Use regex to find the first sequence of digits, optionally followed by a dot and more digits.
    # This extracts numerical parts like "14.00" from "Sale price$ 14.00 USD".
    match = re.search(r'(\d+\.?\d*)', price_string)

    if match:
        numerical_price_string = match.group(1)
        try:
            # Format to two decimal places and append " $" for consistency.
            return f"{float(numerical_price_string):.2f} $"
        except ValueError:
            # If the extracted part isn't a valid float, return "N/A".
            return "N/A"
    
    return "N/A"  # If no numerical part is found.

def _extract_field(card_element, field_config, base_url):
    """
    Helper function to extract data from a product card element based on its field configuration.
    """
    selector = field_config["selector"]
    extract_type = field_config["extract_type"]
    
    selected_element = card_element.select_one(selector)

    # Handle cases where the element is not found.
    if not selected_element:
        # For availability, default to "Available" if the 'sold out' indicator is not found.
        if extract_type == "text_contains" or extract_type == "presence_of_child":
            return "Available"
        return "N/A"  # Default for other fields.

    extracted_value = "N/A"

    if extract_type == "text":
        extracted_value = selected_element.get_text(strip=True)
    
    elif extract_type == "attribute":
        attribute_name = field_config.get("attribute")
        if attribute_name:
            value = selected_element.get(attribute_name)
            # Join relative URLs with the base URL.
            if value and attribute_name == "href":
                extracted_value = urljoin(base_url, value)
            else:
                extracted_value = value
    
    elif extract_type == "text_contains":
        # Check if specific text (e.g., "sold out") is present in the element's text.
        text_to_check = field_config.get("value", "").lower()
        if text_to_check in selected_element.get_text(strip=True).lower():
            extracted_value = "Sold Out"
        else:
            extracted_value = "Available"
        
    elif extract_type == "presence_of_child":
        # Check for the presence of a specific child element to determine availability.
        child_selector = field_config.get("child_selector")
        if child_selector and selected_element.select_one(child_selector):
            extracted_value = "Sold Out"
        else:
            extracted_value = "Available"

    elif extract_type == "complex_price":
        # Handle complex price extraction with multiple possible selectors.
        price_selectors = [
            "sale-price span.price",        # Specific span within sale-price
            "sale-price",                   # Direct sale-price tag
            "compare-at-price span.price",  # Specific span within compare-at-price
            "compare-at-price",             # Direct compare-at-price tag
        ]

        # Iterate through selectors, using the first one that yields a result.
        for s in price_selectors:
            price_tag = selected_element.select_one(s)
            if price_tag:
                extracted_value = price_tag.get_text(strip=True)
                break
        
        # Fallback to general text if specific selectors fail.
        if extracted_value == "N/A":
            extracted_value = selected_element.get_text(strip=True)

    # Apply price cleaning if the field is price-related.
    if "price" in selector or extract_type == "complex_price": 
        return _clean_price(extracted_value)
    
    return extracted_value


def parse_products(html_content, config):
    """
    Parses HTML content to extract product information based on the site's configuration.
    Returns a list of product dictionaries and the BeautifulSoup object of the parsed HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    selectors = config["selectors"]
    base_url = config["base_url"]

    # Select all product cards on the page.
    product_card_selector_info = selectors["product_card"]
    product_cards = soup.select(product_card_selector_info["selector"])
    products = []

    print(f"Found {len(product_cards)} product cards using selector '{product_card_selector_info['selector']}'")

    # Extract details for each product card.
    for card in product_cards:
        name = _extract_field(card, selectors["name"], base_url)
        price = _extract_field(card, selectors["price"], base_url)
        availability = _extract_field(card, selectors["availability"], base_url)
        link = _extract_field(card, selectors["link"], base_url)

        # Adjust availability if price is "N/A" (implying it might be sold out).
        if price == "N/A" and availability == "Available":
            availability = "Sold Out"

        products.append({
            "name": name,
            "price": price,
            "availability": availability,
            "link": link,
            "category": detect_category(name)  # Assign category based on product name.
        })
        
    return products, soup