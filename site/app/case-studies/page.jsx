"use client";

import { motion } from "framer-motion";

export default function CaseStudies() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-700">
            Case Studies
          </h1>
          <p className="text-lg text-gray-600 mt-4 max-w-2xl mx-auto">
            Real‑world examples of how OpenResQ improves emergency response and
            community resilience.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto"></div>
        </motion.div>

        <div className="space-y-12">

          {/* Case 1 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-gray-700 mb-3">
              Wildfire Response Optimization
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              A municipality used OpenResQ to coordinate volunteers and fire
              services during a wildfire event. Real‑time citizen reports helped
              responders identify hotspots faster and allocate resources more
              effectively.
            </p>
          </motion.div>

          {/* Case 2 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
          >
            <h2 className="text-2xl font-semibold text-gray-700 mb-3">
              Missing Person Search Coordination
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              Volunteer groups and local authorities collaborated through
              OpenResQ to track sightings, coordinate search teams and share
              updates instantly, reducing search time significantly.
            </p>
          </motion.div>

        </div>

      </div>
    </main>
  );
}
