import sys
import os

# Ensure we can import from local dir
sys.path.append(os.getcwd())

from menu_manager import MenuManager
from tts_client import TTSClient
from llm_client import LLMClient
import config

def verify_menu():
    print("--- Verifying Menu Manager ---")
    mm = MenuManager()
    print(f"Total Items: {len(mm.items)}")
    print("Random Upsell:", mm.get_random_upsell())
    print("Search 'Lobster':", mm.find_items_in_text("I want the House Special Lobster"))
    print("✅ Menu Verified")

def verify_tts():
    print("\n--- Verifying TTS Client ---")
    client = TTSClient()
    text = "Hello, welcome to Garlic and Chives."
    chunk_count = 0
    total_bytes = 0
    for chunk in client.generate_audio(text):
        chunk_count += 1
        total_bytes += len(chunk)
    
    print(f"Generated {chunk_count} chunks, {total_bytes} bytes.")
    if total_bytes > 0:
        print("✅ TTS Verified")
    else:
        print("❌ TTS Failed (No bytes)")

def verify_llm():
    print("\n--- Verifying LLM Client ---")
    client = LLMClient()
    try:
        response = client.get_waiter_response([{"role": "user", "content": "What do you have for dinner?"}], "Menu Context: Burger ($10)")
        print(f"Response: {response}")
        if response:
             print("✅ LLM Verified")
        else:
             print("❌ LLM Empty Response")
    except Exception as e:
        print(f"❌ LLM Failed: {e}")

if __name__ == "__main__":
    verify_menu()
    verify_tts()
    verify_llm()
