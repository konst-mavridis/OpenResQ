"use client";

import { Bell } from "lucide-react";
import { logout } from "../lib/auth";

export default function Topbar() {
  return (
    <header className="w-full bg-gray-900 border-b border-border px-6 py-3 flex justify-between items-center">
      <div className="font-semibold text-lg">Admin Console</div>

      <div className="flex items-center gap-6">
        <button className="text-foreground/70 hover:text-foreground">
          <Bell size={20} />
        </button>

        <button
          onClick={logout}
          className="text-sm text-red-600 hover:underline"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
