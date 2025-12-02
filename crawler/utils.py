import json
from datetime import datetime
import os # Import os to create logs directory if it doesn't exist

def save_json(data, file_prefix="all_products"):
    """
    Saves a list of dictionaries to a timestamped JSON file in the 'logs' directory.
    Combines products from all sites into a single file.
    """
    # Ensure the logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{log_dir}/{file_prefix}_{timestamp}.json"
    
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} products to {file_name}")
    

def detect_category(name):
    n = name.lower()

    CATEGORY_KEYWORDS = {
        "Dress": ["dress", "gown"],
        "Top": ["top", "tank", "blouse", "camisole"],
        "Shirt": ["shirt", "button-down", "blouse"],
        "Sweater": ["sweater", "knit", "pullover", "cardigan"],
        "Hoodie": ["hoodie", "hooded", "fleece"],
        "Jacket": ["jacket", "coat", "outerwear", "parka"],
        "Jeans": ["jean", "denim"],
        "Pants": ["pant", "trouser", "cargo"],
        "Shorts": ["shorts"],
        "Skirt": ["skirt"],
        "Shoes": ["shoe", "boot", "heel", "sandal", "sneaker"],
        "Romper/Jumpsuit": ["romper", "jumpsuit"],
        "Activewear": ["leggings", "sports", "athletic"],
    }

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(word in n for word in keywords):
            return category

    return "Other"

