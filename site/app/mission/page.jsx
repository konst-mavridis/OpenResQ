"use client";

import { motion } from "framer-motion";

export default function Mission() {
  return (
    <main className="py-24 px-6 bg-white text-neutral-800">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.header
          className="mb-16 text-center sm:text-left"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-gray-700">
            Our Mission
          </h1>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto sm:mx-0"></div>
        </motion.header>

        {/* Sections */}
        <section className="space-y-12">

          {/* Card 1 */}
          <motion.div
            className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
            initial={{ opacity: 0, y: 25 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <h2 className="text-2xl font-semibold mb-3 text-gray-700">
              Transforming Emergency Response
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              OpenResQ aims to reduce emergency response times by enabling
              real-time coordination between citizens, volunteers and authorities.
              We empower communities to act quickly when every second counts.
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
              Core Values
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              We believe open data, transparency and collaboration can save lives.
              By breaking down barriers between responders and communities, we create
              a network of trust and accountability that strengthens public safety.
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
              Our Vision
            </h2>
            <p className="text-neutral-600 leading-relaxed text-lg">
              The platform is designed to be open, scalable and adaptable
              to local communities and public protection agencies worldwide.
              Together, we&apos;re building the future of emergency response.
            </p>
          </motion.div>

        </section>
      </div>
    </main>
  );
}
