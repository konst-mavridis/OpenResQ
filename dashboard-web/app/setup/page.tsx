"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import PublicLegalFooter from "../components/legal/PublicLegalFooter";

interface OrganizationData {
  orgName?: string;
  adminEmail?: string;
}

export default function SetupPage() {
  const [step, setStep] = useState(1); // 1: ID, 2: Password
  const [customerId, setCustomerId] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [orgData, setOrgData] = useState<OrganizationData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  async function verifyId(e: React.FormEvent) {
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
        setOrgData(data);
        setStep(2);
      } else {
        setError(data.detail || "Invalid Customer ID");
      }
    } catch {
      setError("Failed to verify Customer ID. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSetup(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/billing/public/setup-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ customerId, password }),
      });

      const data = await response.json();
      if (response.ok) {
        setSuccess(true);
      } else {
        setError(data.detail || "Failed to setup account");
      }
    } catch {
      setError("An error occurred during setup. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="min-h-screen w-full flex flex-col bg-black text-white">
        <div className="flex flex-1 items-center justify-center px-6 py-10">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-md w-full p-8 rounded-3xl bg-zinc-900 border border-zinc-800 text-center"
          >
            <div className="w-16 h-16 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6 text-3xl">
              ✓
            </div>
            <h1 className="text-2xl font-bold mb-4">Setup Complete!</h1>
            <p className="text-zinc-400 mb-8">
              Your organization account has been created. You can now login with your email and the password you just set.
            </p>
            <Link 
              href="/login"
              className="block w-full py-4 rounded-xl bg-primary text-white font-bold bg-blue-600 hover:bg-blue-500 transition shadow-lg shadow-blue-900/20"
            >
              Go to Login
            </Link>
          </motion.div>
        </div>
        <div className="w-full border-t border-white/10 px-4 py-4 text-center text-xs text-zinc-500">
          <PublicLegalFooter />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full flex flex-col relative overflow-hidden bg-black text-white">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#020617] via-[#0f172a] to-[#020617]" />
      <div className="relative z-10 flex flex-1 items-center justify-center px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-[450px] max-w-full p-8 rounded-3xl shadow-2xl border border-white/10 bg-white/5 backdrop-blur-2xl"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Setup OpenResQ</h1>
            <p className="text-zinc-400 text-sm mt-2">
              Initialize your organization&apos;s environment
            </p>
          </div>

        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.form
              key="step1"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={verifyId}
              className="space-y-6"
            >
              <div>
                <label className="text-xs text-zinc-500 block mb-2 font-medium">CUSTOMER ID</label>
                <input
                  type="text"
                  required
                  placeholder="CUST-XXXXXXXXXXXX"
                  className="w-full px-4 py-4 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500 transition font-mono uppercase"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                />
                <p className="text-[10px] text-zinc-500 mt-2">
                  Found in your welcome email
                </p>
              </div>

              {error && <p className="text-red-400 text-sm text-center">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition shadow-lg shadow-blue-900/20 disabled:opacity-50"
              >
                {loading ? "Verifying..." : "Continue"}
              </button>

              <div className="text-center mt-4">
                <Link href="/login" className="text-sm text-zinc-500 hover:text-white transition">
                  Back to Login
                </Link>
              </div>
            </motion.form>
          ) : (
            <motion.form
              key="step2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              onSubmit={handleSetup}
              className="space-y-6"
            >
              <div className="bg-white/5 p-4 rounded-xl border border-white/10 mb-6">
                <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Organization</p>
                <p className="font-bold text-lg">{orgData?.orgName}</p>
                <p className="text-sm text-zinc-400 mt-1">{orgData?.adminEmail}</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-xs text-zinc-500 block mb-2 font-medium">CREATE PASSWORD</label>
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    className="w-full px-4 py-4 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-500 block mb-2 font-medium">CONFIRM PASSWORD</label>
                  <input
                    type="password"
                    required
                    placeholder="••••••••"
                    className="w-full px-4 py-4 rounded-xl bg-white/10 border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </div>
              </div>

              {error && <p className="text-red-400 text-sm text-center">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition shadow-lg shadow-blue-900/20 disabled:opacity-50"
              >
                {loading ? "Setting up..." : "Complete Setup"}
              </button>

              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-zinc-500 hover:text-white text-sm transition"
              >
                Use different ID
              </button>
            </motion.form>
          )}
          </AnimatePresence>
        </motion.div>
      </div>
      <div className="relative z-10 mt-auto w-full border-t border-white/10 px-4 py-4 text-center text-xs text-zinc-500">
        <PublicLegalFooter />
      </div>
    </div>
  );
}
