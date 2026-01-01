import json
import os
import sys

def find_missing_images():
    # Base directory is the project root, assuming script is run from project root
    # or we can find data relative to the script location.
    # Let's assume script is run from project root as per other scripts
    if os.path.isdir('data'):
        base_dir = 'data'
    elif os.path.isdir('../data'):
        base_dir = '../data'
    else:
        print("Error: Could not locate data directory.")
        sys.exit(1)

    menu_path = os.path.join(base_dir, 'menu.json')
    
    print(f"Reading menu from: {menu_path}")
    
    try:
        with open(menu_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {menu_path} not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {menu_path}.")
        sys.exit(1)

    items = data.get('items', [])
    
    missing_files = []
    empty_paths = []
    
    print(f"Checking {len(items)} items...")
    
    for item in items:
        name = item.get('item_name', 'Unknown Item')
        image_path = item.get('image_path', '').strip()
        
        if not image_path:
            empty_paths.append(name)
            continue
            
        # Resolve path relative to data directory
        # If path starts with ./, it's relative to data/
        # e.g., ./images/foo.jpg -> data/images/foo.jpg
        # e.g., ./downloaded_images/bar.jpg -> data/downloaded_images/bar.jpg
        
        if image_path.startswith('./'):
            clean_path = image_path[2:] # Remove ./
        else:
            clean_path = image_path
            
        full_path = os.path.join(base_dir, clean_path)
        
        if not os.path.exists(full_path):
            missing_files.append({
                'name': name,
                'path_in_json': image_path,
                'resolved_path': full_path
            })

    print("\n" + "="*50)
    print("MISSING IMAGE FILES REPORT")
    print("="*50)
    
    if missing_files:
        print(f"\nFound {len(missing_files)} items with broken image links:\n")
        for item in missing_files:
            print(f"[X] {item['name']}")
            print(f"    JSON Path:     {item['path_in_json']}")
            print(f"    Resolved Path: {item['resolved_path']} (Not Found)")
            print("-" * 30)
    else:
        print("\nNo broken image links found.")

    print("\n" + "="*50)
    print("ITEMS WITHOUT IMAGES")
    print("="*50)
    
    if empty_paths:
        print(f"\nFound {len(empty_paths)} items with no image assigned:\n")
        for name in empty_paths:
            print(f"[ ] {name}")
    else:
        print("\nAll items have an image path assigned.")

if __name__ == "__main__":
    find_missing_images()
