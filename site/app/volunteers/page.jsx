"use client";

import { motion } from "framer-motion";
import Link from "next/link";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0 },
};

export default function Volunteers() {
  return (
    <main className="bg-linear-to-b from-white to-gray-50 min-h-screen py-24 px-6">
      <div className="max-w-5xl mx-auto">

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="mb-20">
          <h1 className="text-5xl font-bold mb-4">Volunteer Groups</h1>
          <p className="text-gray-600 text-lg max-w-2xl">
            Empowering community-driven response teams.
          </p>
        </motion.div>

        <motion.div variants={container} initial="hidden" animate="show" className="space-y-10">
          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">Community Response</h2>
            <p className="text-gray-600">
              Stay organized and informed in real-time.
            </p>
          </motion.div>

          <motion.div variants={item} className="bg-white p-8 rounded-2xl shadow-sm border">
            <h2 className="text-2xl font-semibold mb-4">What You Gain</h2>
            <ul className="space-y-3 text-gray-600">
              <li>Instant alerts</li>
              <li>Clear instructions</li>
              <li>Team coordination</li>
              <li>Safety monitoring</li>
              <li>Community impact</li>
            </ul>
          </motion.div>
        </motion.div>

        <motion.div variants={item} className="mt-24 text-center bg-white p-12 rounded-2xl shadow-sm border">
          <h3 className="text-3xl font-semibold mb-4">Onboard your team</h3>
          <Link href="/contact" className="bg-blue-600 text-white px-8 py-3 rounded-xl hover:bg-blue-700">
            Contact Our Team
          </Link>
        </motion.div>

      </div>
    </main>
  );
}