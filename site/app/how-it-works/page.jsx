"use client";

import { motion } from "framer-motion";

export default function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Report",
      description: "A citizen reports an incident through the platform.",
      icon: (
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
          <path d="M9 12h6" />
          <path d="M12 9v6" />
          <rect x="3" y="3" width="18" height="18" rx="2" />
        </svg>
      ),
      highlight: false,
    },
    {
      number: "2",
      title: "Notify",
      description:
        "Nearby volunteers and authorities are notified instantly through real-time alerts.",
      icon: (
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
          <path d="M12 2v4" />
          <path d="M5.5 5.5l2.5 2.5" />
          <path d="M18.5 5.5l-2.5 2.5" />
          <path d="M12 14v8" />
          <circle cx="12" cy="10" r="3" />
        </svg>
      ),
      highlight: true,
    },
    {
      number: "3",
      title: "Respond",
      description:
        "Coordinated response based on location and availability.",
      icon: (
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
          <path d="M2 12h20" />
          <path d="M12 2l4 4-4 4" />
          <path d="M12 22l-4-4 4-4" />
        </svg>
      ),
      highlight: false,
    },
  ];

  return (
    <main className="bg-white min-h-screen py-24 px-6 text-neutral-800">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-700">
            How It Works
          </h1>
          <p className="text-xl text-gray-600 mt-4">
            Simple, fast, and effective emergency response
          </p>
        </motion.div>

        {/* Steps */}
        <div className="grid md:grid-cols-3 gap-10">
          {steps.map((step, index) => (
            <motion.div
              key={step.number}
              className={`p-8 rounded-xl transition shadow-sm hover:shadow-md border ${
                step.highlight
                  ? "bg-neutral-50 border-neutral-200 scale-[1.02]"
                  : "bg-neutral-50 border-neutral-200"
              }`}
              initial={{ opacity: 0, y: 25 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <div className="mb-4">{step.icon}</div>

              <h2 className="text-2xl font-semibold mb-3 text-gray-700">
                {step.title}
              </h2>

              <p className="text-neutral-600 leading-relaxed">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  );
}
