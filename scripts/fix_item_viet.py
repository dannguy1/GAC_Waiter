#!/usr/bin/env python3
"""
Fix Vietnamese item names (item_viet) with proper diacritics.
"""

import json
import os

# Corrected Vietnamese names with proper diacritics
# Format: "item_name" -> "corrected_item_viet"
ITEM_VIET_FIXES = {
    # === ALREADY CORRECT (with diacritics) ===
    # Skip these - they're already good
    
    # === NEEDS FIXING (missing diacritics) ===
    
    # Seafood & Appetizers
    "Honey Walnut Shrimps with Chips": "Tôm Walnut Mật Ong với Bánh Phồng Tôm",
    "Baked Crispy Catfish with Boiled Pork": "Cá Nướng Da Giòn Thịt Luộc",
    "Crispy Peking Duck with Crepes": "Vịt Bắc Kinh Giòn với Bánh Crepe",
    "Crispy Whole Fish with Mango Sauce or Thai Chili": "Cá Nguyên Con Chiên Giòn Sốt Xoài hoặc Ớt Thái",
    "House Special Pork Chops": "Sườn Heo Đặc Biệt",
    "Salt & Pepper Garlic Butter Pork Chops": "Sườn Heo Muối Tiêu Bơ Tỏi",
    "House Special Squid": "Mực Đặc Biệt",
    "House Special Lobster with Garlic Noodles (priced by lbs)": "Tôm Hùm Đặc Biệt với Mì Tỏi",
    "Grilled Salmon in Seafood Sauce with Garlic Rice": "Cá Hồi Nướng Sốt Hải Sản với Cơm Tỏi",
    "Sticky Rice with Mango": "Xôi Xoài",
    "Creme Brulee": "Kem Brûlée",
    "Garlic Butter Chicken": "Cánh Gà Chiên Bơ Tỏi",
    "Baked Corn Cheese": "Bắp Nướng Phô Mai",
    "Egg rolls": "Chả Giò",
    "Chicken Satay": "Gà Sa Tế",
    "Holy Crunchy Chicken wings": "Cánh Gà Chiên Giòn",
    "Fried Sweet Potatoes": "Khoai Lang Chiên",
    "Salmon Belly Chien Gion": "Bụng Cá Hồi Chiên Giòn",
    "Toothpick Lamb": "Cừu Xiên Que",
    "Corn with Dried Shrimp": "Bắp Xào Tôm Khô",
    "Pho French Dip": "Phở French Dip",
    
    # Spring Rolls
    "Shrimp Roll": "Gỏi Cuốn Tôm",
    "Grilled Pork Sausage Roll": "Gỏi Cuốn Nem Nướng",
    "Vegetable Roll": "Gỏi Cuốn Chay",
    "Grilled Pork Spring Roll": "Gỏi Cuốn Thịt Nướng",
    "Salmon Belly Roll": "Gỏi Cuốn Cá Hồi",
    "Beef Roll": "Gỏi Cuốn Bò Nướng",
    "Poke Roll": "Gỏi Cuốn Ahi Poke",
    "Pork and Shrimp Roll": "Gỏi Cuốn Tôm Thịt",
    "Shrimp and Pork Mustard Green": "Cải Bẹ Xanh Cuốn Tôm Thịt",
    
    # Salads
    "Tiger Shrimp and Mango Salad": "Gỏi Xoài Tôm Sú",
    "Ahi Poke Salad (Seared)": "Gỏi Cá Ahi Áp Chảo",
    "Green Papaya Beef Jerky Salad": "Gỏi Đu Đủ Khô Bò",
    "Thai Calamari Salad": "Gỏi Mực Thái Lan",
    "Baby Clam Salad": "Gỏi Hến",
    "Grilled Salmon Salad": "Gỏi Cá Hồi Nướng",
    "Ahi Poke Salad": "Gỏi Cá Ahi",
    "Lotus Root Salad": "Gỏi Ngó Sen",
    "Beef Ong Choy Salad": "Gỏi Rau Muống Bò Xào",
    "Thai Beef Salad": "Gỏi Bò Thái Lan",
    "Rice paper Salad": "Bánh Tráng Trộn",
    "Lime Beef Salad": "Bò Tái Chanh",
    "Pomelo Salad": "Gỏi Bưởi",
    "Hamachi Yellowtail Sashimi Salad": "Gỏi Cá Cam Sashimi",
    "Mango and Papaya Salad": "Gỏi Xoài Đu Đủ",
    "Pineapple Salad": "Gỏi Thơm",
    "Chicken Salad": "Gỏi Gà",
    
    # Seafood Main Dishes
    "Tamarind Crab": "Cua Rang Me",
    "Ong Choy with Pork Belly and Seasnails": "Rau Muống Xào Ốc Ba Chỉ",
    "Baked Clams with Chili Garlic": "Nghêu Nướng Tỏi Ớt",
    "Sauteed Sea Snails": "Ốc Hương Xào",
    "Clams in Lemongrass Soup": "Nghêu Hấp Sả",
    "Chili Lemongrass Sea Snail Soup": "Ốc Hương Hấp Sả Ớt",
    "Deep Fried Calamari": "Mực Lăn Bột",
    "Baked Clams": "Nghêu Nướng Mỡ Hành Tỏi",
    "Basil Clams": "Nghêu Xào Lá Quế",
    "Chili Dungeness Crab": "Cua Singapore",
    "Charbroiled Blk Tiger on Garlic Noodles": "Mì Tỏi Tôm Sú Nướng",
    "Salt and Pepper Shrimp": "Tôm Rang Muối",
    "Ong Choy with Seasnails": "Rau Muống Xào Ốc Hương",
    "Grilled Blood Clams": "Sò Huyết Nướng Mỡ Hành",
    "Shrimp Skewers": "Tôm Xiên Nướng",
    "Baked King Crab Legs": "Càng Cua Hoàng Đế Nướng",
    "Grilled Calamari": "Mực Nướng Thái",
    "Grilled Scallops": "Sò Điệp Nướng",
    "Razor Clams": "Ốc Móng Tay",
    "Coconut Seasnails": "Ốc Len Xào Dừa",
    "Spicy Baby Clams on Rice Chips": "Hến Xào Xúc Bánh Tráng",
    "Lemongrass Seafood Soup": "Đồ Biển Hấp Sả",
    "House-Special Garlic Crab": "Cua Đặc Biệt",
    "House Special Lobster": "Tôm Hùm Đặc Biệt",
    "Baked Crispy Catfish w. Boiled Pork": "Cá Nướng Da Giòn Thịt Luộc",
    
    # Meat & Poultry
    "Ong choy with Beef": "Rau Muống Xào Bò",
    "Shaken Tofu": "Đậu Hũ Lúc Lắc",
    "Lamb Chops": "Sườn Cừu",
    "Chicken Curry": "Cà Ri Gà",
    "Sizzling Filet Mignon": "Bò Né",
    
    # Noodles & Rice
    "Seafood Chowfun": "Hủ Tiếu Xào Hải Sản",
    "Chicken Chowfun": "Hủ Tiếu Xào Gà",
    "Sauteed Beef and Garlic Noodles": "Bò Xào Mì Tỏi",
    "Vegetarian Egg Noodles": "Mì Xào Chay",
    "Chicken Egg Noodles": "Mì Xào Gà",
    "Seafood Egg Noodles": "Mì Xào Hải Sản",
    "Pork Chop/Egg/Garlic Fries": "Sườn Heo Cốt Lết",
    "Combination Egg Noodles": "Mì Xào Thập Cẩm",
    "Chicken Garlic Noodles": "Mì Tỏi Gà",
    "Beef Egg Noodles": "Mì Xào Bò",
    "Beef Chowfun": "Hủ Tiếu Xào Bò",
    "Shaken Filet Mignon": "Bò Lúc Lắc",
    "Goat Curry": "Cà Ri Dê",
    "Combination Chowfun": "Hủ Tiếu Xào Thập Cẩm",
    "Pad Thai": "Phở Xào Thái",
    "Stir Fried Glass Noodles Crab & Shrimp": "Miến Xào Tôm Cua",
    "Shrimp Chowfun": "Hủ Tiếu Xào Tôm",
    "Vegetarian Chowfun": "Hủ Tiếu Xào Chay",
    "Grilled Chicken Garlic Noodles": "Gà Nướng Mì Tỏi",
    "Stir-Fried Eggplant with Crispy Pork": "Cà Tím Xào Thịt Heo Giòn",
    "Fried Rice": "Cơm Chiên",
    "Salted Fish Rice": "Cơm Cá Mặn",
    "Grilled Pork Rice": "Cơm Thịt Nướng",
    "Ong Choy with Pork Belly": "Rau Muống Xào Ba Chỉ",
    
    # Hotpots
    "Thai Hotpot": "Lẩu Thái",
    "Fish Head Hotpot": "Lẩu Đầu Cá Bắp Chuối",
    "Fish Hotpot": "Lẩu Canh Chua Cá",
    "Lobster and Seafood Hotpot": "Lẩu Tôm Hùm Hải Sản",
    "Salmon Hotpot": "Lẩu Cá Hồi",
    "Seabass w. Prawn Hot Pot": "Lẩu Cá Chẽm Tôm Càng",
    "Szechwan Hotpot": "Lẩu Tứ Xuyên",
    "Goat Hot Pot": "Lẩu Dê",
    "Filet Mignon Hot Pot": "Lẩu Bò Thăn",
    "Oxtail Hotpot": "Lẩu Đuôi Bò",
    
    # Soups
    "Vietnamese Soup": "Phở",
    "Water Spinach Noodle Soup": "Canh Bún",
    "Vietnamese Hot and Sour Soup": "Canh Chua",
    "Purple Yam Soup": "Canh Khoai Mỡ",
    "Tofu and Fish Soup": "Canh Cá và Đậu Hũ",
    "Mustard Green Soup": "Canh Cải Chua",
    
    # Rice Dishes
    "Carmelized Salmon": "Cá Hồi Kho Tộ",
    "Grilled Salmon w. Tamarind Sauce": "Cơm Cá Hồi Nướng Sốt Me",
    "Caramelized Catfish w. Pork Belly": "Cá Kho Tộ Ba Chỉ",
    "Caramelized Peppered Pork Belly": "Thịt Ba Chỉ Kho Tiêu",
    "Grilled Salmon": "Cá Hồi Nướng",
    "Lemongrass Pork Ribs": "Sườn Non Nướng Sả",
    "Rotisserie Chicken": "Gà Quay",
    "Sticky Rice w. Chinese Sausage, Eggs, Shredded Pork": "Xôi Lạp Xưởng Trứng Chà Bông",
    "Carmelized Catfish": "Cá Kho Tộ",
    "Caramelized Pork Ribs": "Sườn Ram",
    "Salmon w. House Special Sauce": "Cá Hồi Sốt Đặc Biệt",
    "Fried Chili Lemongrass Salmon": "Cá Hồi Chiên Sả Ớt",
    "Dill and Tumeric Fish": "Chả Cá Thăng Long",
    
    # Vermicelli / Bún
    "Sauteed Filet Mignon Vermicelli": "Bún Bò Xào",
    "Grilled Salmon Noodles": "Bún Cá Hồi Nướng",
    "Grilled Shrimp Noodles": "Bún Tôm Nướng",
    "Eggroll Noodles": "Bún Chả Giò",
    "Grilled Filet Mignon Vermicelli": "Bún Bò Nướng",
    "Grilled Pork Vermicelli": "Bún Thịt Nướng",
    "Noodle Soup": "Bún Cá",
    "Famous Central VN Spicy Noodles": "Bún Bò Huế",
    "Shrimp and Crab Soup": "Bún Riêu Tôm Cua",
    "Hanoi Styled Vermicelli with Grilled Pork": "Bún Chả Hà Nội",
    "Deep Fried Tofu and Boiled Pork Vermicelli": "Bún Đậu Mắm Tôm",
    
    # Porridge
    "Plain Pho": "Phở Không",
    "Shrimp Rice Porridge": "Cháo Tôm",
    "Minced Beef Porridge": "Cháo Bò Bằm",
    "Fish Porridge": "Cháo Cá",
    "Minced Pork/Salted Egg Porridge": "Cháo Thịt Bằm Trứng Bách Thảo",
    "Combination Rice Porridge": "Cháo Thập Cẩm",
    "Chicken Porridge": "Cháo Gà",
    "Plain Rice Porridge": "Cháo Trắng",
    
    # Vegetarian / Sides
    "Tofu and Veggie Soup": "Canh Đậu Hũ Rau Củ",
    "Stir-Fried Eggplant": "Cà Tím Xào Tỏi",
    "Fried Tofu": "Đậu Hũ Chiên Giòn",
    "Garlic Spinach": "Rau Dền Xào Tỏi",
    "Vegetarian Salad": "Gỏi Chay",
    "Ong choy with Garlic": "Rau Muống Xào Tỏi",
    "Green Beans with Garlic": "Đậu Que Xào Tỏi",
    "Stir Fried Bok choy with Garlic": "Cải Thìa Xào Tỏi",
}


def main():
    menu_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'menu.json')
    
    print("=" * 60)
    print("Fixing Vietnamese Item Names (item_viet)")
    print("=" * 60)
    
    # Load menu
    with open(menu_path, 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    
    items = menu_data.get('items', [])
    print(f"\nTotal items: {len(items)}")
    print(f"Fixes available: {len(ITEM_VIET_FIXES)}")
    
    # Apply fixes
    fixed = 0
    already_good = 0
    not_found = []
    
    for item in items:
        name = item.get('item_name', '')
        current_viet = item.get('item_viet', '')
        
        # Look up fix
        if name in ITEM_VIET_FIXES:
            new_viet = ITEM_VIET_FIXES[name]
            if current_viet != new_viet:
                item['item_viet'] = new_viet
                fixed += 1
                print(f"  ✅ {name}")
                print(f"     OLD: {current_viet}")
                print(f"     NEW: {new_viet}")
            else:
                already_good += 1
        else:
            # Check if it already has proper diacritics
            if current_viet and any(c in current_viet for c in 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'):
                already_good += 1
            else:
                not_found.append((name, current_viet))
    
    print(f"\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Fixed: {fixed}")
    print(f"   ⏭️  Already good: {already_good}")
    print(f"   ⚠️  Not in fix list: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Items not in fix list (may need review):")
        for name, current in not_found:
            print(f"   - {name}: '{current}'")
    
    # Save
    with open(menu_path, 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {menu_path}")


if __name__ == "__main__":
    main()
