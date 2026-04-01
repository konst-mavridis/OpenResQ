// app/layout.tsx
"use client";

import "./globals.css";
import type { ReactNode } from "react";
import { ThemeProvider } from "./lib/ThemeContext";
import { getThemeScript } from "./lib/theme-script";

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

function AuthWrapper({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [isAdmin, setIsAdmin] = useState<boolean | null>(null); // null = checking role
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (u: User | null) => {
      setUser(u);
      if (u) {
        // Fetch role from Firestore
        try {
          const userDoc = await getDoc(doc(db, "users", u.uid));
          if (userDoc.exists() && userDoc.data().role === "admin") {
            setIsAdmin(true);
          } else {
            console.warn("User is not an admin");
            setIsAdmin(false);
          }
        } catch (error) {
          console.error("Error fetching user role:", error);
          setIsAdmin(false);
        }
      } else {
        setIsAdmin(null);
      }
    });
    return unsubscribe;
  }, []);

  useEffect(() => {
    if (user === null && pathname !== "/login") {
      console.log("No user, redirecting to /login");
      router.push("/login");
    } else if (user && isAdmin === false && pathname !== "/login") {
      // User is logged in but not an admin
      console.log("User is not admin, logging out");
      signOut(auth);
      router.push("/login?error=not-authorized");
    }
  }, [user, isAdmin, pathname, router]);

  // Allow login page to render without auth
  if (pathname === "/login") {
    return children;
  }

  // Loading state (auth still checking or role still being fetched)
  if (user === undefined || (user && isAdmin === null)) {
    return (
      <div className="h-screen w-full flex items-center justify-center bg-black text-white">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-white/60 animate-pulse">Verifying access…</p>
        </div>
      </div>
    );
  }

  // Final check: if not logged in or not admin, don't render children
  if (!user || !isAdmin) {
    return null;
  }

  return <>{children}</>;
}
