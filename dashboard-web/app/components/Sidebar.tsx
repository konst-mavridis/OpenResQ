"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/incidents", label: "Incidents" },
  { href: "/responders", label: "Responders" },
  { href: "/teams", label: "Teams" }, // TODO: create a system that has multiple teams into one organization.
  { href: "/analytics", label: "Analytics" },
  { href: "/billing", label: "Billing" },
  // { href: "/devices", label: "Devices" },
  { href: "/settings", label: "Settings" }, // TODO: this should be for user settings, not global settings. Global settings should be in a separate admin panel that only org admins can access. Also need to implement user roles and permissions. And adjust this to the teams-org system
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-(--background) border-r border-border p-6 flex flex-col">
      <div className="font-bold text-xl mb-8">OpenResQ</div>

      <nav className="space-y-2 flex-1">
        {links.map((link) => {
          const active = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`block rounded-lg px-3 py-2 text-sm ${
                active
                  ? "bg-(--sidebar-active) text-foreground font-medium"
                  : "text-foreground/80 hover:bg-(--sidebar-hover)"
              }`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
