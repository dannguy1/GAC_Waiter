"use client";
import CartTab from "../cart/CartTab";

export default function OrderView() {
    return (
        <div className="h-full bg-slate-50 p-4 md:p-8">
            <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-sm h-full flex flex-col overflow-hidden border border-slate-200">
                <div className="p-4 border-b bg-white">
                    <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                        🍽️ My Current Order
                    </h2>
                    <p className="text-sm text-muted-foreground">Review your items before submitting to the kitchen.</p>
                </div>
                <CartTab />
            </div>
        </div>
    );
}
