"use client";

import Link from "next/link";

export default function PublicLegalFooter() {
  return (
    <div className="mt-6 space-y-4 text-center">
      <p className="text-xs text-foreground/40 font-medium tracking-wide">
        © {new Date().getFullYear()} OpenResQ • Empowering First Responders
      </p>
      <nav
        aria-label="Legal"
        className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-semibold text-foreground/60"
      >
        <Link 
          href="/privacy" 
          className="transition hover:text-primary hover:underline underline-offset-4 decoration-primary/30"
        >
          Privacy Policy
        </Link>
        <Link 
          href="/terms" 
          className="transition hover:text-primary hover:underline underline-offset-4 decoration-primary/30"
        >
          Terms of Service
        </Link>
        <Link 
          href="/cookies" 
          className="transition hover:text-primary hover:underline underline-offset-4 decoration-primary/30"
        >
          Cookie Policy
        </Link>
      </nav>
    </div>
  );
}
