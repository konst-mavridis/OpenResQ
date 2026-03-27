"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Volunteers() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center sm:text-left mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-700">
            Volunteer Groups
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl leading-relaxed">
            Empowering community-driven response teams to make a difference.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto sm:mx-0"></div>
        </motion.div>

        {/* Section 1 */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">
            Community Response
          </h2>
          <p className="text-neutral-600 leading-relaxed text-lg">
            Stay organized and informed in real-time with instant notifications and clear coordination during emergencies.
          </p>
        </motion.div>

        {/* Section 2 */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">
            What You Gain
          </h2>

          <ul className="space-y-4 text-neutral-600 text-lg leading-relaxed">
            <li><strong className="text-gray-700">Instant alerts:</strong> Be the first to know about incidents in your area.</li>
            <li><strong className="text-gray-700">Clear instructions:</strong> Receive guidance from coordinators in real-time.</li>
            <li><strong className="text-gray-700">Team coordination:</strong> Work seamlessly with other volunteers and professionals.</li>
            <li><strong className="text-gray-700">Safety monitoring:</strong> Track your team members and ensure everyone stays safe.</li>
            <li><strong className="text-gray-700">Community impact:</strong> Make a measurable difference in your community.</li>
          </ul>
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center sm:text-left mt-20"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h3 className="text-3xl font-semibold text-gray-700 mb-4">
            Ready to onboard your volunteer team?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8 leading-relaxed">
            Contact our team to set up OpenResQ for your volunteer group and start saving lives.
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