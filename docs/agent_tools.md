# Agent Tool Documentation

This document describes the tools available to the `WaitstaffAgent` in the GAC Waiter system. These tools allow the agent to interact with the backend (menu, order system) and control the frontend state (cart, language, checkout lock).

## Tool List

### 1. `lookup_menu`
*   **Purpose**: Search the vector database for menu items, prices, descriptions, and ingredients.
*   **Input**: `query` (string) - Key terms to search for (e.g., "pho", "spicy noodles", "dessert").
*   **Usage**:
    ```
    Action: lookup_menu
    Action Input: spicy beef soup
    ```
*   **Returns**: A list of matching menu items with details.

### 2. `lookup_info`
*   **Purpose**: Search the vector database for general restaurant information such as history, owner, location, policies, and business hours.
*   **Input**: `query` (string) - The question or topic.
*   **Usage**:
    ```
    Action: lookup_info
    Action Input: who is the owner
    ```
*   **Returns**: Relevant text snippets from the restaurant's knowledge base.

### 3. `set_language`
*   **Purpose**: Updates the session language preference. The agent will respond in this language for future turns.
*   **Input**: `language` (string) - The target language (e.g., "Vietnamese", "English").
*   **Usage**:
    ```
    Action: set_language
    Action Input: Vietnamese
    ```
*   **Returns**: Confirmation message.

### 4. `add_to_cart`
*   **Purpose**: Adds a specific item to the user's shopping cart.
*   **Input**: `input` (string) - Comma-separated string format: `"Item Name, Quantity, Notes"`.
    *   `Item Name`: Fuzzy-matched against the menu.
    *   `Quantity`: Integer (default 1).
    *   `Notes`: **Modifications ONLY** (e.g., "no onions", "extra sauce"). Do NOT put allergies here.
*   **Usage**:
    ```
    Action: add_to_cart
    Action Input: Pho Tai, 2, extra noodles
    ```
*   **Returns**: Success message with price details, or an error if the item is not found (with suggestions).

### 5. `set_general_note`
*   **Purpose**: Sets a global note for the entire order. **REQUIRED** for all Allergies and Dietary Restrictions.
*   **Input**: `note` (string) - The text to display in the "Special Instructions" box on the frontend.
*   **Usage**:
    ```
    Action: set_general_note
    Action Input: Customer has a severe shrimp allergy
    ```
*   **Returns**: Confirmation that the note has been set.
*   **Frontend Effect**: Updates the `generalNotes` state in the store, visible in the Cart tab.

### 6. `confirm_order`
*   **Purpose**: Unlocks the "Submit Order" button on the frontend, allowing the user to proceed to checkout.
*   **Rule**: MUST be called ONLY after the agent has performed an explicitly **Order Readback** and confirmed **Allergies** with the user.
*   **Input**: `confirmed` (string) - Usually just the word "confirmed" or similar.
*   **Usage**:
    ```
    Action: confirm_order
    Action Input: confirmed
    ```
*   **Returns**: Confirmation message "Order confirmed. Checkout button unlocked."
*   **Frontend Effect**: Sets `isOrderVerified` to `true` in the store, enabling the checkout button.
