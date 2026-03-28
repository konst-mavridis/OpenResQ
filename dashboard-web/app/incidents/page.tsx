"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { apiGet } from "../lib/api";
import { auth } from "../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

interface Incident {
  id: string;
  title: string;
  event_type: string;
  severity: string;
  latitude: number;
  longitude: number;
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user: User | null) => {
      if (user) {
        loadIncidents();
      } else {
        setIncidents([]);
        setLoading(false);
      }
    });
    return unsubscribe;
  }, []);

  async function loadIncidents() {
    setLoading(true);
    console.log("currentUser =", auth.currentUser);

    try {
        console.log("currentUser =", auth.currentUser);

      const token = await auth.currentUser?.getIdToken();
      console.log("Fetching incidents with token:", token);
      const data = await apiGet("/reports/nearby", token);
      console.log("Loaded incidents:", data);
      setIncidents(data);
    } catch (e) {
      console.error("Failed to load incidents", e);
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
          <h1 className="text-2xl font-semibold">Nearby Incidents</h1>

          {loading && <p className="text-foreground/60">Loading…</p>}

          {!loading && (
            <div className="bg-(--background) border border-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-(--background) border-b border-border">
                  <tr>
                    <th className="px-4 py-2 text-left">Title</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-left">Severity</th>
                    <th className="px-4 py-2 text-left">Latitude</th>
                    <th className="px-4 py-2 text-left">Longitude</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((r) => (
                    <tr key={r.id} className="border-b border-border">
                      <td className="px-4 py-2">{r.title}</td>
                      <td className="px-4 py-2">{r.event_type}</td>
                      <td className="px-4 py-2">{r.severity}</td>
                      <td className="px-4 py-2">{r.latitude}</td>
                      <td className="px-4 py-2">{r.longitude}</td>
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
