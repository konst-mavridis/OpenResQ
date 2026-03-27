"use client";

import { motion } from "framer-motion";

export default function CaseStudies() {
  return (
    <main className="bg-white min-h-screen py-24 px-6 text-black">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <motion.div
          className="text-center sm:text-left mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight text-black">
            Case Studies
          </h1>
          <p className="text-lg text-black/70 mt-4 max-w-2xl leading-relaxed">
            Examples of how OpenResQ enhances emergency response, coordination
            and community resilience across different environments.
          </p>
          <div className="w-24 h-1 bg-primary rounded mt-4 mx-auto sm:mx-0"></div>
        </motion.div>

        {/* Case Study 1 */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-black">
            Urban Flood Response Coordination
          </h2>
          <p className="text-black/70 leading-relaxed text-lg">
            During a sudden flash‑flood event, OpenResQ enabled a municipality to
            receive over 120 citizen reports within minutes. Real‑time mapping of
            flooded streets, trapped individuals and blocked routes allowed emergency
            teams to prioritize interventions and deploy resources efficiently.
          </p>
          <p className="text-black/70 leading-relaxed text-lg mt-4">
            As a result, response teams reduced dispatch delays by 35% and improved
            communication between municipal services, volunteers and civil protection units.
          </p>
        </motion.div>

        {/* Case Study 2 */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-black">
            Coordinated Search & Rescue in Mountain Region
          </h2>
          <p className="text-black/70 leading-relaxed text-lg">
            A volunteer rescue group used OpenResQ to coordinate a multi‑team search
            operation for a missing hiker. Citizen sightings, GPS‑tagged updates and
            shared location markers helped responders cover more ground in less time.
          </p>
          <p className="text-black/70 leading-relaxed text-lg mt-4">
            The platform’s shared dashboard allowed all teams — volunteers, local
            authorities and emergency services — to maintain a unified operational
            picture, ultimately leading to a successful rescue within the same day.
          </p>
        </motion.div>

        {/* Case Study 3 */}
        <motion.div
          className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition mb-12"
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <h2 className="text-2xl font-semibold mb-4 text-black">
            Fire Risk Monitoring with Community Input
          </h2>
          <p className="text-black/70 leading-relaxed text-lg">
            In a rural region with high wildfire risk, OpenResQ was used to collect
            early‑warning reports from residents. Suspicious smoke sightings, dry
            vegetation hotspots and small fires were reported instantly through the app.
          </p>
          <p className="text-black/70 leading-relaxed text-lg mt-4">
            Combined with responder feedback and on‑site verification, the municipality
            managed to contain multiple incidents before they escalated, demonstrating
            the value of community‑driven prevention.
          </p>
        </motion.div>

      </div>
    </main>
  );
}
