// app/layout.tsx
"use client";

import "./globals.css";
import type { ReactNode } from "react";
import { ThemeProvider } from "./lib/ThemeContext";
import { getThemeScript } from "./lib/theme-script";
import CookieBanner from "./components/legal/CookieBanner";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{ __html: getThemeScript() }}
          suppressHydrationWarning
        />
      </head>
      <body>
        <ThemeProvider>
          <CookieBanner />
          <AuthWrapper>{children}</AuthWrapper>
        </ThemeProvider>
      </body>
    </html>
  );
}


import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { auth, db } from "./lib/firebase";
import { onAuthStateChanged, User, signOut } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";

type AccessRole = "admin" | "superadmin";

function AuthWrapper({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [role, setRole] = useState<AccessRole | null | undefined>(undefined);
  const [loadingTimeout, setLoadingTimeout] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const isPublicPath =
    pathname === "/login" ||
    pathname === "/privacy" ||
    pathname === "/terms" ||
    pathname === "/cookies";
  const isSuperadminPath = pathname.startsWith("/superadmin");

  useEffect(() => {
    // Set a timeout to prevent indefinite loading
    const timeout = setTimeout(() => {
      if (user === undefined || role === undefined) {
        setLoadingTimeout(true);
      }
    }, 5000); // 5 seconds timeout

    const unsubscribe = onAuthStateChanged(auth, async (u: User | null) => {
      clearTimeout(timeout);
      setUser(u);
      if (u) {
        // Fetch role from Firestore
        try {
          const userDoc = await getDoc(doc(db, "users", u.uid));
          const userRole = userDoc.data()?.role;
          if (userDoc.exists() && (userRole === "admin" || userRole === "superadmin")) {
            setRole(userRole);
          } else {
            console.warn("User is not an admin or superadmin");
            setRole(null);
          }
        } catch (error) {
          console.error("Error fetching user role:", error);
          setRole(null);
        }
      } else {
        setRole(undefined);
      }
    });
    return () => {
      clearTimeout(timeout);
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (user === undefined || role === undefined) {
      if (loadingTimeout) {
        // Timeout reached, assume no user
        setUser(null);
        setRole(undefined);
      }
      return;
    }

    if (user === null) {
      if (!isPublicPath) {
        console.log("No user, redirecting to /login");
        router.replace("/login");
      }
      return;
    }

    if (role === null) {
      console.log("User is not authorized, logging out");
      signOut(auth);
      router.replace("/login?error=not-authorized");
      return;
    }

    if (role === "superadmin") {
      if (pathname === "/" || pathname === "/login") {
        router.replace("/superadmin/organizations");
      }
      return;
    }

    if (isSuperadminPath) {
      router.replace("/");
    }
  }, [isPublicPath, isSuperadminPath, pathname, role, router, user, loadingTimeout]);

  // Allow login page to render without auth
  if (isPublicPath) {
    return children;
  }

  // Loading state (auth still checking or role still being fetched)
  if ((user === undefined || role === undefined) && !loadingTimeout) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-black text-white">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-white/60 animate-pulse">Verifying access…</p>
        </div>
      </div>
    );
  }

  // Final check: if not logged in or not authorized, don't render children
  if (!user || !role) {
    return null;
  }

  return <>{children}</>;
}
