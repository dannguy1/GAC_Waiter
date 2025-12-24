import sys
import os

# Add project root to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Load .env file explicitly
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import config

# Print config on startup for debugging
print("=" * 60)
print("Backend API Starting - Configuration:")
print(f"LLM_BASE_URL: {config.LLM_BASE_URL}")
print(f"LLM_MODEL: {config.LLM_MODEL}")
print(f"API_PORT: {config.API_PORT}")
print("=" * 60)

# Import logic classes
from backend.menu_manager import MenuManager
from backend.tts_client import TTSClient

# Initialize singletons
menu_manager = MenuManager()
tts_client = TTSClient()

# Create FastAPI app
app = FastAPI(title="GAC Waiter Backend")

# Request Models
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]  # Allow any fields, not just role/content
    
    class Config:
        extra = "allow"  # Allow extra fields

class CheckOutRequest(BaseModel):
    messages: List[Dict[str, Any]]
    
    class Config:
        extra = "allow"

@app.get("/v1/menu")
def get_menu():
    """Returns the full menu as JSON."""
    return menu_manager.items

@app.post("/v1/chat")
def chat_endpoint(request: ChatRequest):
    try:
        # Get user's latest message for retrieval
        user_message = ""
        if request.messages:
            user_message = request.messages[-1].get('content', '')
        
        # RAG RETRIEVAL: Get only relevant menu items (not entire menu)
        from backend.rag_retriever import get_retriever
        retriever = get_retriever()
        relevant_items = retriever.retrieve_items(user_message, top_k=5)
        
        # Build focused menu context from retrieved items
        menu_context = "RELEVANT MENU ITEMS:\n\n"
        if relevant_items:
            for item in relevant_items:
                menu_context += f"- {item.get('item_name')} (${item.get('price', 0):.2f})"
                if item.get('popular'):
                    menu_context += " [POPULAR]"
                menu_context += f"\n  {item.get('description', '')}\n"
                menu_context += f"  Category: {item.get('category', 'Other')}\n\n"
        else:
            # Fallback: show a few popular items if no relevant items found
            popular_items = [item for item in menu_manager.items if item.get('popular')][:5]
            for item in popular_items:
                menu_context += f"- {item.get('item_name')} (${item.get('price', 0):.2f}) [POPULAR]\n"
                menu_context += f"  {item.get('description', '')}\n\n"

        
        # DIRECT LLM CALL - NO WRAPPER
        from openai import OpenAI
        
        system_prompt = f"""You are Kristin, a friendly restaurant waiter at Garlic & Chives.

{menu_context}

CRITICAL RULES:
- ONLY recommend items from the "RELEVANT MENU ITEMS" list above
- NEVER invent or suggest items not explicitly listed above
- If asked for something not in the list above, politely say you'll check and ask them to rephrase or be more specific
- When customers greet you, introduce yourself as Kristin warmly
- Before finalizing orders, ask about allergies
- Repeat orders back to confirm with exact prices
- Keep responses brief and friendly
- If you're unsure about an item, admit it rather than making up information"""

        # Clean messages - remove 'images' field (only for UI, not for LLM)
        clean_messages = []
        for msg in request.messages:
            clean_msg = {"role": msg.get("role"), "content": msg.get("content")}
            clean_messages.append(clean_msg)
        
        full_messages = [{"role": "system", "content": system_prompt}] + clean_messages
        
        print(f"Calling LLM: {config.LLM_BASE_URL} / {config.LLM_MODEL}")
        
        client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=60.0
        )
        
        response = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=full_messages
        )
        
        response_text = response.choices[0].message.content
        print(f"LLM Response: {response_text[:100]}...")
        
        # Find mentioned items (for UI to display images)
        mentioned = menu_manager.find_items_in_text(response_text)
        
        return {
            "text": response_text,
            "mentioned_items": mentioned
        }
    except Exception as e:
        import traceback
        print(f"API Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/tts")
def tts_endpoint(request: dict = Body(...)):
    """Generate TTS audio on-demand for given text."""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Generate audio using TTS client
        audio_bytes = b"".join(list(tts_client.generate_audio(text)))
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None
        
        return {
            "audio_base64": audio_b64
        }
    except Exception as e:
        import traceback
        print(f"TTS Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/checkout")
def checkout_endpoint(request: CheckOutRequest):
    """Analyzes conversation history to generate a structured order."""
    try:
        import json
        from openai import OpenAI
        
        sys_p = """You are an Order Parser. 
Extract the final accepted order from the conversation. 
Ignore items discussed but rejected.
Check context for any mentioned allergies.
Output JSON structure: 
{
  "order": [
    {"name": "Item Name", "qty": 1, "price": 10.0}
  ],
  "allergies": ["Peanuts", "Shellfish"],
  "total": 0.0
}
If no allergies mentioned, return "allergies": [].
No markdown, just JSON.
"""
        full_msgs = [{"role": "system", "content": sys_p}] + request.messages
        
        client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=60.0
        )
        
        completion = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=full_msgs,
            response_format={"type": "json_object"}
        )
        order_json_str = completion.choices[0].message.content
        order_data = json.loads(order_json_str)
        
        # VALIDATION: Ensure all ordered items exist in menu
        from backend.rag_retriever import get_retriever
        retriever = get_retriever()
        
        ordered_items = [item.get('name', '') for item in order_data.get('order', [])]
        is_valid, invalid_items = retriever.validate_items(ordered_items)
        
        if not is_valid:
            print(f"WARNING: Invalid items in order: {invalid_items}")
            # Filter out invalid items
            order_data['order'] = [
                item for item in order_data['order']
                if item.get('name', '') not in invalid_items
            ]
            # Recalculate total
            order_data['total'] = sum(
                item.get('price', 0) * item.get('qty', 1)
                for item in order_data['order']
            )
        
        return order_data
    except Exception as e:
        print(f"Checkout Error: {e}")
        return {
            "order": [],
            "allergies": [],
            "total": 0.0
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.API_PORT)
