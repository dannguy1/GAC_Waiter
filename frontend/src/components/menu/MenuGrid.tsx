"use client";
import { useStore } from "@/lib/store";
import { useEffect } from "react";
import MenuCard from "./MenuCard";
import { Loader2 } from "lucide-react";
import { MenuItem } from "@/lib/types";

interface MenuGridProps {
    title?: string;
    compact?: boolean;
    items?: MenuItem[];
}

export default function MenuGrid({ title, compact, items }: MenuGridProps) {
    const { menuItems, activeCategory, fetchMenu, isLoading } = useStore();

    useEffect(() => {
        fetchMenu();
    }, [fetchMenu]);

    const displayItems = items
        ? items
        : (activeCategory === "All" || !activeCategory
            ? menuItems
            : menuItems.filter(item => item.category === activeCategory));

    if (isLoading && menuItems.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center p-8">
                <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
                <p className="text-muted-foreground">Loading menu...</p>
            </div>
        );
    }

    return (
        <div className="p-4 w-full">
            <div className={`mb-4 flex justify-between items-end ${compact ? 'mb-2' : ''}`}>
                <h2 className="text-xl md:text-2xl font-bold text-slate-800">
                    {title || (activeCategory === "All" ? "Suggested Items" : activeCategory)}
                </h2>
                <span className="text-muted-foreground text-sm font-medium">
                    {displayItems.length} items
                </span>
            </div>

            {/* Auto-fill grid with min-width card size */}
            <div className="grid gap-6 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
                {displayItems.map((item, idx) => (
                    <MenuCard key={`${item.item_name}-${idx}`} item={item} />
                ))}
            </div>

            {displayItems.length === 0 && !isLoading && (
                <div className="text-center py-12 text-muted-foreground">
                    {items ? "Ask me for recommendations to see items here!" : "No items found in this category."}
                </div>
            )}
        </div>
    );
}
