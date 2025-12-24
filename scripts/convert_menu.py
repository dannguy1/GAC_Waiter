import json
import re
import random
import os

def categorize_item(name, desc):
    """Heuristic categorization based on keywords."""
    text = (name + " " + desc).lower()
    
    if any(k in text for k in ["shrimp", "lobster", "fish", "squid", "salmon", "crab", "seafood", "clam", "snail", "oyster"]):
        return "Seafood"
    if any(k in text for k in ["pork", "duck", "chicken", "beef", "meat", "rib", "belly", "lamb"]):
        return "Meat & Poultry"
    if any(k in text for k in ["rice", "noodle", "vermicelli", "pho", "bun "]):
        return "Rice & Noodles"
    if any(k in text for k in ["vegetable", "tofu", "corn", "salad", "greens", "vegetarian"]):
        return "Vegetables & Sides"
    if any(k in text for k in ["mango", "brulee", "ice cream", "dessert", "sweet", "sticky rice"]):
        return "Dessert"
    if any(k in text for k in ["drink", "tea", "boba", "coffee", "lemonade", "beer", "wine"]):
        return "Drinks"
        
    return "Specialties" # Fallback

def parse_menu_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    items = []
    
    # Split content into blocks based on "Item Name:"
    blocks = re.split(r'(?=Item Name:)', content)
    
    for block in blocks:
        if "Item Name:" not in block or "Item Description:" not in block:
            continue
            
        item = {}
        
        # Extract Name
        name_match = re.search(r'Item Name:\s*(.*)', block)
        if name_match:
            item['item_name'] = name_match.group(1).strip()
            
        # Extract Description
        desc_match = re.search(r'Item Description:\s*(.*)', block)
        if desc_match:
            item['description'] = desc_match.group(1).strip()
            
        # Extract Image
        img_match = re.search(r'Item Image:\s*(.*)', block)
        if img_match:
            item['image_path'] = img_match.group(1).strip()
        else:
            item['image_path'] = "" 
            
        # Generate Random Price (10 - 30)
        item['price'] = random.randint(10, 30)
        
        if 'item_name' in item and 'description' in item:
            # Enrichment
            item['category'] = categorize_item(item['item_name'], item['description'])
            
            # 20% chance to be popular, or higher if it has an image (usually better items)
            is_popular = random.random() < 0.2
            if item['image_path']:
                is_popular = random.random() < 0.5
            item['popular'] = is_popular
            
            items.append(item)
            
    return items

def main():
    input_file = "data/GarlicAndChives.txt"
    output_file = "menu.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Parsing {input_file}...")
    items = parse_menu_file(input_file)
    
    data = {
        "restaurant_info": {
            "name": "Garlic & Chives",
            "location": "Garden Grove, CA"
        },
        "items": items
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Successfully created {output_file} with {len(items)} items.")

if __name__ == "__main__":
    main()
