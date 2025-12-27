"use client";

import { useStore } from "@/lib/store";
import { cn } from "@/lib/utils";
import { UtensilsCrossed, RefreshCw, X } from "lucide-react";

export default function Sidebar() {
    const { categories, activeCategory, setCategory, isSidebarOpen, toggleSidebar } = useStore();

    return (
        <>
            {/* Backdrop for Mobile/Drawer Mode */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 transition-opacity"
                    onClick={toggleSidebar}
                    aria-hidden="true"
                />
            )}

            <aside className={cn(
                "fixed left-0 top-0 h-screen w-72 flex flex-col bg-white border-r z-50 shadow-2xl transition-transform duration-300 ease-in-out",
                isSidebarOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                {/* Header */}
                <div className="p-6 border-b bg-white flex justify-between items-center">
                    <div>
                        <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
                            <UtensilsCrossed className="w-6 h-6" />
                            Menu
                        </h1>
                        <p className="text-xs text-muted-foreground mt-1">Select a category</p>
                    </div>
                    <button onClick={toggleSidebar} className="p-2 -mr-2 text-slate-400 hover:text-slate-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto p-4 space-y-1">
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => {
                                setCategory(cat);
                                if (window.innerWidth < 1024) toggleSidebar(); // Close on selection on mobile/tablet
                            }}
                            className={cn(
                                "w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors",
                                activeCategory === cat
                                    ? "bg-primary text-primary-foreground shadow-md"
                                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                            )}
                        >
                            {cat}
                        </button>
                    ))}
                </nav>

                {/* Footer Actions */}
                <div className="p-4 border-t bg-white space-y-2">
                    <button className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-slate-200 rounded-md text-sm font-medium hover:bg-slate-100 text-slate-700">
                        <RefreshCw className="w-4 h-4" />
                        Reset
                    </button>
                </div>
            </aside>
        </>
    );
}
