"use client";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

export default function SettingsPage() {
  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-8">
          <h1 className="text-2xl font-semibold">Settings</h1>

          <section className="bg-white border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg">Organization</h2>
            <div className="space-y-3 text-sm">
              <div>
                <label className="block text-foreground/70 mb-1">Name</label>
                <input
                  className="w-full border border-border rounded-lg px-3 py-2"
                  defaultValue="Municipality A"
                />
              </div>
              <div>
                <label className="block text-foreground/70 mb-1">Contact Email</label>
                <input
                  className="w-full border border-border rounded-lg px-3 py-2"
                  defaultValue="admin@municipality-a.gov"
                />
              </div>
              <button className="mt-2 px-4 py-2 rounded-lg bg-primary text-white text-sm">
                Save changes
              </button>
            </div>
          </section>

          <section className="bg-white border border-border rounded-xl p-6 space-y-4 max-w-xl">
            <h2 className="font-semibold text-lg">Subscription</h2>
            <p className="text-sm text-foreground/70">
              Current plan: <span className="font-semibold">Pro — 50€/month</span>
            </p>
            <button className="px-4 py-2 rounded-lg border border-border text-sm">
              Manage billing
            </button>
          </section>
        </main>
      </div>
    </div>
  );
}
