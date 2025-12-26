import json
import re
import logging
import config
from openai import OpenAI
from backend.rag_retriever import get_retriever

# Configure logging
logger = logging.getLogger("gac_waiter.agent")


def clean_llm_response(text: str) -> str:
    """Remove LLM thinking tags and cleanup the response."""
    if not text:
        return text
    
    # Remove <think>...</think> blocks (including multiline)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Remove any remaining opening/closing tags
    text = re.sub(r'</?think>', '', text)
    
    # Clean up extra whitespace resulting from removal
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

class WaitstaffAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.client = OpenAI(
            base_url=config.LLM_BASE_URL,
            api_key=config.LLM_API_KEY,
            timeout=180.0  # 3 minute timeout for slow CPU inference
        )
        self.model = config.LLM_MODEL
        logger.info(f"Agent initialized with model: {self.model}")
        self.last_mentioned_items = []


    def lookup_menu(self, query: str, language: str = "English") -> str:
        """Search for items in the menu."""
        items = self.retriever.retrieve_items(query, top_k=5)
# Note: Filter for menu_items only? The retriever currently mixes them but marks type.
# For specific menu lookup, we might want to prioritize 'menu_item'.
        if not items:
            return "No menu items found matching that query."
        
        # Track found items for the UI
        self.last_mentioned_items.extend([i for i in items if i.get('type') != 'general_info'])
        
        result = "Found Menu Items:\n"
        for item in items:
            if item.get('type') == 'general_info': continue # Skip regular info for menu lookup
            
            # Show Vietnamese name first when in Vietnamese mode
            if language.lower() == "vietnamese" and item.get('item_viet'):
                result += f"- {item.get('item_viet')} (${item.get('price', 0):.2f})\n"
                result += f"  EN: {item.get('item_name')}\n"
                if item.get('pronunciation'):
                    result += f"  Phát âm: {item.get('pronunciation')}\n"
            else:
                result += f"- {item.get('item_name')} (${item.get('price', 0):.2f})\n"
            
            if item.get('popular'):
                result += "  [PHỔ BIẾN]\n" if language.lower() == "vietnamese" else "  [POPULAR]\n"
            result += f"  Mô tả: {item.get('description', '')}\n" if language.lower() == "vietnamese" else f"  Desc: {item.get('description', '')}\n"
        return result

    def lookup_info(self, query: str) -> str:
        """Search for general restaurant info (owner, history, location, etc)."""
        items = self.retriever.retrieve_items(query, top_k=3)
        
        if not items:
            return "No specific info found."
            
        result = "Found Information:\n"
        for item in items:
            # We accept both types here as menu items might be relevant to info (e.g. signature dishes)
            name = item.get('item_name') or item.get('topic')
            content = item.get('content') or item.get('description')
            result += f"- {name}: {content}\n"
        return result

    def run(self, messages: list, current_language: str = "English") -> dict:
        self.last_mentioned_items = [] # Reset for this turn
        """
        Run the ReAct loop to process the conversation.
        Returns: { "text": str, "language": str }
        """
        # 1. Prepare Tools and System Prompt
        tools_desc = """
1. lookup_menu(query: str): Search for dishes, prices, ingredients. usage: Action: lookup_menu\nAction Input: query
2. lookup_info(query: str): Search for owner, location, history, policies, AND SPECIALS. usage: Action: lookup_info\nAction Input: query
3. set_language(language: str): Set the current session language. usage: Action: set_language\nAction Input: language
"""
        # Track the language state locally for this turn
        detected_language = current_language
        
        system_prompt = f"""You are Kristin, an intelligent waiter at Garlic & Chives.
You have access to the following tools to answer customer questions accurately:

{tools_desc}

Current Language Preference: {current_language}. 
You MUST respond in this language ({current_language}) unless the user explicitly requests a switch using `set_language`.
If the language is Vietnamese, write purely in Vietnamese using the Latin alphabet (Quốc ngữ). DO NOT use Thai, Cyrillic, Chinese, or any other non-Latin scripts.
Methodically translate your thoughts to {current_language} before outputting.

PROTOCOL:
1. Review the customer's input.
2. If the user asks to speak another language, use `set_language`.
3. If the customer asks for **specials (lunch, dinner, daily)**, ALWAYS use `lookup_info` first to check for "Specials of the Day" or policies.
   - Do NOT use `lookup_menu` for generic 'special' queries unless you are looking for a specific named dish.
4. If you need facts (prices, ingredients, owner name), use a tool. 
   - Output: 
     Action: [tool_name]
     Action Input: [query]
5. If you have enough info or it's just chit-chat, respond directly to the customer.
   - Output: [Final Answer]

ORDER WORKFLOW (CRITICAL - Follow this order):
1. **Exploration**: Help customers browse the menu, answer questions about dishes.
2. **Taking Orders**: When customer orders items, acknowledge each item with its price.
   - Listen for special requests: "no spicy", "extra sauce", "well done", etc.
   - Acknowledge any modifications: "Got it, Pad Thai with no peanuts."
3. **SPECIAL NOTES (IMPORTANT)**: Listen for and acknowledge:
   - Dietary preferences: "no spicy", "vegetarian", "less salt", "no onions"
   - Time constraints: "I'm in a hurry", "only have 30 minutes", "need it quick"
   - Preparation notes: "well done", "sauce on the side", "extra hot"
   - Service notes: "to go", "separate checks", "for here"
   - If customer mentions any of these, repeat back to confirm: "I've noted that you're in a hurry."
4. **ALLERGY CHECK (MANDATORY)**: Before confirming any order, you MUST ask:
   - "Do you have any food allergies we should be aware of?"
   - If they mention allergies, acknowledge and note them.
   - If they say "no allergies", confirm this.
5. **Order Confirmation**: Read back the full order WITH special notes:
   - "Just to confirm: [items with prices], no spicy, and you need it within 30 minutes. Total is $X. Is that correct?"
6. **Finalization**: Only after customer confirms, thank them and let them know the order is being prepared.

CRITICAL RULES:
- NEVER hallucinate menu items or prices. ALWAYS verify with lookup_menu.
- If asking about the owner or history, ALWAYS use lookup_info.
- If `lookup_menu` returns items, ensure they actually match the user's request. Do not claim an item is a "Lunch Special" just because it appeared in the search results.
- If no specific lunch specials are found in `lookup_info`, politely state that you can check the daily specials instead.
- **Only provide Vietnamese names and pronunciations if the current language is Vietnamese or if the user explicitly asks for them.** Do not volunteer this information in English conversation.
- **ALWAYS ask about allergies before confirming an order. This is a safety requirement.**
- Be concise and friendly.
- Do not expose the tool usage to the user in the final answer.
"""

        # Construct message history for LLM
        # We process the last user message to decide on action
        current_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Max steps to prevent loops
        max_steps = 3
        
        # Token tracking
        total_prompt_tokens = 0
        total_completion_tokens = 0
        
        for step in range(max_steps):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=current_messages,
                # stop=["Observation:"] # DISABLE STOP FOR DEBUGGING
            )
            
            # Extract token usage
            if hasattr(response, 'usage') and response.usage:
                prompt_tokens = response.usage.prompt_tokens or 0
                completion_tokens = response.usage.completion_tokens or 0
                total_prompt_tokens += prompt_tokens
                total_completion_tokens += completion_tokens
                logger.debug(f"TOKEN USAGE Step {step+1}: Prompt={prompt_tokens}, Completion={completion_tokens}")
            
            logger.debug(f"Messages sent: {json.dumps(current_messages[-1])}")
            
            try:
                content = response.choices[0].message.content
                if content is None: content = ""
                content = content.strip()
                
                # Clean up <think> tags from LLM response
                content = clean_llm_response(content)
                
                logger.debug(f"Cleaned Content: '{content[:200]}...'")
            except Exception as e:
                logger.debug(f"Error extracting content: {e}")
                content = ""
                
            logger.info(f"Agent Step {step+1}: {content[:200]}...")
            
            # Check for Action
            if "Action:" in content and "Action Input:" in content:
                # Parse action
                try:
                    action_line = [l for l in content.split('\n') if "Action:" in l][0]
                    input_line = [l for l in content.split('\n') if "Action Input:" in l][0]
                    
                    tool = action_line.split("Action:")[1].strip()
                    query = input_line.split("Action Input:")[1].strip()
                    
                    # Execute
                    observation = ""
                    if tool == "lookup_menu":
                        observation = self.lookup_menu(query, detected_language)
                    elif tool == "lookup_info":
                        observation = self.lookup_info(query)
                    elif tool == "set_language":
                        detected_language = query
                        observation = f"Language set to {detected_language}. Please respond in {detected_language} from now on."
                    else:
                        observation = f"Error: Tool {tool} not found."
                        
                    logger.debug(f"Tool Output: {observation[:100]}...")
                    
                    # Append result to history
                    current_messages.append({"role": "assistant", "content": content})
                    current_messages.append({"role": "user", "content": f"Observation: {observation}"})
                    
                except Exception as e:
                    logger.error(f"Parsing Error: {e}")
                    # If parsing fails, just return the content as is or try again?
                    # Usually better to break and ask user
                    return {
                        "text": content, 
                        "language": detected_language,
                        "mentioned_items": self.last_mentioned_items,
                        "token_usage": {
                            "prompt_tokens": total_prompt_tokens,
                            "completion_tokens": total_completion_tokens,
                            "total_tokens": total_prompt_tokens + total_completion_tokens
                        }
                    }
            else:
                # No action, this is the final answer
                return {
                    "text": content, 
                    "language": detected_language,
                    "mentioned_items": self.last_mentioned_items,
                    "token_usage": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens
                    }
                }

        return {
            "text": "I apologize, I'm having trouble connecting to the system right now. Could you ask that again?", 
            "language": detected_language,
            "mentioned_items": [],
            "token_usage": {
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens
            }
        }
