// app/layout.tsx
"use client";

import "./globals.css";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthWrapper>{children}</AuthWrapper>
      </body>
    </html>
  );
}


import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "./lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

function AuthWrapper({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const router = useRouter();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (u: User | null) => {
      setUser(u);
    });
    return unsubscribe;
  }, []);

  // Allow login page to render without auth
  if (typeof window !== 'undefined' && window.location.pathname === '/login') {
    return children;
  }

  if (user === undefined) {
    console.log("Auth loading…");
    return <div>Loading auth…</div>;
  }

  if (!user) {
    console.log("No user, redirecting to /login");
    if (window.location.pathname !== "/login") {
      router.push("/login");
    }
    return null;
  }

  console.log("User authenticated:", user);
  return children;
}
