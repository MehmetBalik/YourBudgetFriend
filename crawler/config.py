# Website-specific configurations is stored here.
# This makes the crawler adaptable to different site structures.
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
    # Future websites can be added here
}