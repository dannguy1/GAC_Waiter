import json
import os

def audit_images():
    menu_path = 'data/menu.json'
    images_dir = 'data/images'
    
    with open(menu_path, 'r') as f:
        data = json.load(f)
        
    items = data.get('items', [])
    missing_images = []
    empty_paths = []
    
    # Get actual files in directory
    actual_files = set(os.listdir(images_dir))
    
    for item in items:
        name = item.get('item_name')
        path = item.get('image_path', '').strip()
        
        if not path:
            empty_paths.append(name)
            continue
            
        # Extract filename from path (e.g., ./images/Foo.jpg -> Foo.jpg)
        filename = os.path.basename(path)
        
        if filename not in actual_files:
            # Also check if the path itself exists (in case it's not in data/images)
            if not os.path.exists(path):
                missing_images.append({
                    "name": name,
                    "path": path,
                    "filename": filename
                })

    print(f"Total Items: {len(items)}")
    print(f"Items with Empty Image Path: {len(empty_paths)}")
    print(f"Items with Missing Image Files: {len(missing_images)}")
    print("\n--- Items with Missing Image Files (Path set but file not found) ---")
    for m in missing_images:
        print(f"- {m['name']} (Expected: {m['path']})")
        
    print("\n--- Items with Empty Image Path ---")
    for name in empty_paths:
        print(f"- {name}")

if __name__ == "__main__":
    audit_images()
