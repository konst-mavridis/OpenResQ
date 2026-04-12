"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function SuccessPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-6">
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center max-w-md"
      >
        <div className="bg-emerald-100 text-emerald-600 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-8">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
            <polyline points="20 6 9 17 4 12" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>
        <p className="text-neutral-600 mb-10 leading-relaxed">
          Thank you for choosing OpenResQ. We are preparing your dedicated operational environment. 
          You will receive an email shortly with instructions on how to access your dashboard.
        </p>
        
        <Link 
          href="/"
          className="inline-block bg-gray-600 text-white font-bold px-8 py-3 rounded-lg hover:bg-emerald-700 transition"
        >
          Return Home
        </Link>
      </motion.div>
    </div>
  );
}
