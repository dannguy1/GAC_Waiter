"use client";
import { useStore } from "@/lib/store";
import { X, Plus, Image as ImageIcon } from "lucide-react";
import Image from "next/image";
import { getImageUrl } from "@/lib/api";
import { useState } from "react";

export default function ItemDetailModal() {
    const { selectedItem, setSelectedItem, addToCart } = useStore();
    const [imgSrc, setImgSrc] = useState<string>("");

    if (!selectedItem) return null;

    // Reset image source when item changes if needed, but key={} in render helps
    const currentImgSrc = imgSrc || getImageUrl(selectedItem.image_path);

    const handleClose = () => {
        setSelectedItem(null);
        setImgSrc(""); // Reset fallback
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
            onClick={handleClose}
        >
            <div
                className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Image Section */}
                <div className="relative w-full aspect-video bg-slate-100 shrink-0">
                    <Image
                        src={currentImgSrc}
                        alt={selectedItem.item_name}
                        fill
                        className="object-cover"
                        sizes="(max-width: 768px) 100vw, 800px"
                        priority
                        onError={() => setImgSrc("https://placehold.co/800x600?text=No+Image")}
                    />
                    <button
                        onClick={handleClose}
                        className="absolute top-4 right-4 p-2 bg-black/50 hover:bg-black/70 text-white rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                    {selectedItem.popular && (
                        <div className="absolute top-4 left-4 bg-amber-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                            POPULAR
                        </div>
                    )}
                </div>

                {/* Content Section */}
                <div className="p-6 overflow-y-auto flex-1">
                    <div className="flex justify-between items-start gap-4 mb-2">
                        <div>
                            <h2 className="text-2xl font-bold text-slate-900">{selectedItem.item_name}</h2>
                            {selectedItem.item_viet && (
                                <p className="text-lg text-primary font-medium italic">{selectedItem.item_viet}</p>
                            )}
                        </div>
                        <span className="text-2xl font-bold text-slate-900 shrink-0">
                            ${selectedItem.price.toFixed(2)}
                        </span>
                    </div>

                    <p className="text-slate-600 text-base leading-relaxed mb-6">
                        {selectedItem.description}
                    </p>

                    {/* Additional details if available could go here */}

                    <button
                        onClick={() => {
                            addToCart(selectedItem);
                            handleClose();
                        }}
                        className="w-full bg-primary text-white py-3.5 rounded-xl font-bold text-lg hover:bg-primary/90 active:scale-95 transition-all shadow-lg flex items-center justify-center gap-2"
                    >
                        <Plus className="w-6 h-6" />
                        Add to Order
                    </button>
                </div>
            </div>
        </div>
    );
}
