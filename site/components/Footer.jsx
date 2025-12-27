"use client";

import Link from "next/link";
import { useState } from "react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState(null); // null | 'loading' | 'success' | 'error'
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
        setMessage(data.error || data.message || "Subscription failed");
        return;
      }

      setStatus("success");
      setMessage(data.message || "Subscribed successfully");
      setEmail("");
    } catch (err) {
      setStatus("error");
      setMessage("Something went wrong. Please try again.");
    }
  }

  return (
    <footer className="bg-white text-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-12 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">

        {/* Brand */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            OpenResQ
          </h2>
          <p className="text-sm text-gray-600">
            An open, community-driven platform improving emergency
            response through collaboration and transparency.
          </p>
        </div>

        {/* Site Links */}
        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-4 uppercase">
            Platform
          </h3>
          <ul className="space-y-2 text-sm">
            <li><Link href="/mission" className="hover:text-gray-900">Mission</Link></li>
            <li><Link href="/platform" className="hover:text-gray-900">Platform</Link></li>
            <li><Link href="/how-it-works" className="hover:text-gray-900">How it works</Link></li>
            <li><Link href="/community" className="hover:text-gray-900">Community</Link></li>
            <li><Link href="/join" className="hover:text-gray-900">Get involved</Link></li>
          </ul>
        </div>

        {/* Community / Social */}
        <div>
          <h3 className="text-sm font-semibold text-gray-900 mb-4 uppercase">
            Community
          </h3>
          <ul className="space-y-2 text-sm">
            <li>
              <a href="https://github.com/" target="_blank" className="hover:text-blue-600">
                GitHub
              </a>
            </li>
            <li>
              <a href="https://twitter.com/" target="_blank" className="hover:text-blue-600">
                X (Twitter)
              </a>
            </li>
            <li>
              <a href="https://linkedin.com/" target="_blank" className="hover:text-blue-600">
                LinkedIn
              </a>
            </li>
            <li>
              <a href="mailto:contact@openresq.org" className="hover:text-blue-600">
                Contact
              </a>
            </li>
          </ul>
        </div>

        {/* Newsletter */}
        <div>
          <h3 className="text-sm font-semibold text-white mb-4 uppercase">
            Newsletter
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Stay informed about updates, partnerships and releases.
          </p>

          <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
            <label htmlFor="newsletter-email" className="sr-only">Email address</label>
            <input
              id="newsletter-email"
              name="email"
              type="email"
              placeholder="Your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 rounded bg-white border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <div className="flex items-center gap-3">
              <button
                type="submit"
                disabled={status === "loading"}
                className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded transition disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {status === "loading" ? "Subscribing..." : "Subscribe"}
              </button>
              {status === "success" && (
                <p className="text-sm text-green-600">{message}</p>
              )}
              {status === "error" && (
                <p className="text-sm text-red-600">{message}</p>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-gray-200 py-6 text-center text-sm text-gray-500">
        © {new Date().getFullYear()} OpenResQ. All rights reserved. ·
        <Link href="/privacy" className="ml-2 hover:text-blue-600">Privacy</Link> ·
        <Link href="/terms" className="ml-2 hover:text-blue-600">Terms</Link>
      </div>
    </footer>
  );
}
