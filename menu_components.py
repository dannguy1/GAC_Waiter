import streamlit as st
import os

def render_menu_item(item, item_index=0):
    """
    Renders a single menu item card.
    item: dict containing 'item_name', 'price', 'description', 'image_path'
    item_index: unique index to prevent key collisions
    """
    with st.container(border=True):
        # Image Handling
        img_path = item.get('image_path', '')
        if img_path:
            # Normalize path - convert ./images to data/images
            if img_path.startswith('./images/'):
                img_path = img_path.replace('./images/', 'data/images/')
            
            if os.path.exists(img_path):
                try:
                    st.image(img_path, use_container_width=True)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
                    st.image("https://placehold.co/300x200?text=Image+Error", use_container_width=True)
            else:
                # Placeholder if file not found
                st.image("https://placehold.co/300x200?text=No+Image", use_container_width=True)
        else:
            # Placeholder for items without images
            st.image("https://placehold.co/300x200?text=No+Image", use_container_width=True)
            
        st.subheader(item.get('item_name', 'Unknown Item'))
        st.write(f"**Price:** ${item.get('price', '--')}")
        
        # Truncate description for grid view
        desc = item.get('description', '')
        if len(desc) > 80:
            desc = desc[:77] + "..."
        st.caption(desc)
        
        # Interaction Buttons with unique keys
        col1, col2 = st.columns(2)
        with col1:
            if st.button("❓ Ask", key=f"ask_{item_index}"):
                return f"Tell me more about the {item.get('item_name')}"
        with col2:
            if st.button("🛒 Order", key=f"ord_{item_index}"):
                return f"I would like to order the {item.get('item_name')}, please."
    
    return None

def render_menu_grid(items, cols=3):
    """
    Renders a grid of menu items.
    Returns: The text action triggered by a button click, if any.
    """
    action_text = None
    
    # Process in chunks of 'cols'
    for i in range(0, len(items), cols):
        columns = st.columns(cols)
        batch = items[i:i+cols]
        
        for col_idx, (col, item) in enumerate(zip(columns, batch)):
            with col:
                # Pass unique index to avoid key collisions
                action = render_menu_item(item, item_index=i+col_idx)
                if action:
                    action_text = action
                    
    return action_text
