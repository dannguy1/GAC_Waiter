"use client";
import { useStore } from "@/lib/store";
import { Trash2 } from "lucide-react";

export default function CartTab() {
    const { cart, removeFromCart, clearCart, generalNotes, setGeneralNotes, submitOrder, isOrderVerified } = useStore();

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

            <div className="p-4 border-t bg-slate-50 space-y-4">
                {/* General Notes Section */}
                <div>
                    <label className="block text-xs font-semibold text-slate-500 mb-1 uppercase tracking-wider">
                        Special Instructions / Allergies (Entire Order)
                    </label>
                    <textarea
                        value={generalNotes}
                        onChange={(e) => setGeneralNotes(e.target.value)}
                        placeholder="e.g. Peanut allergy, Extra napkins, Separate checks..."
                        className="w-full text-sm p-3 rounded-lg border border-slate-200 focus:border-primary focus:ring-1 focus:ring-primary outline-none min-h-[80px] resize-none"
                    />
                </div>

                <div className="flex justify-between items-center pt-2 border-t border-slate-200">
                    <span className="font-semibold text-lg text-slate-700">Total</span>
                    <span className="font-bold text-2xl text-primary">${total.toFixed(2)}</span>
                </div>

                {!isOrderVerified && cart.length > 0 && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
                        <strong>Please confirm with waiter:</strong>
                        <p>You must ask the waiter to verify your order and allergies before checking out.</p>
                    </div>
                )}

                <button
                    disabled={!isOrderVerified}
                    onClick={async () => {
                        try {
                            const response = await submitOrder();
                            if (response) {
                                alert(`Order Confirmed!\n\nTotal: $${response.total.toFixed(2)}\n\n(Backend Validated)`);
                            }
                        } catch (e) {
                            alert("Failed to submit order. Please try again.");
                        }
                    }}
                    className={`w-full py-3 rounded-lg font-bold transition-all shadow-md flex items-center justify-center gap-2
                        ${isOrderVerified
                            ? "bg-primary text-white hover:bg-primary/90 active:scale-95"
                            : "bg-slate-300 text-slate-500 cursor-not-allowed"}`}
                >
                    Submit Order
                </button>
            </div>
        </div>
    );
}
