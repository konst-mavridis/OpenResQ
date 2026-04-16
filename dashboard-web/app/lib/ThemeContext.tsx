"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

type Theme = "light" | "dark" | "system";

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  actualTheme: "light" | "dark";
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Initialize theme from localStorage
function initializeTheme(): Theme {
  if (typeof window === "undefined") return "system";
  return (localStorage.getItem("theme") || "system") as Theme;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(initializeTheme);

  // Get system theme preference
  const getSystemTheme = useCallback((): "light" | "dark" => {
    if (typeof window !== "undefined") {
      return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
    }
    return "dark";
  }, []);

  // Derive actual theme from selected theme (no state needed)
  const actualTheme: "light" | "dark" = theme === "system" ? getSystemTheme() : theme;

  // Apply theme to DOM only
  const applyTheme = useCallback(
    (themeToApply: Theme) => {
      const actual = themeToApply === "system" ? getSystemTheme() : themeToApply;

      if (typeof document !== "undefined") {
        document.documentElement.classList.remove("dark");
        if (actual === "dark") {
          document.documentElement.classList.add("dark");
        }
      }
    },
    [getSystemTheme]
  );

  // Apply theme when it changes
  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => {
      applyTheme(theme);
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme, applyTheme]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem("theme", newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, actualTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}
