"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function ForMunicipalities() {
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
            OpenResQ for Municipalities
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl leading-relaxed">
            A modern emergency‑response platform designed to strengthen local
            preparedness, improve coordination and enhance community safety.
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
            Strengthening Municipal Emergency Response
          </h2>
          <p className="text-neutral-600 leading-relaxed text-lg">
            Municipalities face increasing challenges in managing emergencies,
            from fires and floods to accidents and public safety incidents.
            OpenResQ provides a unified digital environment where citizens,
            responders and municipal teams collaborate in real time.
          </p>
          <p className="text-neutral-600 leading-relaxed text-lg mt-4">
            With instant incident reporting, live dashboards and structured
            workflows, municipalities gain faster situational awareness and
            improved operational efficiency.
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
            Key Benefits for Municipalities
          </h2>

          <ul className="space-y-4 text-neutral-600 text-lg leading-relaxed">
            <li><strong className="text-gray-700">Real‑time incident visibility:</strong> Monitor all active events on a live map.</li>
            <li><strong className="text-gray-700">Faster coordination:</strong> Assign responders and track progress instantly.</li>
            <li><strong className="text-gray-700">Citizen engagement:</strong> Empower residents to contribute to public safety.</li>
            <li><strong className="text-gray-700">Data insights:</strong> Identify hotspots, trends and response times.</li>
            <li><strong className="text-gray-700">Scalable integration:</strong> Connect with local volunteer groups, civil protection units and municipal services.</li>
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
            Interested in using OpenResQ in your municipality?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8 leading-relaxed">
            Contact our team to explore how OpenResQ can support your local
            emergency response strategy.
          </p>

          <Link
            href="/contact"
            className="inline-block bg-gray-300 text-primary font-semibold px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition"
          >
            Contact Us
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
