"use client";

import { useState, useEffect, useCallback } from "react";
import { auth } from "../lib/firebase";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function SettingsPage() {
  const [theme, setTheme] = useState("dark");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const getSystemTheme = useCallback(() => {
    if (typeof window !== "undefined") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    return "dark";
  }, []);

  const applyTheme = useCallback(
    (themeValue: string) => {
      const actualTheme = themeValue === "system" ? getSystemTheme() : themeValue;
      document.documentElement.classList.remove("light", "dark");

      if (actualTheme === "dark") {
        document.documentElement.classList.add("dark");
      } else if (actualTheme === "light") {
        document.documentElement.classList.add("light");
      }
    },
    [getSystemTheme]
  );

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") || "dark";
    setTheme(savedTheme);
    applyTheme(savedTheme);

    if (auth.currentUser) {
      setEmail(auth.currentUser.email || "");
    }
  }, [applyTheme]);

  useEffect(() => {
    // Listen for system theme changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => {
      if (theme === "system") {
        applyTheme("system");
      }
    };
    mediaQuery.addEventListener("change", handleChange);

    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme, applyTheme]);

  const handleThemeChange = async (newTheme: string) => {
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);

    try {
      const token = await auth.currentUser?.getIdToken();
      await fetch("${process.env.NEXT_PUBLIC_API_BASE_URL}/user/theme", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ theme: newTheme }),
      });
    } catch (error) {
      console.error("Error saving theme:", error);
    }
  };

  const handleSaveAccount = async () => {
    setLoading(true);
    try {
      const token = await auth.currentUser?.getIdToken();
      const updates: Record<string, string> = {};
      if (email !== auth.currentUser?.email) updates.email = email;
      if (password) updates.password = password;

      if (Object.keys(updates).length > 0) {
        await fetch("${process.env.NEXT_PUBLIC_API_BASE_URL}/user/change", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(updates),
        });
        alert("Account updated successfully");
        setPassword("");
      }
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
      await fetch("/user/delete", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
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

        <main className="p-8 space-y-8">
          <h1 className="text-2xl font-semibold">Settings</h1>

          <section className="bg-(--background) border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg">Theme</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-4">
                <select
                  className="border border-border rounded-lg px-3 py-2"
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
            <h2 className="font-semibold text-lg">Account</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center space-x-4">
                <label className="w-24">Email</label>
                <input
                  type="email"
                  className="border border-border rounded-lg px-3 py-2 flex-1"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <div className="flex items-center space-x-4">
                <label className="w-24">Password</label>
                <input
                  type="password"
                  className="border border-border rounded-lg px-3 py-2 flex-1"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="New password"
                />
              </div>
              <button
                className="mt-2 px-4 py-2 rounded-lg bg-primary text-white text-sm disabled:opacity-50"
                onClick={handleSaveAccount}
                disabled={loading}
              >
                {loading ? "Saving..." : "Save changes"}
              </button>
            </div>
          </section>
          <section className="bg-(--background) text-center border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg ">Danger Zone</h2>
            <div className="space-y-3 text-sm">
              <button
                className="mt-2 px-4 py-2 rounded-lg bg-red-600 text-white text-sm disabled:opacity-50"
                onClick={handleDeleteAccount}
                disabled={loading}
              >
                {loading ? "Deleting..." : "Delete account"}
              </button>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
