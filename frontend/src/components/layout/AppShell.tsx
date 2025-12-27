"use client";
import Sidebar from "./Sidebar";
import ConciergeView from "../views/ConciergeView";
import CartModal from "../cart/CartModal";
import ItemDetailModal from "../menu/ItemDetailModal";
import { useStore } from "@/lib/store";
import { Menu, ShoppingCart } from "lucide-react";
import Image from "next/image";

export default function AppShell() {
    const { toggleSidebar, toggleCart, cart } = useStore();

    return (
        <div className="flex min-h-screen bg-slate-50 overflow-hidden relative">
            <Sidebar />

            {/* Main Content Area - Full Width */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden w-full transition-all">

                {/* Header - Responsive (smaller on mobile, larger on desktop) */}
                <div className="flex items-center justify-between border-b bg-white shrink-0 shadow-md z-30 px-3 sm:px-6 py-2 sm:py-4 h-16 sm:h-24 md:h-32">
                    <div className="flex items-center gap-3 sm:gap-6">
                        {/* Hamburger */}
                        <button
                            onClick={toggleSidebar}
                            className="p-2 sm:p-3 hover:bg-slate-100 rounded-xl text-slate-700 transition-colors"
                            aria-label="Toggle Menu"
                        >
                            <Menu className="w-6 h-6 sm:w-8 sm:h-8" />
                        </button>

                        {/* Branding */}
                        <div className="flex items-center gap-3 sm:gap-5">
                            <div className="relative w-10 h-10 sm:w-16 sm:h-16 md:w-24 md:h-24 rounded-full overflow-hidden border-2 sm:border-4 border-white shadow-lg shrink-0 bg-white">
                                <Image
                                    src="/images/gac_logo.png"
                                    alt="Garlic & Chives"
                                    fill
                                    sizes="(max-width: 640px) 40px, (max-width: 768px) 64px, 96px"
                                    className="object-cover"
                                    priority
                                />
                            </div>
                            <div className="flex flex-col justify-center">
                                <h1 className="font-bold text-base sm:text-xl md:text-3xl text-slate-900 leading-none tracking-tight">Garlic & Chives</h1>
                                <span className="text-[10px] sm:text-xs md:text-sm text-primary font-bold uppercase tracking-[0.1em] sm:tracking-[0.2em] mt-0.5 sm:mt-2">Asian Fusion & Bar</span>
                            </div>
                        </div>
                    </div>

                    {/* Cart Button */}
                    <button
                        onClick={toggleCart}
                        className="p-2 sm:p-3 flex items-center gap-2 sm:gap-3 hover:bg-slate-100 rounded-xl text-slate-700 transition-colors relative group border border-transparent hover:border-slate-200"
                    >
                        <ShoppingCart className="w-6 h-6 sm:w-8 sm:h-8 text-slate-600 group-hover:text-primary transition-colors" />
                        {cart.length > 0 && (
                            <span className="absolute -top-1 -right-1 bg-red-500 text-white w-5 h-5 sm:w-6 sm:h-6 rounded-full text-[10px] sm:text-xs flex items-center justify-center font-bold border-2 border-white shadow-sm">
                                {cart.length}
                            </span>
                        )}
                        <div className="hidden sm:flex flex-col items-start">
                            <span className="font-bold text-sm md:text-base group-hover:text-primary transition-colors">My Order</span>
                            {cart.length > 0 && <span className="text-xs text-muted-foreground">{cart.length} items</span>}
                        </div>
                    </button>
                </div>

                {/* Main Content: Always ConciergeView */}
                <div className="flex-1 overflow-hidden relative">
                    <ConciergeView />
                </div>
            </div>

            {/* Modal Overlay */}
            <CartModal />
            <ItemDetailModal />
        </div>
    );
}
