"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Partnerships() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-black">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-black">
            Partnerships Hub
          </h1>
          <p className="text-lg text-black/70 mt-4 max-w-2xl mx-auto leading-relaxed">
            Explore how OpenResQ collaborates with municipalities, NGOs, emergency services,
            volunteer groups and academic institutions to build safer, more resilient communities.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto"></div>
        </motion.div>

        {/* Partnership Categories */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10">

          {/* Municipalities */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">Municipalities</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Tools for local governments to improve emergency coordination and community safety.
            </p>
            <Link href="/municipalities" className="text-primary font-semibold hover:underline">
              Learn more →
            </Link>
          </motion.div>

          {/* NGOs */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">NGOs</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Support for humanitarian organizations, field teams and community initiatives.
            </p>
            <Link href="/ngos" className="text-primary font-semibold hover:underline">
              Learn more →
            </Link>
          </motion.div>

          {/* Emergency Services */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">Emergency Services</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Real‑time tools for fire departments, rescue units and civil protection.
            </p>
            <Link href="/emergency-services" className="text-primary font-semibold hover:underline">
              Learn more →
            </Link>
          </motion.div>

          {/* Volunteer Groups */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">Volunteer Groups</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Coordination and communication tools for community‑driven response teams.
            </p>
            <Link href="/volunteers" className="text-primary font-semibold hover:underline">
              Learn more →
            </Link>
          </motion.div>

          {/* Universities */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">Universities & Research</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Collaborations for research, innovation, IoT and data‑driven studies.
            </p>
            <Link href="/universities" className="text-primary font-semibold hover:underline">
              Learn more →
            </Link>
          </motion.div>

          {/* Case Studies */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-black mb-3">Case Studies</h2>
            <p className="text-black/70 leading-relaxed mb-6">
              Real‑world examples of OpenResQ in action across different sectors.
            </p>
            <Link href="/case-studies" className="text-primary font-semibold hover:underline">
              View case studies →
            </Link>
          </motion.div>

        </div>

        {/* CTA */}
        <motion.div
          className="text-center mt-20"
          initial={{ opacity: 0, y: 20 }}
        >
          <h3 className="text-3xl font-semibold text-black mb-4">
            Want to explore a partnership?
          </h3>
          <p className="text-black/70 max-w-2xl mx-auto mb-8">
            We collaborate with organizations of all sizes. Let’s discuss how OpenResQ
            can support your mission and strengthen your community.
          </p>

          <Link
            href="/contact"
            className="inline-block bg-gray-300 text-primary font-semibold px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition"
          >
            Contact Our Team
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
