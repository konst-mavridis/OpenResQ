"use client";

import { motion } from "framer-motion";
import Link from "next/link";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function EmergencyServices() {
  return (
    <main className="bg-linear-to-b from-white to-gray-50 min-h-screen py-24 px-6">
      <div className="max-w-5xl mx-auto">

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-20">
          <h1 className="text-5xl font-bold mb-4">Emergency Services</h1>
          <p className="text-gray-600 text-lg max-w-2xl">
            Real-time situational awareness and coordinated response tools.
          </p>
        </motion.div>

        <motion.div variants={container} initial="hidden" animate="show" className="space-y-10">
          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">Faster, Smarter Response</h2>
            <p className="text-gray-600">
              Unified dashboard for incidents, teams and operations.
            </p>
          </motion.div>

          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">Key Capabilities</h2>
            <ul className="space-y-3 text-gray-600">
              <li>Live incident map</li>
              <li>Severity prioritization</li>
              <li>Unit tracking</li>
              <li>Timeline monitoring</li>
              <li>Cross-agency collaboration</li>
            </ul>
          </motion.div>
        </motion.div>

        <motion.div variants={item} className="mt-24 text-center bg-white p-12 rounded-2xl shadow-sm border">
          <h3 className="text-3xl font-semibold mb-4">Bring OpenResQ to your unit</h3>
          <Link href="/contact" className="bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700">
            Contact Our Team
          </Link>
        </motion.div>

      </div>
    </main>
  );
}