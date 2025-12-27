import axios from 'axios';
import { MenuItem, MenuResponse, CartUpdate } from './types';

const API_BASE_URL = '';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getMenu = async (): Promise<MenuResponse> => {
    try {
        const response = await api.get('/v1/menu');
        // Backend returns a list directly, not {items: [...]}
        const items = Array.isArray(response.data) ? response.data : (response.data.items || []);



        // Extract unique categories
        const categories = Array.from(new Set(items.map((i: MenuItem) => i.category))).filter(Boolean) as string[];

        const sortedCategories = categories.sort((a, b) => {
            if (a.includes("Appetizer")) return -1;
            if (b.includes("Appetizer")) return 1;
            return a.localeCompare(b);
        });

        return { items, categories: sortedCategories };
    } catch (error) {
        console.error("Failed to fetch menu:", error);
        return { items: [], categories: [] };
    }
};

export const getImageUrl = (path?: string) => {
    if (!path) return "https://placehold.co/400x300?text=No+Image";

    let cleanPath = path;

    // Remove leading ./ if present
    if (cleanPath.startsWith("./")) {
        cleanPath = cleanPath.substring(2);
    }

    // Handle various path formats
    if (cleanPath.startsWith("data/images/")) {
        cleanPath = cleanPath.replace("data/images/", "images/");
    } else if (cleanPath.startsWith("data/downloaded_images/")) {
        cleanPath = cleanPath.replace("data/downloaded_images/", "downloaded_images/");
    }

    // Ensure path starts with /
    if (!cleanPath.startsWith("/")) {
        cleanPath = "/" + cleanPath;
    }

    // Return relative path, Next.js will handle proxying via rewrites
    return cleanPath;
};

export interface ChatResponse {
    text: string;
    language: string;
    mentioned_items: MenuItem[];
    cart_updates?: CartUpdate[];
}

interface ChatMessagePayload {
    role: string;
    content: string;
}

export const sendChat = async (messages: ChatMessagePayload[]): Promise<ChatResponse> => {
    try {
        const response = await api.post('/v1/chat', {
            messages: messages
        });
        return response.data;
    } catch (error) {
        console.error("Chat API error:", error);
        return {
            text: "",
            language: "English",
            mentioned_items: []
        };
    }
};

export interface TTSResponse {
    audio_base64: string | null;
}

export const requestTTS = async (text: string): Promise<TTSResponse> => {
    try {
        const response = await api.post('/v1/tts', { text });
        return response.data;
    } catch (error) {
        console.error("TTS API error:", error);
        return { audio_base64: null };
    }
};
