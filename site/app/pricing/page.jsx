"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Pricing() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-6xl mx-auto">

        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-700">
            Pricing & Plans
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">
            Flexible plans for municipalities, NGOs, emergency services and organizations
            of all sizes.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto"></div>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-10">

          {/* Plan 1 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Starter</h2>
            <p className="text-neutral-600 mb-6">Ideal for small volunteer groups or pilot deployments.</p>
            <ul className="space-y-3 text-neutral-600">
              <li>✓ Basic incident reporting</li>
              <li>✓ Live dashboard</li>
              <li>✓ Up to X users</li>
            </ul>
          </motion.div>

          {/* Plan 2 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition scale-[1.02]"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Professional</h2>
            <p className="text-neutral-600 mb-6">For municipalities, NGOs and mid‑sized organizations.</p>
            <ul className="space-y-3 text-neutral-600">
              <li>✓ Full dashboard access</li>
              <li>✓ Team management</li>
              <li>✓ Priority support</li>
              <li>✓ API access</li>
            </ul>
          </motion.div>

          {/* Plan 3 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Enterprise</h2>
            <p className="text-neutral-600 mb-6">For large agencies and multi‑region deployments.</p>
            <ul className="space-y-3 text-neutral-600">
              <li>✓ Custom integrations</li>
              <li>✓ IoT & hardware support</li>
              <li>✓ Dedicated onboarding</li>
              <li>✓ Unlimited users</li>
            </ul>
          </motion.div>

        </div>

        <motion.div
          className="text-center mt-20"
          initial={{ opacity: 0, y: 20 }}
        >
          <Link href="/contact" className="bg-gray-300 text-primary px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition">
            Request a Quote
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
