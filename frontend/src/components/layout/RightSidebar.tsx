"use client";

import { useStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import { MessageSquare, ShoppingBag, ChevronLeft, ChevronRight } from "lucide-react";
import ChatTab from "@/components/chat/ChatTab";
import CartTab from "@/components/cart/CartTab";

export default function RightSidebar() {
    const { isRightPanelOpen, rightPanelTab, setRightPanelTab, toggleRightPanel, cart } = useStore();

    if (!isRightPanelOpen) {
        return (
            <div className="fixed right-0 top-0 h-screen w-12 bg-white border-l z-20 flex flex-col items-center pt-24 space-y-4 shadow-sm">
                <button onClick={toggleRightPanel} className="p-2 text-slate-500 hover:text-primary transition-colors tooltip" title="Open Panel">
                    <ChevronLeft className="w-6 h-6" />
                </button>
                <button onClick={() => setRightPanelTab("chat")} className="p-2 relative text-slate-500 hover:text-primary transition-colors" title="Chat">
                    <MessageSquare className="w-6 h-6" />
                </button>
                <button onClick={() => setRightPanelTab("cart")} className="p-2 relative text-slate-500 hover:text-primary transition-colors" title="Cart">
                    <ShoppingBag className="w-6 h-6" />
                    {cart.length > 0 && (
                        <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border border-white"></span>
                    )}
                </button>
            </div>
        );
    }

    return (
        <aside className="fixed right-0 top-0 h-screen w-80 sm:w-96 bg-white border-l z-20 flex flex-col shadow-xl animate-in slide-in-from-right duration-300">
            {/* Header Tabs */}
            <div className="flex border-b bg-white">
                <button
                    onClick={() => setRightPanelTab("chat")}
                    className={cn("flex-1 py-4 flex items-center justify-center gap-2 text-sm font-medium transition-colors border-b-2",
                        rightPanelTab === "chat" ? "border-primary text-primary bg-green-50/50" : "border-transparent text-slate-500 hover:bg-slate-50")}
                >
                    <MessageSquare className="w-4 h-4" />
                    Concierge
                </button>
                <button
                    onClick={() => setRightPanelTab("cart")}
                    className={cn("flex-1 py-4 flex items-center justify-center gap-2 text-sm font-medium transition-colors border-b-2",
                        rightPanelTab === "cart" ? "border-primary text-primary bg-green-50/50" : "border-transparent text-slate-500 hover:bg-slate-50")}
                >
                    <ShoppingBag className="w-4 h-4" />
                    My Order {cart.length > 0 && <span className="bg-primary text-white text-[10px] px-1.5 py-0.5 rounded-full">{cart.length}</span>}
                </button>
                <button onClick={toggleRightPanel} className="px-3 text-slate-400 hover:text-slate-600 border-l hover:bg-slate-50">
                    <ChevronRight className="w-5 h-5" />
                </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden flex flex-col bg-slate-50/50">
                {rightPanelTab === "chat" ? <ChatTab /> : <CartTab />}
            </div>
        </aside>
    );
}
