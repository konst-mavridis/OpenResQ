"use client";

import { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import { apiGet } from "./lib/api";
import { auth } from "./lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";
import ReportsMap from "./components/GoogleMap";
import ReportsGoogleMap from "./components/GoogleMap";

export default function DashboardHome() {
  const [reports, setReports] = useState([]);

  async function loadReports() {
    try {
      const token = await auth.currentUser?.getIdToken();
      const data = await apiGet("/reports/nearby", token);
      setReports(data);
    } catch (e) {
      console.error("Failed to load reports", e);
    }
  }

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user: User | null) => {
      if (user) {
        loadReports();
      } else {
        setReports([]);
      }
    });
    return unsubscribe;
  }, []);

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-8">
          <h1 className="text-3xl font-semibold">Dashboard</h1>

          <div className="grid md:grid-cols-4 gap-4">
            <div className="bg-gray-900 border border-border rounded-xl p-4">
              <div className="text-sm text-foreground/60">Nearby Reports</div>
              <div className="text-2xl font-semibold">{reports.length}</div>
            </div>
          </div>

          <div className="bg-gray-900 border border-border rounded-xl p-4 h-80">
            <div className="font-semibold mb-2">Map Overview</div>

            <div className="h-full">
              <ReportsGoogleMap reports={reports} />
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
