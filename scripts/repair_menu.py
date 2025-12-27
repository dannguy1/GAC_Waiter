import json
import os

target_path = '/home/danlnguyen/GAC/GAC_Waiter/data/menu.json'
original_path = '/home/danlnguyen/GAC/GAC_Waiter/data-original/menu.json'

# Use original if target doesn't exist
if not os.path.exists(target_path):
    target_path = original_path

with open(target_path, 'r') as f:
    data = json.load(f)

items = data.get('items', [])
changes = 0

for item in items:
    name = item.get('item_name', '')
    cat = item.get('category', '')
    
    # Logic to re-categorize
    if "Banh Trang Tron" in name: 
        item['category'] = "Salads"
        changes += 1
    elif "Salad" in name or "Goi" in name:
        item['category'] = "Salads"
        changes += 1
    elif "Roll" in name or "Cuon" in name or "Cha Gio" in name:
        item['category'] = "Appetizers & Rolls"
        changes += 1
    elif "Sweet Potato" in name or "Corn" in name or "Fries" in name:
        item['category'] = "Appetizers & Rolls"
        changes += 1
    elif "Fried Rice" in name or "Porridge" in name or "Chowfun" in name or "Pad Thai" in name or "Noodle" in name:
        # Move Rice/Noodle items out of Seafood/Meat if they are main dishes
        # Unless it's "Lobster with Garlic Noodles" which is borderline. 
        # But "Fried Rice" in Seafood is definitely wrong.
        if cat == "Seafood" or cat == "Meat & Poultry":
             item['category'] = "Rice & Noodles"
             changes += 1

print(f"Repaired {changes} items.")

# Save back
with open(target_path, 'w') as f:
    json.dump(data, f, indent=2)

# Sync to original
if target_path != original_path and os.path.exists(original_path):
    with open(original_path, 'w') as f:
        json.dump(data, f, indent=2)
