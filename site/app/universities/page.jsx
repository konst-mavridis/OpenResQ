"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Universities() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        <motion.div
          className="text-center sm:text-left mb-16"
          initial={{ opacity: 0, y: -20 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-700">
            OpenResQ for Universities & Research Centers
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl">
            A platform for academic collaboration, research, innovation and real‑world
            data analysis in emergency response.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4"></div>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            A Living Laboratory for Innovation
          </h2>
          <p className="text-neutral-600 text-lg leading-relaxed">
            OpenResQ provides real‑world datasets and operational workflows that
            support academic research in fields such as emergency management,
            data science, IoT, public safety, AI and human‑computer interaction.
          </p>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Opportunities for Collaboration
          </h2>
          <ul className="space-y-4 text-neutral-600 text-lg">
            <li><strong className="text-gray-700">Research partnerships:</strong> Access anonymized datasets and system APIs.</li>
            <li><strong className="text-gray-700">Student projects:</strong> Capstone, thesis and applied research opportunities.</li>
            <li><strong className="text-gray-700">IoT experimentation:</strong> Integrate sensors, drones and smart devices.</li>
            <li><strong className="text-gray-700">Simulation environments:</strong> Model emergency scenarios for training.</li>
            <li><strong className="text-gray-700">Joint publications:</strong> Collaborate on academic papers and conferences.</li>
          </ul>
        </motion.div>

        <motion.div
          className="mt-20 text-center sm:text-left"
          initial={{ opacity: 0, y: 20 }}
        >
          <h3 className="text-3xl font-semibold text-gray-700 mb-4">
            Interested in academic collaboration?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8">
            Let’s explore how OpenResQ can support your research and innovation goals.
          </p>
          <Link href="/contact" className="bg-gray-300 text-primary px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition">
            Contact Our Team
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
