"use client";
import ChatTab from "../chat/ChatTab";
import MenuGrid from "../menu/MenuGrid";
import { useStore } from "@/lib/store";

export default function ConciergeView() {
    const { activeCategory, suggestedItems } = useStore();

    // Logic: If Category is "All" (default), show Suggested Items from Chat.
    // If specific Category selected, show that category.
    const showSuggestions = activeCategory === "All";

    return (
        <div className="flex flex-col md:flex-row h-full bg-slate-50 overflow-hidden">
            {/* Chat Area - Left Side (or Top on mobile) - Takes 2/3 height on mobile */}
            <div className="flex-[2] md:flex-1 md:w-1/2 h-full border-b md:border-b-0 md:border-r border-slate-200 bg-white relative">
                <ChatTab />
            </div>

            {/* Menu Showcase - Right Side (or Bottom on mobile) - Takes 1/3 height on mobile */}
            <div className="flex-1 md:h-full md:w-1/2 overflow-y-auto bg-slate-50 shadow-inner transition-colors">
                <MenuGrid
                    compact
                    title={showSuggestions ? "Concierge Suggestions" : activeCategory}
                    items={showSuggestions ? suggestedItems : undefined}
                />
            </div>
        </div>
    );
}
