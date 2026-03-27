"use client";

import { motion } from "framer-motion";
import Link from "next/link";

const container = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.15,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 30 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut" },
  },
};

const cards = [
  {
    title: "Municipalities",
    desc: "Tools for local governments to improve emergency coordination and community safety.",
    link: "/municipalities",
  },
  {
    title: "NGOs",
    desc: "Support for humanitarian organizations, field teams and community initiatives.",
    link: "/ngos",
  },
  {
    title: "Emergency Services",
    desc: "Real-time tools for fire departments, rescue units and civil protection.",
    link: "/emergency-services",
  },
  {
    title: "Volunteer Groups",
    desc: "Coordination and communication tools for community-driven response teams.",
    link: "/volunteers",
  },
  {
    title: "Universities & Research",
    desc: "Collaborations for research, innovation, IoT and data-driven studies.",
    link: "/universities",
  },
  {
    title: "Case Studies",
    desc: "Real-world examples of OpenResQ in action across different sectors.",
    link: "/case-studies",
  },
];

export default function Partnerships() {
  return (
    <main className="bg-linear-to-b from-white to-gray-50 min-h-screen py-24 px-6 text-black">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center mb-20"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight">
            Partnerships Hub
          </h1>
          <p className="text-lg text-gray-600 mt-5 max-w-2xl mx-auto leading-relaxed">
            Explore how OpenResQ collaborates with municipalities, NGOs, emergency services,
            volunteer groups and academic institutions to build safer, more resilient communities.
          </p>
          <div className="w-24 h-1 bg-blue-500 rounded mt-6 mx-auto"></div>
        </motion.div>

        {/* Cards */}
        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid md:grid-cols-2 lg:grid-cols-3 gap-10"
        >
          {cards.map((card, i) => (
            <motion.div
              key={i}
              variants={item}
              whileHover={{ y: -6 }}
              className="group bg-white border border-gray-200 p-8 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300"
            >
              <h2 className="text-2xl font-semibold mb-3 group-hover:text-blue-600 transition">
                {card.title}
              </h2>
              <p className="text-gray-600 leading-relaxed mb-6">
                {card.desc}
              </p>
              <Link
                href={card.link}
                className="text-blue-600 font-semibold inline-flex items-center gap-2 group-hover:gap-3 transition-all"
              >
                Learn more →
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          className="text-center mt-24 bg-white border border-gray-200 rounded-2xl p-12 shadow-sm"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-3xl font-semibold mb-4">
            Want to explore a partnership?
          </h3>
          <p className="text-gray-600 max-w-2xl mx-auto mb-8">
            We collaborate with organizations of all sizes. Let’s discuss how OpenResQ
            can support your mission and strengthen your community.
          </p>

          <Link
            href="/contact"
            className="inline-block bg-blue-600 text-white font-semibold px-8 py-3 rounded-xl shadow hover:bg-blue-700 transition"
          >
            Contact Our Team
          </Link>
        </motion.div>

      </div>
    </main>
  );
}
