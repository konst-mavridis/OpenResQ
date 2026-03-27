"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Pricing() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-black">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-black">
            Pricing Model
          </h1>
          <p className="text-lg text-black/70 mt-4 max-w-2xl mx-auto leading-relaxed">
            A hybrid pricing model combining a one‑time setup cost with a flexible
            monthly subscription — designed to support both the initial deployment
            and the continuous operation of OpenResQ.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto"></div>
        </motion.div>

        {/* One-Time Payment */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-10 rounded-xl shadow-sm hover:shadow-md transition mb-16"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl font-semibold text-black mb-4">One‑Time Setup Cost</h2>

          <p className="text-black/70 text-lg leading-relaxed">
            Organizations pay an initial one‑time fee ranging from <strong>500€ to 2.000€</strong>,
            depending on their size and customization needs. This cost covers:
          </p>

          <ul className="mt-6 space-y-3 text-black/80 text-lg">
            <li>• Installation and configuration of the platform</li>
            <li>• Dashboard setup and customization</li>
            <li>• Basic user training and onboarding</li>
            <li>• Initial system optimization</li>
          </ul>
        </motion.div>

        {/* Monthly Subscription */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-10 rounded-xl shadow-sm hover:shadow-md transition mb-16"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl font-semibold text-black mb-4">Monthly Subscription</h2>

          <p className="text-black/70 text-lg leading-relaxed">
            After installation, OpenResQ operates through a monthly subscription that
            covers hosting, real‑time data processing, updates, support and analytics.
          </p>

          <div className="grid md:grid-cols-3 gap-8 mt-10">

            {/* Basic */}
            <div className="bg-white border border-neutral-200 p-6 rounded-xl shadow-sm">
              <h3 className="text-2xl font-semibold text-black mb-2">Basic —100€/month</h3>
              <p className="text-black/70 leading-relaxed mb-4">
                For small teams or volunteer groups.
              </p>
              <ul className="space-y-2 text-black/80">
                <li>• Basic dashboard access</li>
                <li>• Incident viewing</li>
                <li>• Limited responders</li>
              </ul>
            </div>

            {/* Pro */}
            <div className="bg-white border border-neutral-200 p-6 rounded-xl shadow-sm scale-[1.02]">
              <h3 className="text-2xl font-semibold text-black mb-2">Pro — 250€/month</h3>
              <p className="text-black/70 leading-relaxed mb-4">
                Ideal for small municipalities or organized rescue teams.
              </p>
              <ul className="space-y-2 text-black/80">
                <li>• Real‑time updates</li>
                <li>• Full incident management</li>
                <li>• More users</li>
                <li>• Basic analytics</li>
              </ul>
            </div>

            {/* Enterprise */}
            <div className="bg-white border border-neutral-200 p-6 rounded-xl shadow-sm">
              <h3 className="text-2xl font-semibold text-black mb-2">Enterprise — Contact us</h3>
              <p className="text-black/70 leading-relaxed mb-4">
                For large organizations with advanced needs.
              </p>
              <ul className="space-y-2 text-black/80">
                <li>• Advanced analytics</li>
                <li>• Incident prioritization</li>
                <li>• Real‑time support</li>
                <li>• Custom features & integrations</li>
              </ul>
            </div>

          </div>

          <p className="text-black/70 text-lg leading-relaxed mt-8">
            Enterprise pricing may increase depending on the number of users,
            data volume and additional requirements.
          </p>
        </motion.div>

        {/* IoT Expansion */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-10 rounded-xl shadow-sm hover:shadow-md transition mb-16"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl font-semibold text-black mb-4">Future IoT & Hardware Integration</h2>

          <p className="text-black/70 text-lg leading-relaxed">
            As OpenResQ expands with IoT devices, the one‑time cost may include
            hardware purchases (e.g., sensors, drones, smart rescue units) ranging
            from <strong>+200€ to 500€ per device</strong>.
          </p>

          <p className="text-black/70 text-lg leading-relaxed mt-4">
            The monthly subscription will then cover device connectivity, data
            management and analytics.
          </p>
        </motion.div>

        {/* Summary */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-10 rounded-xl shadow-sm hover:shadow-md transition"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="text-3xl font-semibold text-black mb-4">Why This Model Works</h2>

          <ul className="space-y-3 text-black/80 text-lg">
            <li>• Low entry cost for small teams</li>
            <li>• Stable recurring revenue for sustainability</li>
            <li>• Scalable for large organizations</li>
            <li>• Supports long‑term innovation and growth</li>
          </ul>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center mt-20"
          initial={{ opacity: 0, y: 20 }}
        >
          <Link
            href="/contact"
            className="bg-gray-300 text-primary font-semibold px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition"
          >
            Request a Custom Quote
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
