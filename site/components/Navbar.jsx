"use client";

import Link from "next/link";
import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="w-full px-4 sm:px-8 py-3 sm:py-4 border-b bg-white">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <Link href="/" className="text-2xl font-bold text-blue-600">
          OpenResQ
        </Link>

        {/* Desktop links */}
        <div className="hidden sm:flex items-center gap-6 text-sm font-medium text-black">
          <Link href="/mission" className="hover:text-blue-600">Mission</Link>
          <Link href="/platform" className="hover:text-blue-600">Platform</Link>
          <Link href="/how-it-works" className="hover:text-blue-600">How it works</Link>
          <Link href="/community" className="hover:text-blue-600">Community</Link>
          <Link href="/contact" className="hover:text-blue-600">Contact Us</Link>
          <Link
            href="/join"
            className="text-white font-semibold bg-blue-600 rounded-full px-4 py-2 hover:bg-blue-700 transition-colors"
          >
            Join
          </Link>
        </div>

        {/* Mobile hamburger */}
        <div className="sm:hidden flex items-center">
          <button
            aria-label="Open menu"
            onClick={() => setOpen(true)}
            className="p-2 rounded-md hover:bg-gray-100"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 6H20" stroke="#1E3A8A" strokeWidth="2" strokeLinecap="round" />
              <path d="M4 12H20" stroke="#1E3A8A" strokeWidth="2" strokeLinecap="round" />
              <path d="M4 18H20" stroke="#1E3A8A" strokeWidth="2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile slide-in menu */}
      {open && (
        <div className="fixed inset-0 z-40">
          <div
            className="absolute inset-0 bg-black/40"
            onClick={() => setOpen(false)}
            aria-hidden
          />

          <aside className="absolute right-0 top-0 h-full w-72 bg-white p-6 shadow-lg overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <Link href="/" className="text-xl font-bold text-blue-600">OpenResQ</Link>
              <button aria-label="Close menu" onClick={() => setOpen(false)} className="p-2 rounded-md hover:bg-gray-100">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M6 6L18 18" stroke="#374151" strokeWidth="2" strokeLinecap="round" />
                  <path d="M6 18L18 6" stroke="#374151" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
            </div>

            <nav className="flex flex-col gap-4 text-base text-gray-900">
              <Link href="/mission" onClick={() => setOpen(false)} className="block py-2 hover:text-blue-600">Mission</Link>
              <Link href="/platform" onClick={() => setOpen(false)} className="block py-2 hover:text-blue-600">Platform</Link>
              <Link href="/how-it-works" onClick={() => setOpen(false)} className="block py-2 hover:text-blue-600">How it works</Link>
              <Link href="/community" onClick={() => setOpen(false)} className="block py-2 hover:text-blue-600">Community</Link>
              <Link href="/contact" onClick={() => setOpen(false)} className="block py-2 hover:text-blue-600">Contact Us</Link>
            </nav>

            <div className="mt-6">
              <Link href="/join" onClick={() => setOpen(false)} className="w-full block text-center bg-blue-600 text-white font-semibold px-4 py-2 rounded-md">
                Join
              </Link>
            </div>
          </aside>
        </div>
      )}
    </nav>
  );
}
