# -*- coding: utf-8 -*-
"""
This module stores website-specific configurations for the YourBudgetFriend crawler.

It makes the crawler adaptable to different site structures by defining:
- `base_url`: The base URL of the website.
- `start_path`: The initial path to start crawling (e.g., /collections/all).
- `selectors`: A dictionary of CSS selectors to extract specific product data.
  - `product_card`: Selector for individual product listings.
  - `name`: Selector for the product name.
  - `price`: Selector for the product price (handled as 'complex_price' for special parsing).
  - `availability`: Selector to determine product availability (e.g., 'sold out').
  - `link`: Selector to extract the URL of the product page.
  - `pagination_next_link_rel`: Indicates the 'rel' attribute value for the next pagination link.

Future websites can be added to the `SITE_CONFIGS` dictionary to extend the crawler's reach.
"""
SITE_CONFIGS = {
    "shoppearlsandplaid": {
        "base_url": "https://www.shoppearlsandplaid.com",
        "start_path": "/collections/all",
        "selectors": {
            "product_card": {"selector": "div.product-item", "extract_type": "element"},
            "name": {"selector": ".product-item__title", "extract_type": "text"},
            "price": {"selector": ".price", "extract_type": "complex_price"},
            "availability": {"selector": ".product-item__badge", "extract_type": "text_contains", "value": "sold out"},
            "link": {"selector": "a.product-link", "extract_type": "attribute", "attribute": "href"},
            "pagination_next_link_rel": "next"
        }
    },
    "hopeandstetson": {
        "base_url": "https://hopeandstetson.com",
        "start_path": "/collections/all",
        "selectors": {
            "product_card": {"selector": "product-card", "extract_type": "element"},
            "name": {"selector": "div.product-card__info .product-card__title a.bold", "extract_type": "text"},
            "price": {"selector": "div.product-card__info price-list", "extract_type": "complex_price"},
            "availability": {"selector": ".product-card__badge-list", "extract_type": "presence_of_child", "child_selector": ".badge--sold-out"},
            "link": {"selector": "div.product-card__info .product-card__title a.bold", "extract_type": "attribute", "attribute": "href"},
            "pagination_next_link_rel": "next"
        }
    }
}