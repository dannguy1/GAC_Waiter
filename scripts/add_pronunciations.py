import json
import os
import sys
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from openai import OpenAI
from tqdm import tqdm

MENU_PATH = config.MENU_PATH

def add_pronunciations():
    print(f"Loading menu from {MENU_PATH}...")
    with open(MENU_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    client = OpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        timeout=60.0
    )
    
    updated_count = 0
    
    items = data.get("items", [])
    
    # Process items that have item_viet but no pronunciation
    for item in tqdm(items, desc="Processing Items"):
        item_viet = item.get("item_viet", "")
        if item_viet and (not item.get("pronunciation") or item["pronunciation"] == ""):
            print(f"Generating for: {item_viet}")
            try:
                # Prompt the LLM
                response = client.chat.completions.create(
                    model=config.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides phonetic pronunciations for Vietnamese words for English speakers."},
                        {"role": "user", "content": f"Provide a simple English phonetic pronunciation guide for this Vietnamese text: '{item_viet}'. Return ONLY the phonetic string, nothing else. Example: 'Pho' -> 'Fuh'."}
                    ],
                    temperature=0.3
                )
                pronunciation = response.choices[0].message.content.strip().strip('"')
                item["pronunciation"] = pronunciation
                updated_count += 1
            except Exception as e:
                print(f"\nError processing '{item_viet}': {e}")
                
    # Save back
    if updated_count > 0:
        print(f"Saving {updated_count} new pronunciations...")
        with open(MENU_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Done.")
    else:
        print("No new pronunciations needed.")

if __name__ == "__main__":
    add_pronunciations()
