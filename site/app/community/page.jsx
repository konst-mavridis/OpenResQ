"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Community() {
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
            Community & Partnerships
          </h1>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto sm:mx-0"></div>
        </motion.div>

        {/* Content Cards */}
        <section className="space-y-10">

          {/* Card 1 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-2xl font-semibold mb-3 text-gray-700">
              A Community-Driven Initiative
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              OpenResQ is powered by volunteers, developers, NGOs, municipalities,
              and research institutions who share a common goal: improving public
              safety through collaboration and innovation.
            </p>
          </motion.div>

          {/* Card 2 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h2 className="text-2xl font-semibold mb-3 text-gray-700">
              Partnerships That Matter
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              We actively seek partnerships with public authorities, universities,
              emergency response organizations, and civic groups. By connecting
              diverse stakeholders, we create a unified ecosystem that strengthens
              preparedness and response capabilities.
            </p>
          </motion.div>

          {/* Card 3 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <h2 className="text-2xl font-semibold mb-3 text-gray-700">
              Building Resilient Communities
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              Our long-term vision is to establish a sustainable, open, and
              community-driven network that supports real-world emergency
              operations, training programs, academic research, and civic
              engagement.
            </p>
          </motion.div>

        </section>

        {/* CTA */}
        <motion.div
          className="mt-16 text-center sm:text-left"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Link
            href="/join"
            className="inline-block bg-gray-300 text-primary font-semibold px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition"
          >
            Become a Partner
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
