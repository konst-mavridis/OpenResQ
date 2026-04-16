"use client";

import { Sun, Moon, Monitor } from "lucide-react";
import { useTheme } from "../lib/ThemeContext";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-1 rounded-full border border-border bg-(--background) p-1 shadow-sm">
      <button
        onClick={() => setTheme("light")}
        className={`rounded-full p-2 transition ${
          theme === "light"
            ? "bg-primary text-white shadow-sm"
            : "text-foreground/50 hover:bg-(--sidebar-hover) hover:text-foreground"
        }`}
        title="Light Mode"
      >
        <Sun size={14} />
      </button>
      <button
        onClick={() => setTheme("dark")}
        className={`rounded-full p-2 transition ${
          theme === "dark"
            ? "bg-primary text-white shadow-sm"
            : "text-foreground/50 hover:bg-(--sidebar-hover) hover:text-foreground"
        }`}
        title="Dark Mode"
      >
        <Moon size={14} />
      </button>
      <button
        onClick={() => setTheme("system")}
        className={`rounded-full p-2 transition ${
          theme === "system"
            ? "bg-primary text-white shadow-sm"
            : "text-foreground/50 hover:bg-(--sidebar-hover) hover:text-foreground"
        }`}
        title="System Preference"
      >
        <Monitor size={14} />
      </button>
    </div>
  );
}
