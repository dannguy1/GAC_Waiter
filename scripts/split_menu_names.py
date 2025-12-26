import json
import os

MENU_PATH = "data/menu.json"

def split_names():
    with open(MENU_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated_items = []
    count = 0
    
    for item in data.get("items", []):
        name = item.get("item_name", "")
        # Check for the separator " - "
        if " - " in name:
            parts = name.split(" - ")
            # Only split if we have exactly 2 parts or just take the last part as vietnamese?
            # User said "The separation is ' - '".
            # Some items might have multiple dashes, but typically the structure is Eng - Viet.
            # Let's assume the first split is the separation or the last? 
            # Looking at "Baked Crispy Catfish with Boiled Pork - Ca Nuong Da Gion Thit Luoc" -> split on " - " gives 2 parts.
            # "Shrimp and Pork Mustard Green - Cai Bao Xanh Cuon Tom Thit" -> 2 parts.
            
            # If there are multiple " - " it might be tricky, but assuming 2 parts for now based on file view.
            # If multiple parts, usually the last part is Vietnamese?
            # actually lets check if there are > 2 parts.
            
            if len(parts) >= 2:
                # English is likely the first part, Vietnamese is the rest?
                # or English is everything before the last " - "?
                # Use the last " - " as the delimiter effectively?
                # Actually, looking at "Ong choy with Garlic/Rau Muong Xao Toi" (Wait, original had / but user changed to -)
                # "Ong choy with Garlic - Rau Muong Xao Toi"
                
                # Safe bet: English is everything before the last " - ", Vietnamese is the last part.
                # But wait, what if the English name has a hyphen? "Stir-Fried Eggplant..."
                # The user specified " - " (space hyphen space). "Stir-Fried" uses just hyphen.
                # So splitting on " - " should be safe.
                
                english_name = parts[0].strip()
                viet_name = " - ".join(parts[1:]).strip() # Join back in case there were multiple " - " but likely just one.
                
                item["item_name"] = english_name
                item["item_viet"] = viet_name
                count += 1
            else:
                item["item_viet"] = ""
        else:
             item["item_viet"] = ""
        
        updated_items.append(item)
    
    data["items"] = updated_items
    
    with open(MENU_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    print(f"Updated {count} items.")

if __name__ == "__main__":
    split_names()
