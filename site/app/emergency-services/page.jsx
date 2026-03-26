"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function EmergencyServices() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        <motion.div
          className="text-center sm:text-left mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-700">
            OpenResQ for Emergency Services
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl">
            Real‑time situational awareness and coordinated response tools for
            fire departments, rescue teams, civil protection units and first responders.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4"></div>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Faster, Smarter, Safer Response
          </h2>
          <p className="text-neutral-600 text-lg leading-relaxed">
            Emergency services rely on accurate information and rapid coordination.
            OpenResQ provides a unified operational dashboard where teams can view
            active incidents, assess severity, assign units and track progress in real time.
          </p>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Key Capabilities
          </h2>
          <ul className="space-y-4 text-neutral-600 text-lg">
            <li><strong className="text-gray-700">Live incident map:</strong> View all active events instantly.</li>
            <li><strong className="text-gray-700">Severity assessment:</strong> Prioritize incidents based on urgency.</li>
            <li><strong className="text-gray-700">Unit assignment:</strong> Dispatch teams and track their status.</li>
            <li><strong className="text-gray-700">Operational timeline:</strong> Monitor every step from report to resolution.</li>
            <li><strong className="text-gray-700">Cross‑agency collaboration:</strong> Work seamlessly with municipalities, NGOs and volunteers.</li>
          </ul>
        </motion.div>

        <motion.div
          className="mt-20 text-center sm:text-left"
          initial={{ opacity: 0, y: 20 }}
        >
          <h3 className="text-3xl font-semibold text-gray-700 mb-4">
            Bring OpenResQ to your emergency service unit
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8">
            Contact our team to explore how OpenResQ can support your operations.
          </p>
          <Link href="/contact" className="bg-gray-300 text-primary px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition">
            Contact Us
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
