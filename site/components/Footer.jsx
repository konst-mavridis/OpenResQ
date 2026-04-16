"use client";

import Link from "next/link";
import { useState } from "react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const res = await fetch("/api/newsletter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (!res.ok) {
        setStatus("error");
        setMessage(data.error || "Subscription failed");
        return;
      }

      setStatus("success");
      setMessage(data.message || "Subscribed successfully");
      setEmail("");
    } catch {
      setStatus("error");
      setMessage("Something went wrong. Please try again.");
    }
  }

  return (
    <footer className="bg-neutral-50 dark:bg-neutral-900 text-neutral-800 dark:text-neutral-200 border-t border-neutral-200 dark:border-neutral-800">
      <div className="max-w-7xl mx-auto px-6 py-16 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12">

        {/* Brand */}
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-primary dark:text-primary-300">
            OpenResQ
          </h2>
          <p className="mt-3 text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
            A modern, community‑driven platform enhancing emergency response
            through collaboration, transparency and innovation.
          </p>
        </div>

        {/* Platform Links */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500 dark:text-neutral-400 mb-4">
            Platform
          </h3>
          <ul className="space-y-2 text-sm">
            <li><Link href="/mission" className="hover:text-primary">Mission</Link></li>
            <li><Link href="/platform" className="hover:text-primary">Platform</Link></li>
            <li><Link href="/how-it-works" className="hover:text-primary">How it works</Link></li>
            <li><Link href="/community" className="hover:text-primary">Community</Link></li>
            <li><Link href="/join" className="hover:text-primary">Get involved</Link></li>
          </ul>
        </div>

        {/* Community */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500 dark:text-neutral-400 mb-4">
            Community
          </h3>
          <ul className="space-y-2 text-sm">
            <li><a href="https://github.com" target="_blank" className="hover:text-primary">GitHub</a></li>
            <li><a href="https://twitter.com" target="_blank" className="hover:text-primary">X (Twitter)</a></li>
            <li><a href="https://linkedin.com" target="_blank" className="hover:text-primary">LinkedIn</a></li>
            <li><a href="mailto:openresq.info@gmail.com" className="hover:text-primary">Contact</a></li>
          </ul>
        </div>

        {/* Newsletter */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-neutral-500 dark:text-neutral-400 mb-4">
            Newsletter
          </h3>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">
            Stay informed about updates, releases and partnerships.
          </p>

          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <input
              type="email"
              placeholder="Your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 rounded-lg bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-700 text-sm focus:ring-2 focus:ring-primary focus:outline-none"
            />

            <button
              type="submit"
              disabled={status === "loading"}
              className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-primary-700 transition disabled:opacity-60"
            >
              {status === "loading" ? "Subscribing..." : "Subscribe"}
            </button>

            {status === "success" && (
              <p className="text-sm text-green-600 dark:text-green-400">{message}</p>
            )}
            {status === "error" && (
              <p className="text-sm text-red-600 dark:text-red-400">{message}</p>
            )}
          </form>
        </div>
      </div>

      <div className="border-t border-neutral-200 dark:border-neutral-800 py-6 text-center text-sm text-neutral-500 dark:text-neutral-400 font-medium">
        © {new Date().getFullYear()} OpenResQ • Empowering First Responders
        <div className="mt-2 flex items-center justify-center gap-4">
          <Link href="/privacy" className="hover:text-primary transition">Privacy Policy</Link>
          <span className="text-neutral-300 dark:text-neutral-700">•</span>
          <Link href="/terms" className="hover:text-primary transition">Terms of Service</Link>
          <span className="text-neutral-300 dark:text-neutral-700">•</span>
          <Link href="/cookies" className="hover:text-primary transition">Cookie Policy</Link>
        </div>
      </div>
    </footer>
  );
}
