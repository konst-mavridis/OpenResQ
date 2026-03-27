"use client";

import { useEffect, useState } from "react";
import { login } from "../lib/auth";
import { auth } from "../lib/firebase";
import { onAuthStateChanged } from "firebase/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        window.location.href = "/";
      }
    });
    return unsubscribe;
  }, []);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      window.location.href = "/";
    } catch (err: unknown) {
      console.error(err);
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="h-screen flex items-center justify-center bg-neutral-100">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-xl border border-border w-80 shadow-sm"
      >
        <h1 className="text-xl font-semibold mb-4 text-center">Admin Login</h1>

        <input
          type="email"
          className="w-full border border-border rounded-lg px-3 py-2 mb-3"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          className="w-full border border-border rounded-lg px-3 py-2 mb-4"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && (
          <p className="text-red-600 text-sm mb-3 text-center">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-white py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? "Logging in…" : "Login"}
        </button>
      </form>
    </div>
  );
}
