from backend.agent import WaitstaffAgent
import logging

# Setup basic logging to see agent internals
logging.basicConfig(level=logging.INFO)

print("Initializing Agent...")
agent = WaitstaffAgent()

print("\n--- TEST: Allergy Input ---")
messages = [{"role": "user", "content": "I am allergic to peanut and I don't like spicy food."}]
result = agent.run(messages)

print("\n--- RESULT ---")
print(f"Text Response: {result.get('text')}")
print(f"General Note: {result.get('general_note')}")
print(f"Cart Updates: {result.get('cart_updates')}")

if result.get('general_note'):
    print("\nSUCCESS: General note was set.")
else:
    print("\nFAILURE: General note was NOT set.")
