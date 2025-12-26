import json
import os

def generate_missing_list():
    menu_path = 'data/menu.json'
    output_path = 'missing_images.txt'
    images_dir = 'data/images'
    
    with open(menu_path, 'r') as f:
        data = json.load(f)
    
    actual_files = set(os.listdir(images_dir))
    items = data.get('items', [])
    
    with open(output_path, 'w') as out:
        out.write("MISSING OR BROKEN IMAGES REPORT\n")
        out.write("================================\n\n")
        
        # 1. Broken Links
        out.write("TYPE 1: BROKEN LINKS (Path set but file not found)\n")
        out.write("-" * 50 + "\n")
        count_broken = 0
        for item in items:
            name = item.get('item_name')
            path = item.get('image_path', '').strip()
            
            if path:
                filename = os.path.basename(path)
                if filename not in actual_files:
                     # Check if file exists at absolute path just in case
                    if not os.path.exists(path):
                        out.write(f"[ ] {name}\n    Current Path: {path}\n")
                        count_broken += 1
        
        if count_broken == 0:
            out.write("None found.\n")
            
        out.write("\n\n")
        
        # 2. Missing Images
        out.write("TYPE 2: NO IMAGE ASSIGNED (Empty path)\n")
        out.write("-" * 50 + "\n")
        
        # Group by Category for easier hunting
        by_category = {}
        for item in items:
            name = item.get('item_name')
            path = item.get('image_path', '').strip()
            category = item.get('category', 'Uncategorized')
            
            if not path:
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(name)
        
        for cat in sorted(by_category.keys()):
            out.write(f"\nCategory: {cat}\n")
            for name in by_category[cat]:
                out.write(f"[ ] {name}\n")

    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_missing_list()
