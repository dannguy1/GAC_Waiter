import { create } from 'zustand';
import { MenuItem, CartItem, ChatMessage, CartUpdate } from './types';
import { getMenu, sendChat as apiSendChat } from './api';

interface AppState {
    // Menu Data
    menuItems: MenuItem[];
    categories: string[];
    activeCategory: string;
    suggestedItems: MenuItem[];
    isLoading: boolean;

    // Cart Data
    cart: CartItem[];

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

    addToCart: (item: MenuItem, quantity?: number, notes?: string) => void;
    removeFromCart: (index: number) => void;
    clearCart: () => void;

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

    addToCart: (item, quantity = 1, notes = "") => {
        set((state) => ({
            cart: [...state.cart, { item, quantity, notes }]
            // Removed: isCartOpen: true - cart now opens only on user request
        }));
    },

    removeFromCart: (index) => {
        set((state) => ({
            cart: state.cart.filter((_, i) => i !== index)
        }));
    },

    clearCart: () => set({ cart: [] }),

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

            // Corrected API call with single argument
            const response = await apiSendChat(historyPayload);

            const botMessage: ChatMessage = {
                role: "assistant",
                content: response.text || "Sorry, I didn't get that.",
                timestamp: Date.now(),
                showcase_items: response.mentioned_items || []
            };

            // Handle Cart Updates
            let currentCart = get().cart;
            let cartUpdated = false;



            if (response.cart_updates && response.cart_updates.length > 0) {
                response.cart_updates.forEach((update: CartUpdate) => {
                    // Backend returns 'name' and 'qty', not 'item_name' and 'quantity'
                    const searchName = (update.name || update.item_name || "").toLowerCase().trim();


                    // Fuzzy matching: check item_name, item_viet, and partial matches
                    const item = get().menuItems.find(i => {
                        const name = i.item_name.toLowerCase();
                        const viet = (i.item_viet || "").toLowerCase();
                        // Normalize Vietnamese characters for comparison
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
                            quantity: update.qty || update.quantity || 1,
                            notes: update.notes || ""
                        }];
                        cartUpdated = true;
                    } else {
                        console.warn("Cart update: Item not found:", update.name || update.item_name);
                    }
                });
            }

            set((state) => ({
                chatHistory: [...state.chatHistory, botMessage],
                isChatSending: false,
                cart: cartUpdated ? currentCart : state.cart,
                // Removed: isCartOpen: cartUpdated ? true : state.isCartOpen
                suggestedItems: response.mentioned_items || []
            }));

        } catch (error) {
            console.error("Chat error", error);
            // Add error message to chat for user feedback
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
