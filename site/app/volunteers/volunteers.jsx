"use client";

import { motion } from "framer-motion";
import Link from "next/link";

export default function Volunteers() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        <motion.div
          className="text-center sm:text-left mb-16"
          initial={{ opacity: 0, y: -20 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-700">
            OpenResQ for Volunteer Groups
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl">
            Empowering volunteer teams with tools for coordination, communication
            and rapid response.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4"></div>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Supporting Community‑Driven Response
          </h2>
          <p className="text-neutral-600 text-lg leading-relaxed">
            Volunteer groups are essential in emergency response. OpenResQ helps
            teams stay organized, informed and ready to act by providing real‑time
            alerts, incident details and communication tools.
          </p>
        </motion.div>

        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm mb-12"
          initial={{ opacity: 0, y: 25 }}
        >
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            What Volunteer Groups Gain
          </h2>
          <ul className="space-y-4 text-neutral-600 text-lg">
            <li><strong className="text-gray-700">Instant alerts:</strong> Receive notifications for nearby incidents.</li>
            <li><strong className="text-gray-700">Clear instructions:</strong> Access incident details and response guidelines.</li>
            <li><strong className="text-gray-700">Team coordination:</strong> Track who is responding and where.</li>
            <li><strong className="text-gray-700">Safety monitoring:</strong> Improve situational awareness during operations.</li>
            <li><strong className="text-gray-700">Community impact:</strong> Strengthen local resilience and preparedness.</li>
          </ul>
        </motion.div>

        <motion.div
          className="mt-20 text-center sm:text-left"
          initial={{ opacity: 0, y: 20 }}
        >
          <h3 className="text-3xl font-semibold text-gray-700 mb-4">
            Want to onboard your volunteer group?
          </h3>
          <p className="text-neutral-600 max-w-2xl mb-8">
            We’d be happy to help your team get started with OpenResQ.
          </p>
          <Link href="/contact" className="bg-gray-300 text-primary px-8 py-3 rounded-lg shadow-sm hover:bg-neutral-500 transition">
            Contact Us
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
