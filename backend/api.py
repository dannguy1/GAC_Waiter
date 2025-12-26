import sys
import os
import time
print(f"CRITICAL: API STARTING - VERSION ID: {time.time()} - SANITIZATION ACTIVE")

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
from backend.agent import WaitstaffAgent

# Initialize singletons
menu_manager = MenuManager()
tts_client = TTSClient()
agent = WaitstaffAgent()

# Create FastAPI app
app = FastAPI(title="GAC Waiter Backend")

# Request Models
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]  # Allow any fields, not just role/content
    language: Optional[str] = "English"
    
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
        
        # Prepare messages
        clean_messages = []
        for msg in request.messages:
            clean_msg = {"role": msg.get("role"), "content": msg.get("content")}
            clean_messages.append(clean_msg)
        
        # AGENT RUN
        # The agent handles tool-use, retrieval, and prompts internally
        # response_text is now a DICT: {"text": str, "language": str}
        agent_result = agent.run(clean_messages, current_language=request.language)
        
        if isinstance(agent_result, dict):
            response_text = agent_result.get("text", "")
            detected_lang = agent_result.get("language", request.language)
        else:
            # Fallback if agent returns string (should not happen with new code)
            response_text = str(agent_result)
            detected_lang = request.language
        
        # Find mentioned items (for UI to display images)
        # We prefer the explicitly found items from the agent's tools
        # But we merge with keyword search just in case the agent mentioned something from memory
        explicit_items = agent_result.get("mentioned_items", [])
        keyword_items = menu_manager.find_items_in_text(response_text)
        
        # Merge (deduplicate by item_name)
        seen_names = set()
        mentioned = []
        
        for item in explicit_items + keyword_items:
            name = item.get('item_name')
            if name and name not in seen_names:
                seen_names.add(name)
                mentioned.append(item)
        
        return {
            "text": response_text,
            "language": detected_lang,
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

@app.post("/v1/reload")
def reload_endpoint():
    """Reloads all data (Menu and RAG) from disk."""
    try:
        menu_manager.reload()
        
        from backend.rag_retriever import get_retriever
        retriever = get_retriever()
        retriever.reload()
        
        # Also re-initialize agent's retriever reference if needed, 
        # though agent calls get_retriever() or uses the singleton which is mutated.
        # Ideally agent should check for staleness or we rely on the mutable singleton.
        
        return {"status": "success", "message": "Data reloaded successfully"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=config.API_PORT)
