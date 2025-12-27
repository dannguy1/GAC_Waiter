"use client";
import { useStore } from "@/lib/store";
import { Trash2 } from "lucide-react";

export default function CartTab() {
    const { cart, removeFromCart, clearCart } = useStore();

    const total = cart.reduce((sum, item) => sum + (item.item.price * item.quantity), 0);

    if (cart.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center flex-1 p-8 text-center text-muted-foreground">
                <p>Your cart is empty.</p>
                <p className="text-sm mt-2">Add items from the menu or ask the concierge!</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col flex-1 h-full overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {cart.map((cartItem, idx) => (
                    <div key={idx} className="flex gap-4 p-3 bg-white rounded-lg border border-slate-100 shadow-sm">
                        <div className="flex-1">
                            <div className="flex justify-between">
                                <h4 className="font-semibold text-slate-900">{cartItem.item.item_name}</h4>
                                <span className="font-medium text-slate-600">${(cartItem.item.price * cartItem.quantity).toFixed(2)}</span>
                            </div>
                            <div className="text-sm text-slate-500">
                                Qty: {cartItem.quantity}
                                {cartItem.notes && <span className="block italic text-xs mt-1">Note: {cartItem.notes}</span>}
                            </div>
                        </div>
                        <button
                            onClick={() => removeFromCart(idx)}
                            className="text-slate-400 hover:text-red-500 transition-colors p-1"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>

            <div className="p-4 border-t bg-slate-50">
                <div className="flex justify-between items-center mb-4">
                    <span className="font-semibold text-lg text-slate-700">Total</span>
                    <span className="font-bold text-2xl text-primary">${total.toFixed(2)}</span>
                </div>
                <button
                    onClick={() => {
                        // TODO: Implement actual checkout using /v1/checkout endpoint
                        alert("Order Submitted! (Demo mode - checkout not yet implemented)");
                        clearCart();
                    }}
                    className="w-full bg-primary text-white py-3 rounded-lg font-bold hover:bg-primary/90 transition-all shadow-md active:scale-95"
                >
                    Submit Order
                </button>
            </div>
        </div>
    );
}
