export interface MenuItem {
    item_name: string;
    item_viet?: string;
    description: string;
    price: number;
    category: string;
    image_path?: string;
    ingredients?: string[];
    spicy_level?: number;
    popular?: boolean;
}

export interface MenuResponse {
    items: MenuItem[];
    categories: string[];
}

export interface CartItem {
    item: MenuItem;
    quantity: number;
    notes?: string;
}

export interface ChatMessage {
    role: "user" | "assistant" | "system";
    content: string;
    timestamp?: number;
    showcase_items?: MenuItem[];
}

export interface CartUpdate {
    name: string;
    qty: number;
    notes: string;
    // Optional fallbacks for compatibility
    item_name?: string;
    quantity?: number;
}

export interface CheckoutPayload {
    cart: {
        item_name: string;
        quantity: number;
        notes: string;
        price: number;
    }[];
    general_notes: string;
}
