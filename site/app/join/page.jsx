"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Join() {
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
            Partner With OpenResQ
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl leading-relaxed">
            A modern emergency‑response platform designed for municipalities, NGOs,
            public agencies and organizations seeking smarter, faster and more
            coordinated incident management.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto sm:mx-0"></div>
        </motion.div>

        {/* Section 1 — What OpenResQ Is */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">
            What Is OpenResQ
          </h2>
          <p className="text-neutral-600 leading-relaxed text-lg">
            OpenResQ is a next‑generation emergency reporting and coordination
            platform. Citizens can instantly report incidents — such as fires,
            accidents, missing persons or hazards — by submitting location,
            description and optional media. These reports appear immediately on a
            live operational dashboard used by responders, volunteers and
            authorized agencies.
          </p>
          <p className="text-neutral-600 leading-relaxed text-lg mt-4">
            The platform enables faster situational awareness, better allocation
            of resources and more coordinated response actions. Every incident is
            tracked from the moment it is reported until it is resolved, creating
            a transparent and structured workflow.
          </p>
        </motion.div>

        {/* Section 2 — Why Organizations Join */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">
            Why Municipalities, NGOs & Agencies Join
          </h2>

          <ul className="space-y-4 text-neutral-600 text-lg leading-relaxed">
            <li>
              <strong className="text-gray-700">Real‑time incident visibility:</strong>{" "}
              Access a live dashboard with all active reports on a map.
            </li>
            <li>
              <strong className="text-gray-700">Faster response coordination:</strong>{" "}
              Assign responders, track progress and manage operations efficiently.
            </li>
            <li>
              <strong className="text-gray-700">Community engagement:</strong>{" "}
              Empower citizens to contribute to public safety.
            </li>
            <li>
              <strong className="text-gray-700">Data‑driven decision making:</strong>{" "}
              Analyze incident patterns, hotspots and response times.
            </li>
            <li>
              <strong className="text-gray-700">Scalable & flexible:</strong>{" "}
              Suitable for municipalities, volunteer groups, NGOs, universities,
              civil protection units and more.
            </li>
          </ul>
        </motion.div>

        {/* Section 3 — Future Vision */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-gray-700">
            Our Vision: A Complete Smart‑Rescue Ecosystem
          </h2>
          <p className="text-neutral-600 leading-relaxed text-lg">
            OpenResQ aims to evolve into a fully integrated smart‑rescue system.
            Beyond software, the platform will incorporate IoT devices, sensors,
            drones and specialized hardware for automated detection and real‑time
            data transmission.
          </p>
          <p className="text-neutral-600 leading-relaxed text-lg mt-4">
            This hybrid approach — combining human reports with automated
            intelligence — will significantly enhance accuracy, speed and
            operational readiness for emergency teams.
          </p>
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
            Interested in partnering with OpenResQ?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8 leading-relaxed">
            If you represent a municipality, NGO, emergency response unit or
            public organization, we would be happy to discuss how OpenResQ can
            support your operations and community.
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
