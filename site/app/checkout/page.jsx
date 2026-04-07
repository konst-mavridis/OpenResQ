"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";

function CheckoutContent() {
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan") || "basic";
  
  const [formData, setFormData] = useState({
    orgName: "",
    email: "",
    name: "",
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const plans = {
    basic: { name: "Basic", price: 100, setup: 500 },
    pro: { name: "Pro", price: 250, setup: 1500 },
  };

  const plan = plans[planId] || plans.basic;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          planId,
          ...formData
        }),
      });

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      } else {
        throw new Error(data.error || "Failed to create checkout session");
      }
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-24 px-6 text-black">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid md:grid-cols-2 gap-12"
      >
        {/* Form */}
        <div>
          <h1 className="text-3xl font-bold mb-8 text-white">Deploy OpenResQ</h1>
          
          <form onSubmit={handleSubmit} className="space-y-6 bg-white p-8 rounded-2xl border border-neutral-200">
            <div>
              <label className="block text-sm font-semibold mb-2">Organization / Municipality Name</label>
              <input 
                type="text" 
                required
                placeholder="e.g. Athens Municipality"
                className="w-full border border-neutral-300 rounded-lg px-4 py-3 focus:border-primary outline-none transition"
                value={formData.orgName}
                onChange={(e) => setFormData({...formData, orgName: e.target.value})}
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold mb-2">Admin Name</label>
              <input 
                type="text" 
                required
                placeholder="Manager Name"
                className="w-full border border-neutral-300 rounded-lg px-4 py-3 focus:border-primary outline-none transition"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Admin Email</label>
              <input 
                type="email" 
                required
                placeholder="admin@organization.com"
                className="w-full border border-neutral-300 rounded-lg px-4 py-3 focus:border-primary outline-none transition"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white font-bold py-4 rounded-xl bg-zinc-800 hover:bg-zinc-700 cursor-pointer transition disabled:opacity-50"
            >
              {loading ? "Preparing Checkout..." : `Proceed to Payment — €${plan.price + plan.setup}`}
            </button>
            <p className="text-xs text-neutral-500 text-center">
              You will be redirected to Stripe for secure payment processing.
            </p>
          </form>
        </div>

        {/* Summary */}
        <div className="bg-neutral-50 p-8 rounded-2xl border border-neutral-200 self-start">
          <h2 className="text-xl font-bold mb-6">Order Summary</h2>
          <div className="space-y-4 text-neutral-600">
            <div className="flex justify-between">
              <span>{plan.name} Subscription (Monthly)</span>
              <span className="font-bold text-black">€{plan.price}</span>
            </div>
            <div className="flex justify-between">
              <span>One-time Setup Fee</span>
              <span className="font-bold text-black">€{plan.setup}</span>
            </div>
            <div className="h-px bg-neutral-200 my-4" />
            <div className="flex justify-between text-xl font-bold text-black">
              <span>Total Due Today</span>
              <span>€{plan.price + plan.setup}</span>
            </div>
          </div>

          <div className="mt-8 space-y-4">
            <h3 className="font-bold text-black">What's included:</h3>
            <ul className="text-sm space-y-2">
              <li className="flex gap-2">✅ Full Operational Dashboard</li>
              <li className="flex gap-2">✅ Citizen Mobile Reporting System</li>
              <li className="flex gap-2">✅ Responder Coordination Tools</li>
              <li className="flex gap-2">✅ Cloud Hosting & Support</li>
            </ul>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div className="min-h-screen grid place-items-center">Loading...</div>}>
      <CheckoutContent />
    </Suspense>
  );
}
