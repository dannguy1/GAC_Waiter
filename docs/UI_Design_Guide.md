# User Interface Design Guide

## Overview
The "Garlic & Chives" Digital Waiter application features a premium, custom-styled interface built on Streamlit. The design philosophy focuses on elegance, readability, and a "Fine Dining" aesthetic using a Gold/Green on Dark theme.

## Design System

### Color Palette
- **Primary Accent**: `#4CAF50` (Fresh Green)
  - Used for: Headers, Buttons, Borders, Input Focus, Highlighted Interactions.
  - Significance: Represents the fresh ingredients (chives, herbs) of Vietnamese cuisine.
- **Text Primary**: `#FFFFFF` (White) / Light Grey
- **Background**: Dark Mode (Streamlit Default + Custom Overrides)
- **Secondary/Inactive**: `#888888` (Grey)

### Typography
- **Headings**: `Playfair Display` (Serif)
  - Usage: `h1` (Title), `h2`, `h3`
  - Characteristics: Elegant, editorial, traditional.
- **Body Text**: `Inter` (Sans-Serif)
  - Usage: Chat messages, buttons, descriptions.
  - Characteristics: Clean, modern, highly readable.

### Components

#### 1. Header & Logo
- **Layout**: Offset Column Layout `[4, 1.5]` to balance title and logo.
- **Logo Style**: 
  - Flexbox centering
  - `object-fit: contain` to prevent clipping
  - `max-height: 140px` for visibility
  - `padding-top: 1.5rem` for vertical alignment

#### 2. Buttons
- **Style**: Pill-shaped (`border-radius: 25px`) with transparent background and Green border.
- **Hover State**: Green fill, White text, slight lift (`transform: translateY(-2px)`), and Green shadow (`box-shadow`).

#### 3. Chat Interface
- **Message Bubbles**: 
  - Custom background `rgba(255, 255, 255, 0.03)`
  - Rounded corners `15px`
  - Subtle border `rgba(255, 255, 255, 0.05)`
- **Speak Button**:
  - Minimalist icon-only style
  - Subtle scale animation on hover (`scale(1.1)`)
  - No border to reduce visual clutter

#### 4. Images
- **Style**: Rounded corners (`12px`) and soft drop shadow.
- **Behavior**: Responsive width to container.

## CSS Implementation
Custom styles are injected via `st.markdown` with `unsafe_allow_html=True` in `app.py`.
Key CSS classes overridden:
- `.stButton`
- `.stTextInput`
- `.stChatMessage`
- `.stImage`
- `block-container`

## Best Practices
- **Consistency**: Always use the defined Green (`#4CAF50`) for any new interactive elements.
- **Spacing**: Maintain comfortable padding (e.g., `1rem` - `2rem`) to avoid a cramped interface.
- **Feedback**: Ensure all interactive elements have a visible hover state.
