"use client";

import { motion } from "framer-motion";

export default function Platform() {
  return (
    <main className="bg-white min-h-screen text-neutral-800">
      <div className="max-w-5xl mx-auto py-24 px-6">

        {/* Header */}
        <motion.div
          className="mb-16 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-700">
            The Platform
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mt-4 leading-relaxed">
            A comprehensive emergency response system designed to connect citizens,
            responders, and authorities seamlessly.
          </p>
        </motion.div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-10">

          {/* Card 1 */}
          <motion.div
            className="bg-white border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            {/* Icon */}
            <div className="mb-4">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#1E3A8A"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>

            <h2 className="text-xl font-semibold mb-3 text-gray-700">
              Incident Reporting
            </h2>
            <p className="text-neutral-600 leading-relaxed">
              Citizens can report incidents in real-time using intuitive map-based tools.
              Submit photos, location details, and incident descriptions instantly.
            </p>
          </motion.div>

          {/* Card 2 */}
          <motion.div
            className="bg-white border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            {/* Icon */}
            <div className="mb-4">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#1E3A8A"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="11" width="18" height="10" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>

            <h2 className="text-xl font-semibold mb-3 text-gray-700">
              Role-based Access
            </h2>
            <p className="text-neutral-600 leading-relaxed">
              Customized interfaces for citizens, emergency responders, and authorities.
              Each role has tailored features and permissions for optimal efficiency.
            </p>
          </motion.div>

          {/* Card 3 */}
          <motion.div
            className="bg-white border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Icon */}
            <div className="mb-4">
              <svg
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#1E3A8A"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M9 12l2 2 4-4" />
                <circle cx="12" cy="12" r="10" />
              </svg>
            </div>

            <h2 className="text-xl font-semibold mb-3 text-gray-700">
              Secure & Transparent
            </h2>
            <p className="text-neutral-600 leading-relaxed">
              Data integrity, full traceability, and GDPR-compliant design.
              Trust and transparency at every step.
            </p>
          </motion.div>

        </div>
      </div>
    </main>
  );
}
