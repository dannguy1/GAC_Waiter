import streamlit as st
import requests
import base64
import os
import config
import io
import soundfile as sf
import sounddevice as sd

# Page Config
st.set_page_config(page_title="Garlic & Chives Digital Menu", layout="wide", page_icon="🍽️")

# Custom CSS
# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: #4CAF50 !important; /* Fresh Green */
        font-weight: 700;
    }
    
    h1 {
        font-size: 3.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Header/Logo Area */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: transparent;
        color: #4CAF50;
        border: 1px solid #4CAF50;
        border-radius: 25px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #4CAF50;
        color: #fff;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(76, 175, 80, 0.2);
    }
    
    /* Chat Interface */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* User Message */
    .stChatMessage[data-testid="stChatMessage"]:has(div[data-testid="stMarkdownContainer"] > p) {
        /* Default styling okay for user, usually aligned right or distinct */
    }
    
    /* Speak Button - Minimal Style */
    div[data-testid="column"] > div.stButton > button {
        border: none;
        padding: 0.2rem;
        color: #888;
    }
    div[data-testid="column"] > div.stButton > button:hover {
        color: #4CAF50;
        background: transparent;
        box-shadow: none;
        transform: scale(1.1);
    }
    
    /* Images */
    .stImage > img {
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Logo specific fix */
    [data-testid="stImage"] {
        display: flex;
        align-items: center;
        justify-content: center;
        padding-top: 1.5rem; /* Explicit top spacing */
        height: 100%;
    }
    
    [data-testid="stImage"] > img {
        object-fit: contain !important;
        max-height: 140px !important;
        width: auto !important;
        margin: 0 auto;
    }
    
    /* Input Area */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# API Helper
def api_get_menu():
    try:
        resp = requests.get(f"{config.BACKEND_URL}/v1/menu", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.Timeout:
        st.error("Menu service timed out. Please try again.")
    except Exception as e:
        st.error(f"Failed to connect to menu service: {e}")
    return []

def api_chat(messages):
    try:
        payload = {"messages": messages}
        resp = requests.post(f"{config.BACKEND_URL}/v1/chat", json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.Timeout:
        st.error("Chat service timed out. Please try again.")
    except Exception as e:
        print(f"Chat API Error: {e}")
        st.error(f"Chat service error: {e}")
    return None

def api_checkout(messages):
    try:
        payload = {"messages": messages}
        resp = requests.post(f"{config.BACKEND_URL}/v1/checkout", json=payload, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.Timeout:
        st.error("Checkout service timed out. Please try again.")
    except Exception as e:
        st.error(f"Checkout Error: {e}")
    return None

def api_tts(text):
    """Generate TTS audio for given text on-demand."""
    try:
        payload = {"text": text}
        resp = requests.post(f"{config.BACKEND_URL}/v1/tts", json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("audio_base64")
    except requests.exceptions.Timeout:
        st.error("TTS service timed out. Please try again.")
    except Exception as e:
        print(f"TTS API Error: {e}")
        st.error(f"TTS service error: {e}")
    return None

# State Initialization
if 'conversation' not in st.session_state:
    # Start with empty conversation - waiter will greet on first interaction
    st.session_state.conversation = []
    st.session_state.session_stage = "greeting"  # greeting -> ordering -> checkout -> complete
if 'menu_items' not in st.session_state:
    st.session_state.menu_items = api_get_menu()

# Get categories
categories = {}
for item in st.session_state.menu_items:
    cat = item.get('category', 'Other')
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(item)

# Main Layout - Full width for conversation
# Main Layout - Centered Header
col_header, col_logo = st.columns([4, 1.5])
with col_header:
    st.title("Garlic & Chives")
    st.markdown("*A Taste of Vietnam • Digital Experience*")
with col_logo:
    if os.path.exists("data/gac_logo.png"):
        st.image("data/gac_logo.png", width=140)

# Category Quick Selection
st.subheader("Browse by Category")
cat_cols = st.columns(len(categories))
for idx, (cat_name, items) in enumerate(categories.items()):
    with cat_cols[idx]:
        if st.button(f"{cat_name} ({len(items)})", key=f"cat_{idx}", use_container_width=True):
            # Auto-send message to waiter
            st.session_state.pending_message = f"What do you have in {cat_name}?"

st.divider()

# Conversation Area
st.subheader("💬 Conversation")

# Chat History
chat_container = st.container(height=500, border=True)
with chat_container:
    # Auto-greet if first visit
    if len(st.session_state.conversation) == 0:
        with st.spinner("Your waiter is approaching..."):
            greeting_response = api_chat([{"role": "system", "content": "Greet the customer as this is their first interaction."}])
            if greeting_response:
                text = greeting_response.get("text", "")
                st.session_state.conversation.append({"role": "assistant", "content": text})
                st.session_state.session_stage = "ordering"
                st.rerun()
    
    for idx, msg in enumerate(st.session_state.conversation):
        with st.chat_message(msg["role"]):
            # Create columns for message content and speak button
            if msg["role"] == "assistant":
                col_msg, col_btn = st.columns([6, 1])
                with col_msg:
                    st.write(msg["content"])
                with col_btn:
                    # Add speak button for assistant messages
                    if st.button("🔊", key=f"speak_{idx}", help="Speak this message"):
                        # Check if audio is already cached for this message
                        if f"audio_{idx}" not in st.session_state:
                            with st.spinner("Generating audio..."):
                                audio_b64 = api_tts(msg["content"])
                                if audio_b64:
                                    st.session_state[f"audio_{idx}"] = audio_b64
                        
                        # Play audio if available
                        if f"audio_{idx}" in st.session_state:
                            audio_bytes = base64.b64decode(st.session_state[f"audio_{idx}"])
                            st.audio(audio_bytes, format="audio/wav", autoplay=True)
            else:
                st.write(msg["content"])
            
            if "images" in msg and msg["images"]:
                # Display images inline in conversation
                for img_path in msg["images"]:
                    if img_path:
                        # Normalize path
                        if img_path.startswith('./images/'):
                            img_path = img_path.replace('./images/', 'data/images/')
                        if os.path.exists(img_path):
                            try:
                                st.image(img_path, width=300)
                            except:
                                pass

# Input Area
user_input = st.chat_input("Ask about the menu, order items, or request your check...")

# Checkout Button
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🧾 Request Check", use_container_width=True):
        with st.spinner("Preparing your bill..."):
            summary = api_checkout(st.session_state.conversation)
            if summary:
                st.session_state.order_summary = summary

# Display Order Summary if exists
if 'order_summary' in st.session_state:
    st.divider()
    st.subheader("Order Summary")
    order = st.session_state.order_summary.get("order", [])
    total = st.session_state.order_summary.get("total", 0)
    
    if not order:
        st.write("No items identified.")
    else:
        for item in order:
            st.write(f"- {item.get('qty')}x {item.get('name')} (${item.get('price')})")
        
        allergies = st.session_state.order_summary.get("allergies", [])
        if allergies:
            st.warning(f"⚠️ **Allergies Recorded:** {', '.join(allergies)}")
        else:
            st.info("No allergies recorded.")

        st.write(f"**Total: ${total}**")
        st.success("Ready for POS")

# Process Input
final_input = None
if user_input:
    final_input = user_input
elif 'pending_message' in st.session_state:
    final_input = st.session_state.pending_message
    del st.session_state.pending_message

if final_input:
    # 1. Add User Msg
    st.session_state.conversation.append({"role": "user", "content": final_input})
    
    # 2. Call API
    with st.spinner("Writing order..."):
        response = api_chat(st.session_state.conversation)
    
    if response:
        # 3. Process Response
        text = response.get("text", "")
        mentioned_items = response.get("mentioned_items", [])
        
        # 4. Find images
        image_paths = [i.get('image_path') for i in mentioned_items if i.get('image_path')]

        st.session_state.conversation.append({
            "role": "assistant", 
            "content": text,
            "images": image_paths
        })
        
        st.rerun()
