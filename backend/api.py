import sys
import os
import re
import time
import logging
from collections import defaultdict
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gac_waiter.api")

logger.info(f"API STARTING - VERSION ID: {time.time()}")

# Add project root to path to allow importing config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CRITICAL: Load .env file explicitly
from dotenv import load_dotenv
load_dotenv(override=True)

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import base64
import config

# Print config on startup for debugging
logger.info("=" * 60)
logger.info("Backend API Starting - Configuration:")
logger.info(f"LLM_BASE_URL: {config.LLM_BASE_URL}")
logger.info(f"LLM_MODEL: {config.LLM_MODEL}")
logger.info(f"API_PORT: {config.API_PORT}")
logger.info("=" * 60)

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

# ============== RATE LIMITING ==============
rate_limit_store = defaultdict(list)
RATE_LIMIT_REQUESTS = 30  # requests per window
RATE_LIMIT_WINDOW = 60    # seconds

def rate_limiter(func):
    """Simple rate limiter decorator."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old requests
        rate_limit_store[client_ip] = [
            t for t in rate_limit_store[client_ip] 
            if current_time - t < RATE_LIMIT_WINDOW
        ]
        
        # Check rate limit
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")
        
        # Record this request
        rate_limit_store[client_ip].append(current_time)
        
        return await func(request, *args, **kwargs) if hasattr(func, '__await__') else func(*args, **kwargs)
    return wrapper

# ============== REQUEST MODELS WITH VALIDATION ==============
class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., max_items=100, description="Conversation history")
    language: Optional[str] = Field(default="English", max_length=20)
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('Messages cannot be empty')
        for msg in v:
            content = str(msg.get('content', ''))
            if len(content) > 10000:
                raise ValueError('Message content too long (max 10000 chars)')
        return v
    
    class Config:
        extra = "allow"

class CheckOutRequest(BaseModel):
    messages: List[Dict[str, Any]] = Field(..., max_items=100)
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError('Messages cannot be empty')
        return v
    
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
        
        # FINAL CLEANUP: Strip <think> tags from response before sending to frontend
        if response_text:
            response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
            response_text = re.sub(r'</?think>', '', response_text)
            response_text = response_text.strip()
        
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
        logger.error(f"API Error: {e}")
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
        logger.error(f"TTS Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/checkout")
def checkout_endpoint(request: CheckOutRequest):
    """Analyzes conversation history to generate a structured order."""
    try:
        import json
        from openai import OpenAI
        
        sys_p = """You are an Order Parser for a restaurant. 
Your job is to extract the final accepted order and ALL special notes from the conversation.

PARSING RULES:
1. Extract only items that were CONFIRMED by the customer (not just discussed).
2. Ignore items that were mentioned but rejected or removed.
3. For each item, extract the exact name, quantity, and price.
4. Calculate the correct total.

ALLERGY EXTRACTION (CRITICAL):
- Search the ENTIRE conversation for any mention of allergies.
- Common allergy mentions: "allergic to", "allergy", "can't eat", "avoid", "intolerant"
- Common allergens: Peanuts, Tree Nuts, Shellfish, Fish, Milk/Dairy, Eggs, Wheat/Gluten, Soy, Sesame
- If customer says "no allergies" or "none", set allergies to empty array.
- If allergies are never discussed, set allergy_checked to false.

SPECIAL NOTES EXTRACTION (IMPORTANT):
Extract ALL special requests, preferences, and constraints mentioned by the customer:
- Dietary preferences: "no spicy", "less salt", "extra sauce", "vegetarian", "no onions"
- Time constraints: "in a hurry", "only have 30 minutes", "need it quick", "rushing"
- Preparation notes: "well done", "on the side", "no ice", "extra hot"
- Seating/service: "to go", "for here", "separate checks"
- Any other customer-specific requests

Output JSON structure: 
{
  "order": [
    {"name": "Item Name", "qty": 1, "price": 10.0, "notes": "no onions, extra spicy"}
  ],
  "allergies": ["Peanut", "Shellfish"],
  "allergy_checked": true,
  "special_notes": [
    "Customer is in a hurry - only 30 minutes",
    "No spicy food",
    "To go order"
  ],
  "total": 0.0
}

IMPORTANT:
- allergy_checked: true if allergies were discussed, false if never asked
- allergies: array of allergies mentioned, empty [] if customer said "none"
- special_notes: array of ALL special requests/constraints, empty [] if none
- For item-specific notes (like "Pad Thai no peanuts"), add to item's "notes" field
- No markdown, just valid JSON.
"""
        full_msgs = [{"role": "system", "content": sys_p}] + request.messages
        
        client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=180.0  # 3 minute timeout for slow CPU inference
        )
        
        completion = client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=full_msgs,
            response_format={"type": "json_object"}
        )
        order_json_str = completion.choices[0].message.content
        
        # Clean <think> tags from response
        if order_json_str:
            order_json_str = re.sub(r'<think>.*?</think>', '', order_json_str, flags=re.DOTALL)
            order_json_str = re.sub(r'</?think>', '', order_json_str)
            order_json_str = order_json_str.strip()
        
        order_data = json.loads(order_json_str)
        
        # VALIDATION: Ensure all ordered items exist in menu
        from backend.rag_retriever import get_retriever
        retriever = get_retriever()
        
        ordered_items = [item.get('name', '') for item in order_data.get('order', [])]
        is_valid, invalid_items = retriever.validate_items(ordered_items)
        
        if not is_valid:
            logger.warning(f"Invalid items in order: {invalid_items}")
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
        logger.error(f"Checkout Error: {e}")
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
