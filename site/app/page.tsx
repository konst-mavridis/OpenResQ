"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useState } from "react";

// Online SVG URLs
const featureIllustrations = [
  "https://cdn-icons-png.flaticon.com/512/18251/18251095.png",
  "https://www.svgrepo.com/show/135799/volunteer.svg",
  "https://www.svgrepo.com/show/424993/security.svg"
];

const stepIllustrations = [
  "https://cdn-icons-png.flaticon.com/512/18142/18142320.png",
  "https://www.svgrepo.com/show/489066/notifications-active.svg",
  "https://www.svgrepo.com/show/197425/alarm-siren.svg"
];

const faqData = [
  {
    question: "What is OpenResQ?",
    answer: "OpenResQ is a student project platform connecting citizens and volunteers for emergency response."
  },
  {
    question: "Who can join?",
    answer: "Anyone interested in helping or testing the platform can join as a citizen, volunteer, or developer."
  },
  {
    question: "How is my data handled?",
    answer: "All data is handled securely with privacy in mind; the platform respects GDPR principles."
  }
];

export default function Home() {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  return (
    <main className="bg-white text-blue-600">
      {/* Hero Section */}
      <motion.section
        className="min-h-[70vh] md:min-h-screen bg-gradient-to-b from-blue-600 to-white flex flex-col justify-center items-center text-center px-4 sm:px-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 md:mb-6 text-white">OpenResQ</h1>
        <p className="text-base sm:text-lg max-w-xl md:max-w-2xl mb-6 md:mb-8 text-white">
          A community-driven platform designed to connect citizens and volunteers
          for faster and smarter emergency response.
          <br />
          Currently in development as part of a student project for competitions and demos.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full max-w-md">
          <Link
            href="/mission"
            className="w-full sm:w-auto bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-center"
          >
            Learn more
          </Link>
          <Link
            href="/join"
            className="w-full sm:w-auto border border-white px-6 py-3 rounded-full font-semibold text-center"
          >
            Get involved
          </Link>
        </div>
      </motion.section>

      {/* Key Features Section */}
      <motion.section
        className="py-24 px-6 bg-gradient-to-b from-white to-blue-600 text-center"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <h2 className="text-4xl font-bold mb-12">Key Features</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {[
            "Incident Reporting",
            "Volunteer Coordination",
            "Secure & Transparent",
          ].map((title, i) => (
            <motion.div
              key={i}
              className="bg-blue-600 p-5 sm:p-6 rounded-lg shadow-lg cursor-pointer hover:scale-105 transition-transform"
              whileHover={{ scale: 1.05 }}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
            >
              <img src={featureIllustrations[i]} alt={title} className="w-20 sm:w-24 md:w-32 mx-auto mb-4" />
              <h3 className="text-2xl font-semibold mb-3 text-white">{title}</h3>
              <p className="text-white">
                {{
                  0: "Citizens can report incidents in real time using location-based tools, helping volunteers understand where help is needed.",
                  1: "Volunteers can receive notifications and respond efficiently, testing the system even in a demo environment.",
                  2: "Data is handled securely and the platform is designed for transparency, respecting privacy from day one."
                }[i]}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* How It Works Preview */}
      <motion.section
        className="py-24 px-6 text-center bg-blue-600"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <h2 className="text-4xl font-bold mb-12 text-white">How It Works</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 px-4 py-6 max-w-6xl mx-auto">
          {[
            { title: "1. Report", desc: "Citizens can create incident reports to indicate where help may be needed." },
            { title: "2. Notify", desc: "Volunteers can see nearby incidents and prepare to assist where possible." },
            { title: "3. Respond", desc: "Volunteers act according to availability; the platform demonstrates coordination potential." }
          ].map((step, i) => (
            <motion.div
              key={i}
              className="bg-blue-700 p-5 sm:p-6 rounded-lg shadow-lg"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
              whileHover={{ scale: 1.03 }}
            >
              <img src={stepIllustrations[i]} alt={step.title} className="w-20 sm:w-28 mx-auto mb-4" />
              <h3 className="text-xl sm:text-2xl font-semibold mb-3 text-white">{step.title}</h3>
              <p className="text-white">{step.desc}</p>
            </motion.div>
          ))}
        </div>
        <Link
          href="/how-it-works"
          className="mt-6 sm:mt-10 inline-block w-full sm:w-auto bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-center"
        >
          Learn More
        </Link>
      </motion.section>

      {/* Community / Future Vision */}
      <motion.section
        className="py-24 px-6 bg-white text-blue-600 text-center"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <h2 className="text-4xl font-bold mb-12 ">Community & Vision</h2>
        <p className="max-w-3xl mx-auto text-lg mb-8">
          OpenResQ is designed for citizens and volunteers to explore the potential
          of coordinated emergency response.
          <br />
          While we currently operate in a demo environment, the platform is
          structured to allow future partnerships and expansion.
        </p>
        <Link
          href="/community"
          className="inline-block w-full sm:w-auto bg-blue-600 text-gray-50 px-6 py-3 rounded-full font-semibold text-center"
        >
          Learn More
        </Link>
      </motion.section>

      {/* FAQ Section */}
      <motion.section
        className="py-24 px-6 text-center bg-blue-50 text-blue-600"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <h2 className="text-4xl font-bold mb-12">FAQ</h2>
        <div className="max-w-4xl mx-auto text-left">
          {faqData.map((item, i) => (
            <div key={i} className="mb-4">
              <button
                className="w-full text-left font-semibold text-lg focus:outline-none"
                onClick={() => setOpenFAQ(openFAQ === i ? null : i)}
              >
                {item.question}
              </button>
              {openFAQ === i && (
                <motion.p
                  className="mt-2 text-blue-800"
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  {item.answer}
                </motion.p>
              )}
            </div>
          ))}
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section
        className="py-24 px-6 text-center bg-blue-600"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
      >
        <h2 className="text-4xl font-bold mb-6 text-white">Join the Project</h2>
        <p className="max-w-2xl mx-auto mb-8 text-white">
          Contribute as a citizen, volunteer, or developer.
          Test the platform, give feedback, and help us shape a tool for safer communities.
        </p>
        <Link
          href="/join"
          className="inline-block w-full sm:w-auto bg-white text-blue-600 px-6 py-3 rounded-full font-semibold text-center"
        >
          Get Involved
        </Link>
      </motion.section>
    </main>
  );
}
