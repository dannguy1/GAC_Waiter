# UI Design Guide: Garlic & Chives Digital Waiter

**Goal:** Transform the interface into a professional, immersive digital dining experience using a tabbed layout to maximize screen real estate.

---

## 🏗️ Layout Structure

The application will use a **Sidebar + Tabbed Interface** layout.

```
┌──────────────┐ ┌──────────────────────────────────────────────────────────┐
│  SIDEBAR     │ │ [ Tab 1: CONCIERGE & MENU ]    [ Tab 2: YOUR ORDER ]     │
│  (Auto-      │ │                                                          │
│   hides)     │ │  ┌────────────────────────────────────────────────────┐  │
│              │ │  │                                                    │  │
│  [Logo]      │ │  │              CHAT INTERFACE                        │  │
│              │ │  │                                                    │  │
│  Navigation  │ │  │  User: Show me spicy seafood dishes?               │  │
│  - Menu      │ │  │  AI:   The Tamarind Crab is a great choice!        │  │
│  - Drinks    │ │  │                                                    │  │
│  - Specials  │ │  └────────────────────────────────────────────────────┘  │
│              │ │                                                          │
│  [Call       │ │  ┌────────────────────────────────────────────────────┐  │
│   Server]    │ │  │             MENU SHOWCASE (Full Width)             │  │
│              │ │  │                                                    │  │
│              │ │  │  [  BIG CARD  ]   [  BIG CARD  ]   [  BIG CARD  ]  │  │
│              │ │  │                                                    │  │
│              │ │  └────────────────────────────────────────────────────┘  │
│              │ └──────────────────────────────────────────────────────────┘
└──────────────┘
```

---

## 🎨 Visual Identity

**Theme:** "Fresh & Modern Vietnamese"
- **Primary Color:** `#2E7D32` (Fresh Basil Green)
- **Secondary Color:** `#FF6F00` (Crispy Gold/Orange)
- **Background:** `#F8F9FA` (Clean Off-White)
- **Typography:** *Playfair Display* (Headers) + *Inter* (Body)

---

## 🧩 Key Components

### 1. The Navigation Sidebar (Left)
- **Concept:** Auto-hiding or collapsible sidebar.
- **Function:** Quick filter buttons (e.g., "Seafood", "Meat", "Favorites").
- **Action:** Clicking a category keeps you on the "Concierge" tab but filters the *Menu Showcase* area below the chat.

### 2. Tab 1: Concierge & Menu (The Main Stage)
This is the default view, designed for discovery.
- **Top Half: Chat Interface**
    - Clean, modern chat bubbles.
    - Minimalist input bar.
- **Bottom Half: Dynamic Menu Showcase**
    - Takes advantage of full width.
    - Displays high-quality image cards in a responsive grid.
    - **Context Aware:** If you ask about "Beef", this section auto-updates to show Beef dishes.

### 3. Tab 2: Your Order (The Cart)
A dedicated, distraction-free view for reviewing the meal.
- **Large Order Summary:** Clear list of items, quantities, and prices.
- **Special Instructions:** Input fields for notes (e.g., "No onions").
- **Dietary Alerts:** clearly highlights allergy warnings.
- **Big Checkout Button:** High-visibility call to action.

---

## 📱 Responsiveness

- **Desktop:** Sidebar visible (or toggleable), Tabs at top.
- **Mobile:**
    - Sidebar becomes a hamburger menu.
    - Tabs become a sticky bottom bar (like a native app): `[Chat/Menu] [My Order]`.

---

## 🛠️ Implementation Strategy

1.  **Refactor `app.py`**:
    - Use `st.sidebar` for navigation.
    - Use `st.tabs(["💬 Concierge", "🛒 My Order"])` for main content.
2.  **Componentizing**:
    - `render_chat_tab()`: Encapsulates chat history + showcase grid.
    - `render_order_tab()`: Encapsulates order list + checkout logic.
3.  **State Management**:
    - `st.session_state.active_tab`: To potentially switch tabs programmatically (e.g., after adding item).
4.  **CSS Overhaul**: new styles for larger, immersive cards.

