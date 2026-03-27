"use client";

import { useEffect, useMemo, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import ReportsGoogleMap from "../components/GoogleMap";
import { apiGet } from "../lib/api";
import { auth } from "../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

interface Incident {
  id: string;
  title: string;
  event_type: string;
  severity?: string;
  latitude: number;
  longitude: number;
  created_at?: string;
  timestamp?: string;
  resolved_at?: string;
}

function monthKey(dateString: string) {
  const d = new Date(dateString);
  if (Number.isNaN(d.getTime())) return "Unknown";
  return d.toLocaleString("default", { month: "short", year: "numeric" });
}

export default function AnalyticsPage() {
  const [reports, setReports] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user: User | null) => {
      if (user) {
        loadReports();
      } else {
        setReports([]);
        setLoading(false);
      }
    });
    return unsubscribe;
  }, []);

  async function loadReports() {
    setLoading(true);
    try {
      const token = await auth.currentUser?.getIdToken();
      const data = await apiGet("/reports/nearby", token);
      setReports(data);
    } catch (error) {
      console.error("Failed to load nearby reports", error);
      setReports([]);
    } finally {
      setLoading(false);
    }
  }

  const monthlyCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    reports.forEach((report) => {
      const rawDate = report.created_at || report.timestamp || "";
      const key = rawDate ? monthKey(rawDate) : "Unknown";
      counts[key] = (counts[key] || 0) + 1;
    });
    const entries = Object.entries(counts).sort(
      ([a], [b]) =>
        new Date(a).getTime() - new Date(b).getTime() || a.localeCompare(b)
    );
    return entries;
  }, [reports]);

  const monthlyAvgResponse = useMemo(() => {
    const totals: Record<string, { sum: number; count: number }> = {};

    reports.forEach((report) => {
      const start = report.created_at || report.timestamp;
      const end = report.resolved_at;
      if (!start || !end) return;

      const startDate = new Date(start);
      const endDate = new Date(end);
      if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) return;
      if (endDate < startDate) return;

      const minutes = (endDate.getTime() - startDate.getTime()) / 60000;
      const hours = minutes / 60;
      const month = monthKey(start);

      if (!totals[month]) totals[month] = { sum: 0, count: 0 };
      totals[month].sum += hours;
      totals[month].count += 1;
    });

    const entries = Object.entries(totals)
      .map(([month, value]) => ({ month, avg: value.sum / value.count, count: value.count }))
      .sort((a, b) => new Date(a.month).getTime() - new Date(b.month).getTime());

    return entries;
  }, [reports]);

  const [selectedMonth, setSelectedMonth] = useState<string>("All");

  const reportsByMonth = useMemo(() => {
    return reports.map((report) => {
      const rawDate = report.created_at || report.timestamp || "";
      const month = rawDate ? monthKey(rawDate) : "Unknown";
      return { report, month };
    });
  }, [reports]);

  const filteredReports = useMemo(() => {
    if (selectedMonth === "All") return reportsByMonth;
    return reportsByMonth.filter((entry) => entry.month === selectedMonth);
  }, [reportsByMonth, selectedMonth]);

  const maxCount = Math.max(1, ...monthlyCounts.map(([, count]) => count));

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <h1 className="text-2xl font-semibold">Analytics</h1>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="bg-gray-900 border border-border rounded-xl p-4">
              <div className="font-semibold mb-2">Incidents Over Time</div>
              {loading ? (
                <div className="h-64 bg-neutral-100 rounded-lg flex items-center justify-center text-sm text-foreground/60">
                  Loading incidents data…
                </div>
              ) : monthlyCounts.length === 0 ? (
                <div className="h-64 bg-neutral-100 rounded-lg flex items-center justify-center text-sm text-foreground/60">
                  No report data available
                </div>
              ) : (
                <div className="h-64 space-y-2">
                  {monthlyCounts.map(([month, count]) => (
                    <div key={month} className="flex items-center gap-2">
                      <span className="w-20 text-xs text-gray-600">{month}</span>
                      <div className="h-5 bg-blue-100 rounded overflow-hidden flex-1">
                        <div
                          className="h-full bg-blue-500"
                          style={{ width: `${(count / maxCount) * 100}%` }}
                        />
                      </div>
                      <span className="w-8 text-right text-xs">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="bg-gray-900 border border-border rounded-xl p-4 h-64">
              <div className="font-semibold mb-2">Average Resolve Time (hours)</div>
              {loading ? (
                <div className="h-full bg-neutral-100 rounded-lg flex items-center justify-center text-sm text-foreground/60">
                  Loading data…
                </div>
              ) : monthlyAvgResponse.length === 0 ? (
                <div className="h-full bg-neutral-100 rounded-lg flex items-center justify-center text-sm text-foreground/60">
                  No response-time data
                </div>
              ) : (
                <div className="h-full space-y-2 overflow-y-auto">
                  {monthlyAvgResponse.map(({ month, avg, count }) => {
                    const width = Math.min(100, (avg / Math.max(...monthlyAvgResponse.map((x) => x.avg))) * 100);
                    return (
                      <div key={month} className="flex items-center gap-2">
                        <span className="w-20 text-xs text-gray-600">{month}</span>
                        <div className="h-4 bg-blue-100 rounded overflow-hidden flex-1">
                          <div
                            className="h-full bg-emerald-500"
                            style={{ width: `${width}%` }}
                          />
                        </div>
                        <span className="w-16 text-right text-xs">{avg.toFixed(1)}h ({count})</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-gray-900 border border-border rounded-xl p-4 md:col-span-2">
              <div className="flex items-center justify-between mb-3">
                <div className="font-semibold">Heatmap by Month</div>
                <select
                  value={selectedMonth}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="border border-border rounded px-2 py-1 text-sm"
                >
                  <option value="All">All</option>
                  {monthlyCounts.map(([month]) => (
                    <option key={month} value={month}>
                      {month}
                    </option>
                  ))}
                </select>
              </div>

              {filteredReports.length === 0 ? (
                <div className="h-64 bg-neutral-100 rounded-lg flex items-center justify-center text-sm text-foreground/60">
                  No data for selected month
                </div>
              ) : (
                <div className="h-80">
                  <ReportsGoogleMap
                    reports={filteredReports.map((entry) => entry.report)}
                    heatmap
                  />
                  <div className="mt-2 text-xs text-gray-600">
                    Red/orange clusters indicate high incident density.
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
