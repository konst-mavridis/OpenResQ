"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { useState, useEffect } from "react";

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
    question: "Τι είναι το OpenResQ;",
    answer:
      "Το OpenResQ είναι μια σύγχρονη πλατφόρμα που συνδέει πολίτες και εθελοντές για πιο άμεση και αποτελεσματική ανταπόκριση σε περιστατικά έκτακτης ανάγκης."
  },
  {
    question: "Ποιος μπορεί να συμμετάσχει;",
    answer:
      "Οποιοσδήποτε ενδιαφέρεται να βοηθήσει ή να δοκιμάσει την πλατφόρμα — πολίτες, εθελοντές ή developers."
  },
  {
    question: "Πώς προστατεύονται τα δεδομένα μου;",
    answer:
      "Η πλατφόρμα εφαρμόζει πρακτικές ασφαλείας και αρχές ιδιωτικότητας, με σεβασμό στα ευρωπαϊκά πρότυπα."
  }
];

function useTypingLoop(text: string, speed = 120, pause = 1200) {
  const [displayed, setDisplayed] = useState("");
  const [index, setIndex] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    let timeout: any;

    if (!deleting && index < text.length) {
      timeout = setTimeout(() => {
        setDisplayed(text.slice(0, index + 1));
        setIndex(index + 1);
      }, speed);
    } else if (!deleting && index === text.length) {
      timeout = setTimeout(() => setDeleting(true), pause);
    } else if (deleting && index > 0) {
      timeout = setTimeout(() => {
        setDisplayed(text.slice(0, index - 1));
        setIndex(index - 1);
      }, speed / 1.5);
    } else if (deleting && index === 0) {
      setDeleting(false);
    }

    return () => clearTimeout(timeout);
  }, [index, deleting, text, speed, pause]);

  return displayed;
}

export default function Home() {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);
  const title = useTypingLoop("OpenResQ", 140, 1500);


  return (
    <main className="bg-white text-neutral-800">

      {/* HERO */}
      <motion.section
        className="min-h-[70vh] md:min-h-screen bg-primary text-white flex flex-col justify-center items-center text-center px-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <h1 className="text-gray-700 text-4xl md:text-6xl font-semibold tracking-tight mb-6">
          {title}
          <span className="text-primary animate-blink">|</span>
        </h1>
        <p className="text-gray-400 max-w-2xl text-lg md:text-xl font-light leading-relaxed mb-8 ">
          Μια πλατφόρμα που ενώνει πολίτες και εθελοντές για ταχύτερη,
          αποτελεσματικότερη και πιο έξυπνη ανταπόκριση σε περιστατικά
          έκτακτης ανάγκης.
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            href="/mission"
            className="bg-gray-300 text-primary px-8 py-3 rounded-lg font-semibold shadow-sm hover:bg-neutral-500 transition"
          >
            Μάθε περισσότερα
          </Link>
          <Link
            href="/join"
            className="border bg-gray-300 text-primary px-8 py-3 rounded-lg font-semibold hover:bg-neutral-500 hover:text-primary transition"
          >
            Συμμετοχή
          </Link>
        </div>
      </motion.section>

      {/* FEATURES */}
      <section className="py-24 px-6 bg-neutral-50">
        <h2 className="text-4xl font-semibold text-center mb-16 tracking-tight">
          Βασικές Δυνατότητες
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10 max-w-7xl mx-auto">
          {[
            "Αναφορά Περιστατικών",
            "Συντονισμός Εθελοντών",
            "Ασφάλεια & Διαφάνεια"
          ].map((title, i) => (
            <motion.div
              key={i}
              className="bg-white border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
            >
              <img
                src={featureIllustrations[i]}
                alt={title}
                className="w-24 mx-auto mb-6 opacity-90"
              />
              <h3 className="text-2xl font-semibold text-center mb-4">
                {title}
              </h3>
              <p className="text-center text-neutral-600 leading-relaxed">
                {{
                  0: "Οι πολίτες μπορούν να αναφέρουν περιστατικά σε πραγματικό χρόνο, βοηθώντας στον άμεσο εντοπισμό αναγκών.",
                  1: "Οι εθελοντές ενημερώνονται άμεσα και ανταποκρίνονται αποτελεσματικά, ενισχύοντας τον συντονισμό.",
                  2: "Η πλατφόρμα εφαρμόζει πρακτικές ασφαλείας και διαφάνειας, με σεβασμό στην ιδιωτικότητα."
                }[i]}
              </p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="py-24 px-6 bg-white">
        <h2 className="text-4xl font-semibold text-center mb-16 tracking-tight">
          Πώς Λειτουργεί
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-10 max-w-7xl mx-auto">
          {[
            { title: "1. Αναφορά", desc: "Οι πολίτες δημιουργούν αναφορές περιστατικών." },
            { title: "2. Ειδοποίηση", desc: "Οι εθελοντές ενημερώνονται άμεσα." },
            { title: "3. Ανταπόκριση", desc: "Οι εθελοντές συνδράμουν όπου χρειάζεται." }
          ].map((step, i) => (
            <motion.div
              key={i}
              className="bg-neutral-50 border border-neutral-200 p-8 rounded-xl shadow-sm hover:shadow-md transition"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.2 }}
            >
              <img
                src={stepIllustrations[i]}
                alt={step.title}
                className="w-24 mx-auto mb-6"
              />
              <h3 className="text-xl font-semibold text-center mb-3">
                {step.title}
              </h3>
              <p className="text-center text-neutral-600">
                {step.desc}
              </p>
            </motion.div>
          ))}
        </div>

        <div className="text-center mt-12">
          <Link
            href="/how-it-works"
            className="inline-block bg-primary bg-gray-300 text-white px-8 py-3 rounded-lg font-semibold shadow-sm hover:bg-primary-700 transition"
          >
            Αναλυτικά
          </Link>
        </div>
      </section>

      {/* COMMUNITY */}
      <section className="py-24 px-6 bg-neutral-50 text-center">
        <h2 className="text-4xl font-semibold mb-10 tracking-tight">
          Κοινότητα & Όραμα
        </h2>
        <p className="max-w-3xl mx-auto text-lg text-neutral-700 leading-relaxed mb-10">
          Το OpenResQ αναδεικνύει τη δύναμη της συνεργασίας μεταξύ πολιτών και
          εθελοντών. Η πλατφόρμα έχει σχεδιαστεί με προοπτική εξέλιξης και
          μελλοντικών συνεργασιών.
        </p>

        <Link
          href="/community"
          className="inline-block bg-gray-300 text-white px-8 py-3 rounded-lg font-semibold shadow-sm hover:bg-primary-700 transition"
        >
          Μάθε περισσότερα
        </Link>
      </section>

      {/* FAQ */}
      <section className="py-24 px-6 bg-white">
        <h2 className="text-4xl font-semibold text-center mb-16 tracking-tight">
          Συχνές Ερωτήσεις
        </h2>

        <div className="max-w-3xl mx-auto">
          {faqData.map((item, i) => (
            <div key={i} className="mb-6 border-b border-neutral-200 pb-4">
              <button
                className="w-full text-left text-xl font-semibold"
                onClick={() => setOpenFAQ(openFAQ === i ? null : i)}
              >
                {item.question}
              </button>

              {openFAQ === i && (
                <motion.p
                  className="mt-3 text-neutral-600 leading-relaxed"
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
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-primary text-center text-neutral-500 dark:text-neutral-400">
        <h2 className="text-4xl font-semibold mb-6 tracking-tight  ">
          Γίνε Μέρος της Προσπάθειας
        </h2>
        <p className="max-w-2xl mx-auto text-lg font-light leading-relaxed mb-10 ">
          Συμμετέχετε ως πολίτης, εθελοντής ή developer και συμβάλετε στη
          διαμόρφωση ενός εργαλείου που στοχεύει σε πιο ασφαλείς κοινότητες.
        </p>

        <Link
          href="/join"
          className="inline-block bg-gray-300 text-white text-primary px-8 py-3 rounded-lg font-semibold shadow-sm hover:bg-neutral-100 transition"
        >
          Συμμετοχή
        </Link>
      </section>
    </main>
  );
}
