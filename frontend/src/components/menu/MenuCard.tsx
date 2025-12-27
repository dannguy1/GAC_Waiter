"use client";
import { MenuItem } from "@/lib/types";
import { getImageUrl } from "@/lib/api";
import { useStore } from "@/lib/store";
import { Plus } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

interface MenuCardProps {
    item: MenuItem;
}

export default function MenuCard({ item }: MenuCardProps) {
    const [imgSrc, setImgSrc] = useState(getImageUrl(item.image_path));
    const { addToCart, setSelectedItem } = useStore();

    return (
        <div className="group bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-all flex flex-col h-full">
            <div
                className="relative h-48 w-full bg-slate-100 overflow-hidden cursor-pointer"
                onClick={() => setSelectedItem(item)}
            >
                <Image
                    src={imgSrc}
                    alt={item.item_name}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    style={{ objectFit: "cover" }}
                    onError={() => setImgSrc("https://placehold.co/400x300?text=No+Image")}
                />
            </div>

            <div className="p-4 flex flex-col flex-1">
                <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-lg text-slate-900 leading-tight">
                        {item.item_name}
                    </h3>
                    <span className="font-bold text-primary text-lg">
                        ${item.price.toFixed(2)}
                    </span>
                </div>

                {item.item_viet && (
                    <p className="text-xs text-muted-foreground italic mb-2">{item.item_viet}</p>
                )}

                <p className="text-sm text-slate-500 line-clamp-2 mb-4 flex-1">
                    {item.description}
                </p>

                <button
                    onClick={() => addToCart(item)}
                    className="w-full mt-auto bg-primary text-white py-2 rounded-lg font-medium flex items-center justify-center gap-2 hover:bg-primary/90 active:scale-95 transition-all"
                >
                    <Plus className="w-4 h-4" />
                    Add to Order
                </button>
            </div>
        </div>
    );
}
