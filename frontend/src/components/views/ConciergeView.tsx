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
        <div className="flex flex-col h-full bg-slate-50">
            {/* Chat Area - Takes flexible remaining height, minimum height for mobile */}
            <div className="flex-1 min-h-[40vh] sm:min-h-[30vh] overflow-hidden border-b border-slate-200 bg-white relative">
                <ChatTab />
            </div>

            {/* Menu Showcase - Responsive height: smaller on mobile, larger on desktop */}
            <div className="h-[35vh] sm:h-[40vh] md:h-[45vh] lg:h-[50vh] min-h-[200px] max-h-[500px] overflow-y-auto bg-slate-50 shadow-inner transition-colors">
                <MenuGrid
                    compact
                    title={showSuggestions ? "Concierge Suggestions" : activeCategory}
                    items={showSuggestions ? suggestedItems : undefined}
                />
            </div>
        </div>
    );
}
