"use client";
import { useStore } from "@/lib/store";
import { X } from "lucide-react";
import CartTab from "../cart/CartTab";

export default function CartModal() {
    const { isCartOpen, toggleCart } = useStore();

    if (!isCartOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 transition-opacity backdrop-blur-sm"
                onClick={toggleCart}
                aria-hidden="true"
            />

            {/* Modal Content */}
            <div className="relative bg-white rounded-xl shadow-2xl w-full max-w-lg h-[80vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-200">
                <div className="p-4 border-b flex justify-between items-center bg-slate-50">
                    <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                        🍽️ Your Order
                    </h2>
                    <button
                        onClick={toggleCart}
                        className="p-2 hover:bg-slate-200 rounded-full transition-colors"
                        aria-label="Close Cart"
                    >
                        <X className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Cart Content reused from CartTab */}
                <CartTab />
            </div>
        </div>
    );
}
