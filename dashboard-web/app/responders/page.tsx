"use client";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";
import { auth } from "../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

interface Responder {
  uid: string;
  displayName?: string;
  display_name?: string;
  email: string;
  duty: boolean;
  area: {
    latitude: number;
    longitude: number;
  };
}

export default function RespondersPage() {
      const [responders, setResponders] = useState<Responder[]>([]);
      const [loading, setLoading] = useState(true);

      useEffect(() => {
        document.title = "Responders - OpenResQ";
      }, []);
      useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user: User | null) => {
      if (user) {
        loadResponders();
      } else {
        setResponders([]);
        setLoading(false);
      }
    });
    return unsubscribe;
  }, []);

  async function loadResponders() {
    setLoading(true);

    try {
      const token = await auth.currentUser?.getIdToken();
      const data = await apiGet("/admin/responders", token);
      setResponders(data);
    } catch (e) {
      console.error("Failed to load responders", e);
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <h1 className="text-2xl font-semibold">Nearby Responders</h1>

          {loading && <p className="text-foreground/60">Loading…</p>}

          {!loading && (
            <div className="bg-(--background) border border-border rounded-xl p-4">
              <table className="w-full text-sm">
                <thead className="bg-(--background) border-b border-border">
                  <tr>
                    <th className="text-left px-4 py-2">Name</th>
                    <th className="text-left px-4 py-2">Email</th>
                    <th className="text-left px-4 py-2">Duty</th>
                    <th className="text-left px-4 py-2">Latitude</th>
                    <th className="text-left px-4 py-2">Longitude</th>
                  </tr>
                </thead>
                <tbody>
                  {responders.map((r) => (
                    <tr key={r.uid} className="border-b border-border last:border-0">
                      <td className="px-4 py-2">{r.displayName ?? r.display_name ?? "—"}</td>
                      <td className="px-4 py-2">{r.email}</td>
                      <td className="px-4 py-2">{r.duty ? "On Duty" : "Off Duty"}</td>
                      <td className="px-4 py-2">{r.area.latitude}</td>
                      <td className="px-4 py-2">{r.area.longitude}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
