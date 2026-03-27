"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="w-full bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">

        {/* Logo */}
        <Link href="/" className="text-2xl font-semibold tracking-tight text-primary dark:text-primary-300">
          OpenResQ
        </Link>

        {/* Desktop */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link href="/mission" className="hover:text-primary">Mission</Link>
          <Link href="/platform" className="hover:text-primary">Platform</Link>
          <Link href="/how-it-works" className="hover:text-primary">How it works</Link>
          <Link href="/community" className="hover:text-primary">Community</Link>
          <Link href="/contact" className="hover:text-primary">Contact</Link>
          <Link href="/partnerships" className="hover:text-primary">Partnerships</Link>
          <Link href="/pricing" className="hover:text-primary">Pricing</Link>
          <Link
            href="/join"
            className="bg-primary text-white px-5 py-2 rounded-lg font-semibold hover:bg-primary-700 transition"
          >
            Join
          </Link>
        </div>

        {/* Mobile button */}
        <button
          onClick={() => setOpen(true)}
          className="md:hidden p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
        >
          <svg width="24" height="24" stroke="currentColor" className="text-primary dark:text-primary-300">
            <path d="M4 6H20" strokeWidth="2" strokeLinecap="round" />
            <path d="M4 12H20" strokeWidth="2" strokeLinecap="round" />
            <path d="M4 18H20" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="fixed inset-0 z-40">
          <div className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />

          <aside className="absolute right-0 top-0 h-full w-72 bg-white dark:bg-neutral-900 shadow-xl p-6">
            <div className="flex items-center justify-between mb-8">
              <Link href="/" className="text-xl font-semibold text-primary dark:text-primary-300">
                OpenResQ
              </Link>

              <button
                onClick={() => setOpen(false)}
                className="p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800"
              >
                <svg width="24" height="24" stroke="currentColor">
                  <path d="M6 6L18 18" strokeWidth="2" strokeLinecap="round" />
                  <path d="M6 18L18 6" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
            </div>

            <nav className="flex flex-col gap-4 text-base">
              <Link href="/mission" onClick={() => setOpen(false)} className="hover:text-primary">Mission</Link>
              <Link href="/platform" onClick={() => setOpen(false)} className="hover:text-primary">Platform</Link>
              <Link href="/how-it-works" onClick={() => setOpen(false)} className="hover:text-primary">How it works</Link>
              <Link href="/community" onClick={() => setOpen(false)} className="hover:text-primary">Community</Link>
              <Link href="/contact" onClick={() => setOpen(false)} className="hover:text-primary">Contact</Link>
              <Link href="/partnerships" onClick={() => setOpen(false)} className="hover:text-primary">Partnerships</Link>
              <Link href="/pricing" onClick={() => setOpen(false)} className="hover:text-primary">Pricing</Link>
            </nav>

            <Link
              href="/join"
              onClick={() => setOpen(false)}
              className="mt-6 block text-center bg-primary text-white px-4 py-2 rounded-lg font-semibold hover:bg-primary-700 transition"
            >
              Join
            </Link>
          </aside>
        </div>
      )}
    </nav>
  );
}
