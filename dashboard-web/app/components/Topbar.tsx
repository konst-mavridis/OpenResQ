"use client";

import { Bell } from "lucide-react";
import { logout } from "../lib/auth";
import { IoExitOutline } from "react-icons/io5";

export default function Topbar() {
  return (
    <header className="w-full bg-(--background) border-b border-border px-6 py-3 flex justify-between items-center">
      <div className="font-semibold text-lg">Admin Console</div>

      <div className="flex items-center gap-6">
        <button className="text-foreground/70 hover:text-foreground">
          <Bell size={20} />
        </button>

        <button
          onClick={logout}
          className="text-sm text-red-600 hover:underline"
        >
          <IoExitOutline size={20} />
        </button>
      </div>
    </header>
  );
}
