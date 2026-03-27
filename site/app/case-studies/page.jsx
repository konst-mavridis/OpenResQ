"use client";

import { motion } from "framer-motion";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0 },
};

export default function CaseStudies() {
  return (
    <main className="bg-linear-to-b from-white to-gray-50 min-h-screen py-24 px-6">
      <div className="max-w-5xl mx-auto">

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-20 text-center">
          <h1 className="text-5xl font-bold mb-4">Case Studies</h1>
          <p className="text-gray-600 text-lg max-w-2xl mx-auto">
            Real-world impact of OpenResQ.
          </p>
        </motion.div>

        <motion.div variants={container} initial="hidden" animate="show" className="space-y-10">
          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">Wildfire Response</h2>
            <p className="text-gray-600">
              Coordinated responders and optimized resources.
            </p>
          </motion.div>

          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">Missing Person Search</h2>
            <p className="text-gray-600">
              Faster coordination between teams and authorities.
            </p>
          </motion.div>
        </motion.div>

      </div>
    </main>
  );
}