"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";

const COOKIE_BANNER_KEY = "openresq_cookie_notice_dismissed";

export default function CookieBanner() {
  const isDismissed = useSyncExternalStore(
    (onStoreChange) => {
      if (typeof window === "undefined") return () => {};
      window.addEventListener("storage", onStoreChange);
      window.addEventListener("openresq-cookie-banner", onStoreChange);

      return () => {
        window.removeEventListener("storage", onStoreChange);
        window.removeEventListener("openresq-cookie-banner", onStoreChange);
      };
    },
    () => {
      if (typeof window === "undefined") return false;
      return window.localStorage.getItem(COOKIE_BANNER_KEY) === "true";
    },
    () => false
  );

  const dismissBanner = () => {
    localStorage.setItem(COOKIE_BANNER_KEY, "true");
    window.dispatchEvent(new Event("openresq-cookie-banner"));
  };

  if (isDismissed) {
    return null;
  }

  return (
    <div className="fixed inset-x-0 bottom-4 z-[9999] mx-auto max-w-4xl px-4">
      <div className="flex flex-col items-center gap-6 rounded-[2rem] border border-white/20 bg-black/80 p-6 shadow-2xl backdrop-blur-2xl dark:bg-neutral-900/90 md:flex-row md:justify-between md:p-8">
        <div className="flex-1 space-y-2 text-center md:text-left">
          <h3 className="text-lg font-bold tracking-tight text-white">
            Cookies & Privacy Notice
          </h3>
          <p className="text-sm leading-relaxed text-white/70">
            OpenResQ uses essential technologies to keep you signed in, maintain your theme preferences, 
            and process secure billing. We do not use optional tracking or advertising cookies.
          </p>
        </div>
        <div className="flex w-full flex-col items-center gap-4 md:w-auto md:flex-row">
          <div className="flex items-center gap-4 text-sm font-semibold">
            <Link
              href="/cookies"
              className="text-white/60 transition hover:text-white"
            >
              Learn more
            </Link>
            <Link
              href="/privacy"
              className="text-white/60 transition hover:text-white"
            >
              Privacy
            </Link>
          </div>
          <button
            type="button"
            onClick={dismissBanner}
            className="w-full rounded-2xl bg-white px-8 py-3 text-sm font-bold uppercase tracking-wider text-black transition hover:bg-white/90 active:scale-95 md:w-auto"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  );
}
