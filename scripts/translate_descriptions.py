#!/usr/bin/env python3
"""
Vietnamese Description Translation Script

This script finds menu items without Vietnamese descriptions and translates them
using the local LLM (Ollama).

Usage:
    python scripts/translate_descriptions.py [--dry-run] [--limit N]

Options:
    --dry-run   Preview items that need translation without making changes
    --limit N   Only translate N items (useful for testing)
"""

import json
import os
import sys
import argparse
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from openai import OpenAI


def load_menu():
    """Load menu data from JSON file."""
    with open(config.MENU_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_menu(menu_data):
    """Save menu data back to JSON file."""
    with open(config.MENU_PATH, 'w', encoding='utf-8') as f:
        json.dump(menu_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved updated menu to {config.MENU_PATH}")


def find_items_without_viet_description(menu_data):
    """Find all items that don't have a Vietnamese description."""
    items_needing_translation = []
    
    for idx, item in enumerate(menu_data.get('items', [])):
        # Check if description_viet is missing or empty
        desc_viet = item.get('description_viet', '').strip()
        # Also check if it contains thinking tags (incomplete cleanup)
        if not desc_viet or '<think>' in desc_viet:
            # Must have an English description to translate
            if item.get('description', '').strip():
                items_needing_translation.append({
                    'index': idx,
                    'item_name': item.get('item_name', 'Unknown'),
                    'item_viet': item.get('item_viet', ''),
                    'description': item.get('description', '')
                })
    
    return items_needing_translation


def clean_llm_response(text):
    """Remove LLM thinking tags and cleanup the response."""
    if not text:
        return text
    
    # Remove <think>...</think> blocks (including multiline)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove any remaining opening/closing tags
    text = re.sub(r'</?think>', '', text)
    
    # Clean up extra whitespace
    text = text.strip()
    
    # Remove quotes if the entire response is quoted
    text = text.strip('"\'')
    
    return text


def translate_description(client, model, description, item_name, item_viet):
    """Translate a single description to Vietnamese using LLM."""
    
    prompt = f"""Translate the following restaurant menu item description from English to Vietnamese.

Item Name (English): {item_name}
Item Name (Vietnamese): {item_viet or 'N/A'}

English Description:
{description}

Rules:
1. Use natural, fluent Vietnamese (Quốc ngữ - Latin alphabet)
2. Keep food-related terms that are commonly used in Vietnamese (e.g., "shrimp" -> "tôm")
3. Maintain the appetizing, descriptive tone
4. Do NOT include any English words unless they are commonly used in Vietnamese cuisine
5. Return ONLY the Vietnamese translation, nothing else

Vietnamese Translation:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional Vietnamese translator specializing in restaurant menus. You translate English food descriptions into natural, appetizing Vietnamese. Output ONLY the translation, no explanations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent translations
        )
        
        translation = response.choices[0].message.content.strip()
        
        # Clean up LLM response (remove thinking tags, quotes, etc.)
        translation = clean_llm_response(translation)
        
        return translation
    
    except Exception as e:
        print(f"  ❌ Translation error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Translate menu descriptions to Vietnamese')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Preview items needing translation without making changes')
    parser.add_argument('--limit', type=int, default=0,
                        help='Limit number of items to translate (0 = all)')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Vietnamese Description Translation Script")
    print("=" * 60)
    
    # Load menu
    print(f"\n📂 Loading menu from: {config.MENU_PATH}")
    menu_data = load_menu()
    total_items = len(menu_data.get('items', []))
    print(f"   Found {total_items} total menu items")
    
    # Find items needing translation
    items_to_translate = find_items_without_viet_description(menu_data)
    print(f"\n🔍 Items without Vietnamese description: {len(items_to_translate)}")
    
    if not items_to_translate:
        print("✅ All items already have Vietnamese descriptions!")
        return
    
    # Show preview
    print("\n📋 Items needing translation:")
    print("-" * 60)
    for i, item in enumerate(items_to_translate[:10]):  # Show first 10
        print(f"  {i+1}. {item['item_name']}")
        print(f"      EN: {item['description'][:60]}...")
    
    if len(items_to_translate) > 10:
        print(f"  ... and {len(items_to_translate) - 10} more")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        return
    
    # Initialize LLM client
    print(f"\n🤖 Connecting to LLM: {config.LLM_BASE_URL}")
    print(f"   Model: {config.LLM_MODEL}")
    
    client = OpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        timeout=120.0
    )
    
    # Apply limit if specified
    if args.limit > 0:
        items_to_translate = items_to_translate[:args.limit]
        print(f"\n⚠️  Limited to {args.limit} items")
    
    # Translate each item
    print(f"\n🔄 Translating {len(items_to_translate)} items...")
    print("-" * 60)
    
    success_count = 0
    error_count = 0
    
    for i, item in enumerate(items_to_translate):
        print(f"\n[{i+1}/{len(items_to_translate)}] {item['item_name']}")
        
        translation = translate_description(
            client, 
            config.LLM_MODEL,
            item['description'],
            item['item_name'],
            item['item_viet']
        )
        
        if translation:
            # Update the menu data
            menu_data['items'][item['index']]['description_viet'] = translation
            print(f"  ✅ VN: {translation[:70]}...")
            success_count += 1
        else:
            error_count += 1
    
    # Save updated menu
    print("\n" + "=" * 60)
    print(f"📊 Translation Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    
    if success_count > 0:
        save_menu(menu_data)
    else:
        print("⚠️  No translations were successful, menu not updated")


if __name__ == "__main__":
    main()
