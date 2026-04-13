"use client";

import { useEffect, useState } from "react";
import { login, loginWithGoogle } from "../lib/auth";
import { auth } from "../lib/firebase";
import { onAuthStateChanged } from "firebase/auth";
import { motion } from "framer-motion";
import Link from "next/link";

export default function LoginPage() {
  const [loginMethod, setLoginMethod] = useState<"email" | "id">("email");
  const [email, setEmail] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [password, setPassword] = useState("");
  const [isNewId, setIsNewId] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  useEffect(() => {
    document.title = "Login - OpenResQ";
    const params = new URLSearchParams(window.location.search);
    if (params.get("error") === "not-authorized") {
      setError("Access denied. Admin privileges required.");
    }
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) window.location.href = "/";
    });
    return unsubscribe;
  }, []);

  async function handleIdCheck(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/billing/public/verify-customer-id`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customerId }),
      });

      const data = await response.json();
      if (response.ok) {
        setIsNewId(true);
        setEmail(data.adminEmail);
      } else {
        setError(data.detail || "Invalid Customer ID");
      }
    } catch (err) {
      setError("Failed to verify ID");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isNewId) {
        // Registration/Setup flow
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const setupRes = await fetch(`${backendUrl}/billing/public/setup-password`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ customerId, password }),
        });
        
        if (!setupRes.ok) {
          const data = await setupRes.json();
          throw new Error(data.detail || "Setup failed");
        }
      }

      // Final Login
      await login(email, password);
      window.location.href = "/";
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleLogin() {
    setError("");
    setGoogleLoading(true);

    try {
      await loginWithGoogle();
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      setError("Failed to sign in with Google");
    } finally {
      setGoogleLoading(false);
    }
  }

  return (
    <div className="h-screen w-full flex items-center justify-center relative overflow-hidden bg-black">

      {/* Gradient Glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#020617] via-[#0f172a] to-[#020617]" />

      {/* Animated blobs */}
      <motion.div
        className="absolute w-[500px] h-[500px] bg-primary/20 rounded-full blur-3xl top-[-100px] left-[-100px]"
        animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
        transition={{ repeat: Infinity, duration: 10 }}
      />

      <motion.div
        className="absolute w-[400px] h-[400px] bg-blue-500/20 rounded-full blur-3xl bottom-[-100px] right-[-100px]"
        animate={{ x: [0, -40, 0], y: [0, -20, 0] }}
        transition={{ repeat: Infinity, duration: 12 }}
      />

      {/* Card */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 w-[400px] p-8 rounded-3xl shadow-[0_0_40px_rgba(0,0,0,0.6)] border border-white/10 bg-white/5 backdrop-blur-2xl"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight">
            OpenResQ
          </h1>
          <p className="text-white/50 text-sm mt-1">
            {isNewId ? "Finish Account Setup" : "Admin Control Panel"}
          </p>
        </div>

        {/* Tab Switcher (only if not in setup mode) */}
        {!isNewId && (
          <div className="flex bg-white/5 p-1 rounded-xl mb-6 border border-white/5">
            <button
              onClick={() => setLoginMethod("email")}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${loginMethod === "email" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/60"}`}
            >
              Email
            </button>
            <button
              onClick={() => setLoginMethod("id")}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition ${loginMethod === "id" ? "bg-white/10 text-white" : "text-white/40 hover:text-white/60"}`}
            >
              Customer ID
            </button>
          </div>
        )}

        <form onSubmit={loginMethod === "id" && !email ? handleIdCheck : handleLogin}>
          {/* Inputs */}
          <div className="space-y-5">
            {loginMethod === "email" ? (
              <div>
                <label className="text-xs text-white/50">Email</label>
                <input
                  type="email"
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-white/10 text-white placeholder-white/40 border border-white/20 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-transparent transition"
                  placeholder="admin@openresq.io"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            ) : (
              <div>
                <label className="text-xs text-white/50">Customer ID</label>
                <input
                  type="text"
                  disabled={!!email}
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-white/10 text-white placeholder-zinc-500 border border-white/20 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-transparent transition font-mono uppercase"
                  placeholder="CUST-XXXXXXXX"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  required
                />
              </div>
            )}

            {(email || loginMethod === "email") && (
              <div>
                <label className="text-xs text-white/50">
                  {isNewId ? "Create Password" : "Password"}
                </label>
                <input
                  type="password"
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-white/10 text-white placeholder-white/40 border border-white/20 focus:outline-none focus:ring-2 focus:ring-primary/60 focus:border-transparent transition"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                {isNewId && (
                  <p className="text-[10px] text-zinc-500 mt-2">
                    Min. 8 characters. You'll use this for future logins.
                  </p>
                )}
              </div>
            )}

            {error && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-red-400 text-sm text-center"
              >
                {error}
              </motion.p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-primary text-white font-semibold hover:bg-primary/90 transition-all duration-200 shadow-lg shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Processing…" : (isNewId ? "Complete Setup" : (email || loginMethod === "email" ? "Login" : "Continue"))}
            </button>

            {isNewId && (
              <button
                type="button"
                onClick={() => { setIsNewId(false); setEmail(""); }}
                className="w-full text-zinc-500 hover:text-white text-xs transition"
              >
                Cancel and use different ID
              </button>
            )}

            {!isNewId && (
              <>
                {/* Divider */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-px bg-white/20" />
                  <span className="text-xs text-white/40">Or</span>
                  <div className="flex-1 h-px bg-white/20" />
                </div>

                {/* Google Sign-In Button */}
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={googleLoading}
                  className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold border border-white/20 transition-all duration-200 shadow-lg shadow-black/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="currentColor"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="currentColor"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  {googleLoading ? "Signing in…" : "Sign in with Google"}
                </button>
              </>
            )}
          </div>
        </form>

        {/* Footer */}
        <div className="mt-8">
          <p className="text-center text-white/30 text-xs text-zinc-500">
            © {new Date().getFullYear()} OpenResQ • Secure Access
          </p>
        </div>
      </motion.div>
    </div>
  );
}