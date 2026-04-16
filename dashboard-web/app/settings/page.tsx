"use client";

import { useState, useEffect } from "react";
import { auth } from "../lib/firebase";
import { apiPost, apiDelete } from "../lib/api";
import { useTheme } from "../lib/ThemeContext";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import PublicLegalFooter from "../components/legal/PublicLegalFooter";

export default function SettingsPage() {
  const { theme, setTheme, actualTheme } = useTheme();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    document.title = "Settings - OpenResQ";
  }, []);

  useEffect(() => {
    if (auth.currentUser) {
      setEmail(auth.currentUser.email || "");
    }
  }, []);

  const handleThemeChange = async (newTheme: string) => {
    setTheme(newTheme as "light" | "dark" | "system");

    try {
      const token = await auth.currentUser?.getIdToken();
      // Send actual theme (not "system") to backend
      const backendTheme =
        newTheme === "system"
          ? actualTheme
          : newTheme;
      await apiPost("/user/theme", { theme: backendTheme }, token);
    } catch (error) {
      console.error("Error saving theme:", error);
    }
  };

  const handleSaveAccount = async () => {
    if (email !== auth.currentUser?.email) {
      alert("Email updates are not supported by the backend yet.");
      return;
    }

    if (!password) {
      return;
    }

    setLoading(true);
    try {
      const token = await auth.currentUser?.getIdToken();
      await apiPost("/user/change-password", { new_password: password }, token);

      alert("Password updated successfully");
      setPassword("");
    } catch (error) {
      console.error("Error updating account:", error);
      alert("Error updating account");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
      return;
    }

    setLoading(true);
    try {
      const token = await auth.currentUser?.getIdToken();
      await apiDelete("/user/delete", token);
      alert("Account deleted successfully");
      // Redirect to login or home
      window.location.href = "/login";
    } catch (error) {
      console.error("Error deleting account:", error);
      alert("Error deleting account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="flex-1 p-8 space-y-8">
          <h1 className="text-2xl font-semibold">Settings</h1>

          <section className="bg-(--background) border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg text-foreground">Theme</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-4">
                <select
                  className="border border-border rounded-lg px-3 py-2 bg-(--background) text-foreground"
                  value={theme}
                  onChange={(e) => handleThemeChange(e.target.value)}
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="system">System</option>
                </select>
              </div>
            </div>
          </section>

          <section className="bg-(--background) border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg text-foreground">Account</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-4">
                <label className="w-24 text-foreground/70">Email</label>
                <input
                  type="email"
                  className="border border-border rounded-lg px-3 py-2 flex-1 bg-(--background) text-foreground"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="flex items-center space-x-4">
                <label className="w-24 text-foreground/70">Password</label>
                <input
                  type="password"
                  className="border border-border rounded-lg px-3 py-2 flex-1 bg-(--background) text-foreground"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="New password"
                />
              </div>
              <button
                className="mt-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm disabled:opacity-50"
                onClick={handleSaveAccount}
                disabled={loading}
              >
                {loading ? "Saving..." : "Save changes"}
              </button>
            </div>
          </section>
          <section className="bg-(--background) border border-border rounded-xl p-6 space-y-4 max-w-xl text-center">
            <h2 className="font-semibold text-lg text-foreground">Danger Zone</h2>
            <div className="space-y-3 text-sm">
              <button
                className="mt-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm disabled:opacity-50"
                onClick={handleDeleteAccount}
                disabled={loading}
              >
                {loading ? "Deleting..." : "Delete account"}
              </button>
            </div>
          </section>
        </main>
        <div className="mt-auto w-full border-t border-white/10 p-4 text-center text-xs text-zinc-500">
          <PublicLegalFooter />
        </div>
      </div>
    </div>
  );
}
