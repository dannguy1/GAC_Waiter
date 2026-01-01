import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from backend.agent import WaitstaffAgent

def test_filtering():
    agent = WaitstaffAgent()
    
    # Mock candidate items (what lookup_menu would return)
    # Based on menu.json
    candidates = [
        {
            "item_name": "Carmelized Catfish",
            "item_viet": "Cá Kho Tộ",
            "price": 17,
            "description": "Catfish caramelized in sauce"
        },
        {
            "item_name": "Fish Hotpot",
            "item_viet": "Lẩu Canh Chua Cá",
            "price": 12,
            "description": "Small catfish in sweet-and-sour soup",
            "category": "Soup"
        },
        {
            "item_name": "Baked Crispy Catfish w. Boiled Pork", 
            "item_viet": "Cá Nướng Da Giòn Thịt Luộc",
            "price": 22,
            "description": "Crispy baked catfish"
        }
    ]
    
    # The text response from the user's report
    llm_response = """We have three catfish dishes:

Carmelized Catfish ($17) – Caramelized in sauce, served with crispy rice.
Fish Hotpot ($12) – Small catfish in sweet-and-sour soup with beansprouts, herbs, pineapple, okra, and tomatoes.
Baked Crispy Catfish with Boiled Pork ($22) [Popular] – Crispy baked catfish with poached pork (please allow 1 hour for preparation).
Would you like to add one of these to your order?"""

    print(f"Testing filtering with content:\n---\n{llm_response}\n---\n")
    
    filtered = agent._filter_mentioned_items(llm_response, candidates)
    
    print(f"Found {len(filtered)} items:")
    for item in filtered:
        print(f"- {item['item_name']}")

    expected = ["Carmelized Catfish", "Fish Hotpot", "Baked Crispy Catfish w. Boiled Pork"]
    found_names = [i['item_name'] for i in filtered]
    
    missing = [name for name in expected if name not in found_names]
    
    if missing:
        print(f"\nFAILED: Missing items: {missing}")
    else:
        print("\nSUCCESS: All items found.")

if __name__ == "__main__":
    test_filtering()
