import { create } from 'zustand';
import { MenuItem, CartItem, ChatMessage, CartUpdate, CheckoutPayload } from './types';
import { getMenu, sendChat as apiSendChat, checkout } from './api';

interface AppState {
    // Menu Data
    menuItems: MenuItem[];
    categories: string[];
    activeCategory: string;
    suggestedItems: MenuItem[];
    isLoading: boolean;

    // Cart Data
    cart: CartItem[];
    generalNotes: string;
    isOrderVerified: boolean;

    // Chat Data
    chatHistory: ChatMessage[];
    isChatSending: boolean;

    // UI State
    isSidebarOpen: boolean;
    isCartOpen: boolean;
    selectedItem: MenuItem | null;

    // Actions
    fetchMenu: () => Promise<void>;
    setCategory: (category: string) => void;
    setGeneralNotes: (notes: string) => void;

    addToCart: (item: MenuItem, quantity?: number, notes?: string) => void;
    removeFromCart: (index: number) => void;
    clearCart: () => void;
    submitOrder: () => Promise<any>;

    sendMessage: (content: string) => Promise<void>;
    addSystemMessage: (content: string) => void;

    toggleSidebar: () => void;
    toggleCart: () => void;
    setSelectedItem: (item: MenuItem | null) => void;
}

export const useStore = create<AppState>((set, get) => ({
    // Initial State
    menuItems: [],
    categories: [],
    activeCategory: "All",
    suggestedItems: [],
    isLoading: false,
    cart: [],
    generalNotes: "", // Global order notes (allergies, etc.)
    isOrderVerified: false,
    chatHistory: [{ role: "assistant", content: "Hello! I'm your digital concierge. Ask me for recommendations or help with your order.", timestamp: Date.now() }],
    isChatSending: false,
    isSidebarOpen: false,
    isCartOpen: false,
    selectedItem: null,

    // Actions
    fetchMenu: async () => {
        set({ isLoading: true });
        const { items, categories } = await getMenu();
        const cats = ["All", ...categories];
        set({ menuItems: items, categories: cats, isLoading: false });
    },

    setCategory: (category) => set({ activeCategory: category }),

    setGeneralNotes: (notes) => set({ generalNotes: notes }),

    addToCart: (item, quantity = 1, notes = "") => {
        set((state) => ({
            cart: [...state.cart, { item, quantity, notes }],
            isOrderVerified: false // Reset verification on cart change
            // Removed: isCartOpen: true - cart now opens only on user request
        }));
    },

    removeFromCart: (index: number) => {
        set((state) => ({
            cart: state.cart.filter((_, i) => i !== index),
            isOrderVerified: false // Reset verification on cart change
        }));
    },

    clearCart: () => set({ cart: [], generalNotes: "" }),

    submitOrder: async () => {
        const { cart, generalNotes } = get();
        if (cart.length === 0) return;

        try {
            const payload: CheckoutPayload = {
                cart: cart.map(c => ({
                    item_name: c.item.item_name,
                    quantity: c.quantity,
                    notes: c.notes || "",
                    price: c.item.price
                })),
                general_notes: generalNotes || ""
            };

            const response = await checkout(payload);
            set({ cart: [], generalNotes: "" });
            return response;
        } catch (error) {
            console.error("Submit Order Error:", error);
            throw error;
        }
    },

    sendMessage: async (content) => {
        const { chatHistory } = get();
        const newMessage: ChatMessage = { role: "user", content, timestamp: Date.now() };

        set({
            chatHistory: [...chatHistory, newMessage],
            isChatSending: true
        });

        try {
            // Adapt history for Backend
            const historyPayload = chatHistory
                .filter(m => m.role !== "system")
                .map(m => ({ role: m.role, content: m.content }));

            historyPayload.push({ role: "user", content });

            const response = await apiSendChat(historyPayload);

            const botMessage: ChatMessage = {
                role: "assistant",
                content: response.text || "Sorry, I didn't get that.",
                timestamp: Date.now(),
                showcase_items: response.mentioned_items || []
            };

            // Update Global Notes if agent set them
            if (response.general_note) {
                set({ generalNotes: response.general_note });
            }

            // Handle Order Verification logic
            const isVerified = response.order_confirmed === true;

            // Handle Cart Updates
            let currentCart = get().cart;
            let cartUpdated = false;

            if (response.cart_updates && response.cart_updates.length > 0) {
                response.cart_updates.forEach((update: CartUpdate) => {
                    const searchName = (update.name || update.item_name || "").toLowerCase().trim();

                    // Fuzzy matching
                    const item = get().menuItems.find(i => {
                        const name = i.item_name.toLowerCase();
                        const viet = (i.item_viet || "").toLowerCase();
                        const normalizedViet = viet.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
                        const normalizedSearch = searchName.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

                        return name === searchName ||
                            viet === searchName ||
                            normalizedViet === normalizedSearch ||
                            name.includes(searchName) ||
                            searchName.includes(name) ||
                            viet.includes(searchName) ||
                            normalizedViet.includes(normalizedSearch);
                    });

                    if (item) {
                        currentCart = [...currentCart, {
                            item,
                            quantity: update.qty || 1,
                            notes: update.notes || ""
                        }];
                        cartUpdated = true;
                    } else {
                        console.warn("Cart update: Item not found:", update.name);
                    }
                });
            }

            set((state) => ({
                chatHistory: [...state.chatHistory, botMessage],
                isChatSending: false,
                cart: cartUpdated ? currentCart : state.cart,
                isOrderVerified: isVerified ? true : (cartUpdated ? false : state.isOrderVerified),
                suggestedItems: response.mentioned_items || []
            }));

        } catch (error) {
            console.error("Chat error", error);
            const errorMessage: ChatMessage = {
                role: "system",
                content: "Sorry, something went wrong. Please try again.",
                timestamp: Date.now()
            };
            set((state) => ({
                chatHistory: [...state.chatHistory, errorMessage],
                isChatSending: false
            }));
        }
    },

    addSystemMessage: (content) => set((state) => ({
        chatHistory: [...state.chatHistory, { role: "system", content, timestamp: Date.now() }]
    })),

    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    toggleCart: () => set((state) => ({ isCartOpen: !state.isCartOpen })),
    setSelectedItem: (item) => set({ selectedItem: item }),
}));
