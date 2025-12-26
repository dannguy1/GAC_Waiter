#!/usr/bin/env python3
"""
Apply Vietnamese translations to menu.json
This script contains manually translated Vietnamese descriptions for all menu items.
"""

import json
import os
import sys

# Vietnamese translations - indexed by item_name
TRANSLATIONS = {
    "Salt & Pepper Garlic Butter Pork Chops": "Thưởng thức món Sườn heo muối tiêu bơ tỏi, với từng miếng sườn thấm đẫm gia vị, quyện béo bùi của bơ tỏi, chiên giòn vàng ruộm, mang đến bản hòa tấu hương vị tuyệt vời trong từng miếng cắn.",
    
    "House Special Squid": "Khám phá món Mực đặc biệt của nhà hàng, với mực tươi ngon được ướp gia vị bí truyền, tẩm bột mỏng và chiên giòn vàng, ăn kèm nước chấm chua ngọt hấp dẫn không thể cưỡng lại.",
    
    "House Special Lobster with Garlic Noodles (priced by lbs)": "Thưởng thức sự xa hoa với món Tôm hùm đặc biệt, thịt tôm hùm ngọt thơm hòa quyện cùng mì tỏi béo ngậy, tất cả được kết hợp với sốt đặc biệt, tạo nên món ăn vừa sang trọng vừa thỏa mãn.",
    
    "Grilled Salmon in Seafood Sauce with Garlic Rice": "Thưởng thức món Cá hồi nướng với hương vị đậm đà được tôn lên bởi sốt hải sản thơm ngon, ăn kèm cơm tỏi thơm phức, tạo nên món ăn vừa đủ đầy vừa tinh tế.",
    
    "Sticky Rice with Mango": "Xôi nếp dẻo ngọt ăn kèm xoài tươi chín thơm.",
    
    "Creme Brulee": "Kết thúc bữa ăn với món Crème Brûlée, lớp custard mịn màng hương vani dưới lớp đường caramel giòn tan hoàn hảo, mang đến độ giòn thú vị tiếp nối bởi vị béo ngọt mượt mà tuyệt vời.",
    
    "Garlic Butter Chicken": "Cánh gà chiên giòn xào bơ tỏi thơm phức, rắc tỏi phi giòn lên trên.",
    
    "Baked Corn Cheese": "Bắp nướng trên chảo gang nóng, phủ phô mai mozzarella kéo sợi.",
    
    "Egg rolls": "Thưởng thức Chả giò giòn rụm, nhân thịt heo xay, tôm, rau củ và miến, cuốn và chiên vàng giòn hoàn hảo, ăn kèm nước mắm pha để cân bằng giữa độ giòn và hương vị.",
    
    "Chicken Satay": "Thưởng thức món Gà sa tế xiên que, với gà ướp mềm được nướng khói thơm hoàn hảo, ăn kèm sốt đậu phộng béo bùi ngọt ngào.",
    
    "Holy Crunchy Chicken wings": "Cánh gà chiên giòn tuyệt hảo với sốt chua ngọt cay, rắc tỏi phi giòn lên trên.",
    
    "Fried Sweet Potatoes": "Khoai lang chiên giòn thơm ngon.",
    
    "Salmon Belly Chien Gion": "Bụng cá hồi tẩm gia vị tỏi và chiên giòn rụm. Ăn kèm sốt đặc biệt của nhà hàng.",
    
    "Toothpick Lamb": "Khám phá hương vị món Cừu xiên que, với những miếng cừu mềm ngon được ướp gia vị, xiên và nướng chín tới hoàn hảo, mang đến hương vị tinh túy trong từng miếng nhỏ.",
    
    "Corn with Dried Shrimp": "Bắp xào gia vị đặc biệt của nhà hàng, rắc tôm khô lên trên.",
    
    "Pho French Dip": "Trải nghiệm sự giao thoa văn hóa với món Phở French Dip, nơi nước dùng phở thơm ngon đậm đà kết hợp với bánh mì sandwich kiểu Pháp, kẹp thịt bò thái mỏng và nước dùng phở để chấm.",
    
    "Shrimp Roll": "Thưởng thức độ tươi ngon của Gỏi cuốn tôm, với tôm biển, rau giòn và rau thơm cuốn trong bánh tráng mỏng, ăn kèm nước chấm đậu phộng chua ngọt.",
    
    "Grilled Pork Sausage Roll": "Nem nướng, rau thơm, bún, hẹ, cuốn trong bánh tráng. Ăn kèm sốt đặc biệt của đầu bếp.",
    
    "Vegetable Roll": "Thưởng thức Gỏi cuốn chay, với rau củ tươi, rau thơm và đậu hũ cuốn trong bánh tráng, mang đến vị tươi mát trong từng miếng cắn, ăn kèm nước chấm đậm đà.",
    
    "Grilled Pork Spring Roll": "Thịt nướng, rau xà lách & rau thơm, dưa leo, bún, hẹ cuốn trong bánh tráng, ăn kèm nước mắm pha đặc biệt.",
    
    "Salmon Belly Roll": "Bụng cá hồi, rau thơm, dưa leo, cuốn trong bánh tráng, ăn kèm sốt me.",
    
    "Beef Roll": "Bò xào sả, rau xà lách tươi, củ cải và cà rốt ngâm chua, vỏ hoành thánh giòn cuốn trong bánh tráng. Ăn kèm nước mắm pha đặc biệt.",
    
    "Poke Roll": "Cá ngừ Ahi sống, rau xà lách tươi, bơ, củ cải và cà rốt ngâm chua, vỏ hoành thánh giòn cuốn trong bánh tráng. Ăn kèm nước tương đặc biệt và wasabi.",
    
    "Pork and Shrimp Roll": "Tôm biển, thịt heo, rau thơm, bún, hẹ, ăn kèm sốt đậu phộng của đầu bếp.",
    
    "Shrimp and Pork Mustard Green": "Tôm và thịt heo cuốn trong lá cải bẹ xanh.",
    
    "Tiger Shrimp and Mango Salad": "Tôm sú đen ướp gia vị ăn kèm gỏi xoài.",
    
    "Ahi Poke Salad (Seared)": "Cá ngừ áp chảo trên nền rau xà lách, rong biển, hành tây và hẹ giòn. Ăn kèm sốt wasabi.",
    
    "Green Papaya Beef Jerky Salad": "Gỏi đu đủ xanh với khô bò, rau thơm và đậu phộng rang.",
    
    "Thai Calamari Salad": "Mực nướng với đu đủ, xoài thái sợi, hành tây, rau thơm, đậu phộng và hành phi, trộn nước mắm chua ngọt.",
    
    "Baby Clam Salad": "Nghêu, bắp cải, bông chuối, rau thơm, đậu phộng và hành phi. Ăn kèm nước mắm chua ngọt.",
    
    "Grilled Salmon Salad": "Cá hồi nướng trên nền rau xanh, rau thơm và hành tây với sốt kem.",
    
    "Ahi Poke Salad": "Cá ngừ ướp mè trên nền rau xanh với sốt wasabi.",
    
    "Lotus Root Salad": "Ngó sen, thịt heo, tôm, hành tây, đậu phộng, cà rốt, dưa leo, cần tây trộn nước mắm chua ngọt.",
    
    "Beef Ong Choy Salad": "Rau muống xé nhỏ, rau thơm, củ cải và cà rốt ngâm chua, hành tây và đậu phộng trộn nước mắm chua ngọt.",
    
    "Thai Beef Salad": "Thăn bò ướp kiểu Thái nướng trên nền rau xanh, dưa leo, cần tây, hành tây, đậu phộng và trộn nước mắm chua ngọt.",
    
    "Rice paper Salad": "Khô bò thái sợi, xoài xanh, rau thơm, đậu phộng trộn nước mắm chua ngọt.",
    
    "Lime Beef Salad": "Thăn bò thái mỏng ngâm chanh trộn với rau thơm, hành tây, đậu phộng và nước mắm chua ngọt.",
    
    "Pomelo Salad": "Bưởi, tôm biển, thịt heo, bông chuối, cà rốt, hành tây, rau thơm, đậu phộng trộn nước mắm đặc biệt.",
    
    "Hamachi Yellowtail Sashimi Salad": "Cá cam tươi sashimi, rau thơm, bông chuối, ngó sen, đậu phộng ăn kèm nước tương và wasabi.",
    
    "Mango and Papaya Salad": "Xoài, đu đủ thái sợi, rau thơm, hành tây, cà chua và đậu phộng trộn nước mắm đặc biệt.",
    
    "Pineapple Salad": "Dứa tươi, rau thơm, rau xà lách, thịt heo, tôm, khô cá và đậu phộng trộn nước mắm đặc biệt.",
    
    "Chicken Salad": "Thưởng thức hương vị tươi ngon của Gỏi gà, với gà xé sợi trộn cùng rau củ giòn, chanh, rau thơm và đậu phộng rang.",
    
    "Tamarind Crab": "Cua rang me cay.",
    
    "Ong Choy with Pork Belly and Seasnails": "Rau muống xào ba chỉ và ốc biển.",
    
    "Baked Clams with Chili Garlic": "Nghêu nướng rắc đậu phộng, hành phi giòn và dầu tỏi ớt.",
    
    "Sauteed Sea Snails": "Ốc hương xào bơ tỏi trên nền hành tây xèo xèo.",
    
    "Clams in Lemongrass Soup": "Nghêu hấp trong nước dùng sả cay.",
    
    "Chili Lemongrass Sea Snail Soup": "Ốc hương hấp trong nước dùng sả ớt cay.",
    
    "Deep Fried Calamari": "Mực lăn bột gia vị tỏi và xào bơ tỏi với ớt jalapeño và hành tây.",
    
    "Baked Clams": "Nghêu nướng rắc đậu phộng, hành phi giòn và hành tây.",
    
    "Basil Clams": "Nghêu xào húng quế, hành tây và ớt jalapeño.",
    
    "Chili Dungeness Crab": "Cua Singapore rang ớt - ăn kèm quẩy và bánh mì baguette.",
    
    "Charbroiled Blk Tiger on Garlic Noodles": "Tôm sú đen ướp gia vị nướng than, ăn kèm mì xào bơ tỏi.",
    
    "Salt and Pepper Shrimp": "Tôm lớn chiên giòn xào bơ tỏi, hành tây và ớt jalapeño.",
    
    "Ong Choy with Seasnails": "Rau muống xào ốc biển.",
    
    "Grilled Blood Clams": "Sò huyết nướng rắc đậu phộng, tỏi phi và hẹ giòn.",
    
    "Shrimp Skewers": "Tôm lớn ướp gia vị nướng xiên que, phục vụ trên chảo gang nóng.",
    
    "Baked King Crab Legs": "Chân cua hoàng đế nướng phủ sốt aioli, tỏi phi và hẹ giòn.",
    
    "Grilled Calamari": "Mực ướp kiểu Thái nướng với hành tây, tỏi giòn và ớt jalapeño.",
    
    "Grilled Scallops": "Thưởng thức món Sò điệp nướng, với sò điệp tươi được nướng hoàn hảo, ướp gia vị đặc trưng Việt Nam, phục vụ trên vỏ sò mang đến trải nghiệm hải sản thanh lịch đầy hương vị.",
    
    "Razor Clams": "Ốc móng tay nướng rắc đậu phộng, tỏi ớt và ớt chuông.",
    
    "Coconut Seasnails": "Ốc len nhỏ nấu trong nước dừa với hành tây, tỏi và ớt.",
    
    "Spicy Baby Clams on Rice Chips": "Hến xào đậu phộng, hành tây, tỏi và rau thơm, ăn kèm bánh tráng mè giòn.",
    
    "Lemongrass Seafood Soup": "Nghêu, mực và tôm hấp trong nước dùng hải sản sả cay.",
    
    "House-Special Garlic Crab": "Cua Dungeness chiên gia vị đặc biệt của nhà hàng, xào bơ tỏi, hành tây và ớt jalapeño, rắc tỏi phi giòn.",
    
    "House Special Lobster": "Tôm hùm xào với sốt đặc biệt của nhà hàng cùng tỏi, hành tây và ớt jalapeño.",
    
    "Baked Crispy Catfish w. Boiled Pork": "Cá nướng da giòn với thịt heo luộc. Vui lòng chờ 1 giờ để chuẩn bị.",
    
    "Ong choy with Beef": "Rau muống xào thịt bò thái lát.",
    
    "Shaken Tofu": "Đậu hũ chiên xào hành tây, ớt chuông và nấm. Ăn kèm cơm.",
    
    "Lamb Chops": "Sườn cừu nướng thơm ngon.",
    
    "Chicken Curry": "Gà còn xương om cà ri kiểu Việt với khoai môn và khoai tây. Ăn kèm bánh mì, cơm hoặc bún.",
    
    "Sizzling Filet Mignon": "Thăn bò ướp gia vị nướng với trứng ốp la, xúc xích và pate. Chọn bánh mì hoặc cơm.",
    
    "Seafood Chowfun": "Hủ tiếu xào hải sản tổng hợp, giá đỗ và hành lá.",
    
    "Chicken Chowfun": "Hủ tiếu xào gà, giá đỗ và hành lá.",
    
    "Sauteed Beef and Garlic Noodles": "Bò thái lát xào mì tỏi thơm phức.",
    
    "Vegetarian Egg Noodles": "Mì trứng chay với rau củ xào.",
    
    "Chicken Egg Noodles": "Mì trứng xào gà và rau củ.",
    
    "Seafood Egg Noodles": "Mì trứng xào hải sản tổng hợp.",
    
    "Pork Chop/Egg/Garlic Fries": "Sườn heo nướng với trứng ốp la và khoai tây chiên tỏi.",
    
    "Combination Egg Noodles": "Mì trứng xào thập cẩm với hải sản và thịt.",
    
    "Chicken Garlic Noodles": "Mì tỏi xào gà.",
    
    "Beef Egg Noodles": "Mì trứng xào bò.",
    
    "Beef Chowfun": "Hủ tiếu xào bò, giá đỗ và hành lá.",
    
    "Shaken Filet Mignon": "Thăn bò lúc lắc xào hành tây và ớt chuông. Ăn kèm cơm.",
    
    "Goat Curry": "Dê còn xương om cà ri kiểu Việt với khoai môn và khoai tây. Ăn kèm bánh mì, cơm hoặc bún.",
    
    "Combination Chowfun": "Hủ tiếu xào thập cẩm với hải sản và thịt.",
    
    "Pad Thai": "Mì xào Thái với tôm, đậu phộng, giá đỗ và trứng.",
    
    "Stir Fried Glass Noodles Crab & Shrimp": "Miến xào cua và tôm.",
    
    "Shrimp Chowfun": "Hủ tiếu xào tôm, giá đỗ và hành lá.",
    
    "Vegetarian Chowfun": "Hủ tiếu xào chay với đậu hũ và rau củ.",
    
    "Grilled Chicken Garlic Noodles": "Gà nướng ăn kèm mì tỏi.",
    
    "Stir-Fried Eggplant with Crispy Pork": "Cà tím xào thịt heo chiên giòn.",
    
    "Fried Rice": "Cơm chiên với trứng và rau củ.",
    
    "Salted Fish Rice": "Cơm chiên cá mặn.",
    
    "Grilled Pork Rice": "Cơm thịt heo nướng.",
    
    "Ong Choy with Pork Belly": "Rau muống xào ba chỉ.",
    
    "Thai Hotpot": "Lẩu Thái cay nồng với hải sản và rau củ.",
    
    "Fish Head Hotpot": "Lẩu đầu cá với rau củ tươi.",
    
    "Fish Hotpot": "Lẩu cá với nước dùng đậm đà và rau củ tươi.",
    
    "Lobster and Seafood Hotpot": "Lẩu tôm hùm và hải sản tổng hợp.",
    
    "Salmon Hotpot": "Lẩu cá hồi với rau củ tươi.",
    
    "Seabass w. Prawn Hot Pot": "Lẩu cá vược và tôm với rau củ tươi.",
    
    "Szechwan Hotpot": "Lẩu Tứ Xuyên cay nồng the.",
    
    "Goat Hot Pot": "Lẩu dê với nước dùng đậm đà.",
    
    "Filet Mignon Hot Pot": "Lẩu thăn bò với nước dùng đậm đà.",
    
    "Oxtail Hotpot": "Lẩu đuôi bò với nước dùng đậm đà.",
    
    "Vietnamese Soup": "Canh Việt Nam truyền thống với rau củ tươi.",
    
    "Water Spinach Noodle Soup": "Mì rau muống trong nước dùng trong.",
    
    "Vietnamese Hot and Sour Soup": "Canh chua Việt Nam với rau củ và tôm.",
    
    "Purple Yam Soup": "Chè khoai môn tím ngọt thanh.",
    
    "Tofu and Fish Soup": "Canh đậu hũ và cá với rau thơm.",
    
    "Mustard Green Soup": "Canh cải bẹ xanh với thịt bằm.",
    
    "Carmelized Salmon": "Cá hồi kho tộ đậm vị.",
    
    "Grilled Salmon w. Tamarind Sauce": "Cá hồi nướng với sốt me chua ngọt.",
    
    "Caramelized Catfish w. Pork Belly": "Cá basa kho tộ với ba chỉ.",
    
    "Caramelized Peppered Pork Belly": "Thịt ba chỉ kho tiêu trong nồi đất.",
    
    "Grilled Salmon": "Cá hồi nướng thơm ngon.",
    
    "Lemongrass Pork Ribs": "Sườn heo nướng sả thơm lừng.",
    
    "Rotisserie Chicken": "Gà quay giòn da.",
    
    "Sticky Rice w. Chinese Sausage, Eggs, Shredded Pork": "Xôi với lạp xưởng, trứng và thịt heo xé sợi.",
    
    "Carmelized Catfish": "Cá basa kho tộ đậm vị.",
    
    "Caramelized Pork Ribs": "Sườn heo kho tộ trong nồi đất.",
    
    "Salmon w. House Special Sauce": "Cá hồi với sốt đặc biệt của nhà hàng.",
    
    "Fried Chili Lemongrass Salmon": "Cá hồi chiên sả ớt cay thơm.",
    
    "Dill and Tumeric Fish": "Chả cá Lã Vọng - Cá chiên nghệ thì là.",
    
    "Sauteed Filet Mignon Vermicelli": "Bún thăn bò xào với rau thơm.",
    
    "Grilled Salmon Noodles": "Bún cá hồi nướng.",
    
    "Grilled Shrimp Noodles": "Bún tôm nướng.",
    
    "Eggroll Noodles": "Bún chả giò giòn rụm.",
    
    "Grilled Filet Mignon Vermicelli": "Bún thăn bò nướng thơm lừng.",
    
    "Grilled Pork Vermicelli": "Bún thịt heo nướng.",
    
    "Noodle Soup": "Phở hoặc bún với nước dùng trong veo.",
    
    "Famous Central VN Spicy Noodles": "Bún bò Huế cay nồng nổi tiếng.",
    
    "Shrimp and Crab Soup": "Súp tôm cua thơm ngon.",
    
    "Hanoi Styled Vermicelli with Grilled Pork": "Bún chả Hà Nội với thịt heo nướng than.",
    
    "Deep Fried Tofu and Boiled Pork Vermicelli": "Bún đậu mắm tôm với đậu hũ chiên và thịt heo luộc.",
    
    "Plain Pho": "Phở không thịt với nước dùng xương bò đậm đà.",
    
    "Shrimp Rice Porridge": "Cháo tôm nóng hổi.",
    
    "Minced Beef Porridge": "Cháo bò bằm thơm ngon.",
    
    "Fish Porridge": "Cháo cá nóng hổi.",
    
    "Minced Pork/Salted Egg Porridge": "Cháo thịt heo bằm với trứng muối.",
    
    "Combination Rice Porridge": "Cháo thập cẩm với nhiều loại thịt.",
    
    "Chicken Porridge": "Cháo gà nóng hổi thơm ngon.",
    
    "Plain Rice Porridge": "Cháo trắng với gia vị.",
    
    "Tofu and Veggie Soup": "Canh đậu hũ và rau củ thanh đạm.",
    
    "Stir-Fried Eggplant": "Cà tím xào tỏi thơm ngon.",
    
    "Fried Tofu": "Đậu hũ chiên giòn.",
    
    "Garlic Spinach": "Rau bina xào tỏi.",
    
    "Vegetarian Salad": "Gỏi chay với rau củ tươi.",
    
    "Ong choy with Garlic": "Rau muống xào tỏi.",
    
    "Green Beans with Garlic": "Đậu que xào tỏi.",
    
    "Stir Fried Bok choy with Garlic": "Cải thìa xào tỏi.",
}


def main():
    menu_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'menu.json')
    
    print("=" * 60)
    print("Applying Vietnamese Translations")
    print("=" * 60)
    
    # Load menu
    with open(menu_path, 'r', encoding='utf-8') as f:
        menu_data = json.load(f)
    
    items = menu_data.get('items', [])
    print(f"\nTotal items: {len(items)}")
    print(f"Translations available: {len(TRANSLATIONS)}")
    
    # Apply translations
    applied = 0
    skipped = 0
    not_found = []
    
    for item in items:
        name = item.get('item_name', '')
        
        # Check if this item needs a translation
        current_viet = item.get('description_viet', '').strip()
        if current_viet and '<think>' not in current_viet:
            skipped += 1
            continue
        
        # Look up translation
        if name in TRANSLATIONS:
            item['description_viet'] = TRANSLATIONS[name]
            applied += 1
            print(f"  ✅ {name}")
        else:
            not_found.append(name)
    
    print(f"\n" + "=" * 60)
    print(f"📊 Summary:")
    print(f"   ✅ Applied: {applied}")
    print(f"   ⏭️  Skipped (already has): {skipped}")
    print(f"   ❌ Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n⚠️  Items without translation:")
        for name in not_found[:20]:
            print(f"   - {name}")
        if len(not_found) > 20:
            print(f"   ... and {len(not_found) - 20} more")
    
    # Save
    with open(menu_path, 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {menu_path}")


if __name__ == "__main__":
    main()
