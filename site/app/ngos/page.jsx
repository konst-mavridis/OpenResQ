"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function ForNGOs() {
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
            OpenResQ for NGOs
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl leading-relaxed">
            Empowering humanitarian organizations with real‑time tools for
            coordination, field operations and community engagement.
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
            Supporting NGOs in the Field
          </h2>
          <p className="text-neutral-600 leading-relaxed text-lg">
            NGOs play a critical role in emergency response, humanitarian aid and
            community support. OpenResQ provides a unified platform where field
            teams, volunteers and coordinators can collaborate seamlessly.
          </p>
          <p className="text-neutral-600 leading-relaxed text-lg mt-4">
            From incident reporting to resource allocation and volunteer
            coordination, the platform enhances operational efficiency and
            improves the speed and accuracy of interventions.
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
            Key Benefits for NGOs
          </h2>

          <ul className="space-y-4 text-neutral-600 text-lg leading-relaxed">
            <li><strong className="text-gray-700">Unified coordination:</strong> Manage volunteers, field teams and operations in one place.</li>
            <li><strong className="text-gray-700">Real‑time reporting:</strong> Receive incident updates directly from citizens or field staff.</li>
            <li><strong className="text-gray-700">Resource management:</strong> Track availability, deployment and needs.</li>
            <li><strong className="text-gray-700">Transparency & accountability:</strong> Document actions and outcomes for donors, partners and authorities.</li>
            <li><strong className="text-gray-700">Scalable collaboration:</strong> Work alongside municipalities, civil protection units and other NGOs.</li>
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
            Interested in using OpenResQ in your organization?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8 leading-relaxed">
            Let’s discuss how OpenResQ can support your mission and enhance your
            operational capabilities.
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
