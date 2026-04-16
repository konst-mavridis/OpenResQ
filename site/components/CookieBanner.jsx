"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const COOKIE_BANNER_KEY = "openresq_cookie_notice_dismissed";

export default function CookieBanner() {
  const [isDismissed, setIsDismissed] = useState(true);

  useEffect(() => {
    const dismissed = localStorage.getItem(COOKIE_BANNER_KEY) === "true";
    setIsDismissed(dismissed);
  }, []);

  const dismissBanner = () => {
    localStorage.setItem(COOKIE_BANNER_KEY, "true");
    setIsDismissed(true);
  };

  if (isDismissed) {
    return null;
  }

  return (
    <div className="fixed inset-x-0 bottom-4 z-50 mx-auto max-w-4xl px-4 animate-in fade-in slide-in-from-bottom-5 duration-500">
      <div className="flex flex-col items-center gap-6 rounded-3xl border border-neutral-200 bg-white/95 p-6 shadow-2xl backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-900/95 md:flex-row md:justify-between md:p-8">
        <div className="flex-1 space-y-2 text-center md:text-left">
          <h3 className="text-lg font-bold tracking-tight text-neutral-900 dark:text-neutral-50 font-serif">
            Cookies & Privacy Notice
          </h3>
          <p className="text-sm leading-relaxed text-neutral-600 dark:text-neutral-400">
            OpenResQ uses essential technologies to maintain your theme, keep you signed in, 
            and handle secure billing. We do not use optional tracking or advertising cookies.
          </p>
        </div>
        <div className="flex w-full flex-col items-center gap-4 md:w-auto md:flex-row">
          <div className="flex items-center gap-6 text-sm font-semibold">
            <Link
              href="/cookies"
              className="text-neutral-500 transition hover:text-primary dark:text-neutral-400 dark:hover:text-primary-400"
            >
              Cookies
            </Link>
            <Link
              href="/privacy"
              className="text-neutral-500 transition hover:text-primary dark:text-neutral-400 dark:hover:text-primary-400"
            >
              Privacy
            </Link>
          </div>
          <button
            type="button"
            onClick={dismissBanner}
            className="w-full rounded-2xl bg-neutral-900 px-8 py-3 text-sm font-bold uppercase tracking-wider text-white transition hover:bg-neutral-800 active:scale-95 dark:bg-white dark:text-black dark:hover:bg-neutral-100 md:w-auto"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
