# -*- coding: utf-8 -*-
"""
This module provides utility functions for the YourBudgetFriend crawler,
including data saving and product categorization.
"""

import json
from datetime import datetime

# Module-level constant for category keywords, used to classify products.
CATEGORY_KEYWORDS = {
    "Dress": ["dress", "gown", "frock", "maxi", "midi", "mini", "cocktail", "evening"],
    "Top": ["top", "tank", "blouse", "camisole", "t-shirt", "tee", "crop top", "bodysuit"],
    "Shirt": ["shirt", "button-down", "blouse", "flannel", "button-up"],
    "Sweater": ["sweater", "knit", "pullover", "cardigan", "jumper"],
    "Hoodie": ["hoodie", "hooded", "fleece"],
    "Jacket": ["jacket", "coat", "outerwear", "parka", "blazer", "vest", "bomber", "trench", "raincoat"],
    "Jeans": ["jean", "denim"],
    "Pants": ["pant", "trouser", "cargo", "joggers", "capris", "culottes"],
    "Shorts": ["shorts"],
    "Skirt": ["skirt"],
    "Shoes": ["shoe", "boot", "heel", "sandal", "sneaker", "flats", "loafers", "pumps", "wedges"],
    "Romper/Jumpsuit": ["romper", "jumpsuit"],
    "Activewear": ["leggings", "sports", "athletic", "yoga pants", "sportswear", "athletic wear"],
}

def save_json(data, file_prefix="all_products"):
    """
    Saves the output data to a timestamped JSON file in the 'logs' directory.
    Combines products from all websites into a single file for easy access and logging.
    """
    log_dir = "logs"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{log_dir}/{file_prefix}_{timestamp}.json"
    
    # Ensure the log directory exists before writing.
    os.makedirs(log_dir, exist_ok=True)
    
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} products to {file_name}")
    
def detect_category(name):
    """
    Detects the category of a product based on its name using predefined keywords.
    """
    normalized_name = name.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in normalized_name for word in keywords):
            return category

    return "Other"