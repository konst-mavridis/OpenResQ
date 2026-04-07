"use client";

import { useEffect, useState } from "react";
import { auth } from "../../lib/firebase";
import { apiGet, apiPost } from "../../lib/api";
import Sidebar from "../../components/Sidebar";
import Topbar from "../../components/Topbar";
import Link from "next/link";

interface Organization {
  id: string;
  name: string;
  plan: string;
  subscription_status: string;
  manual_override: boolean;
  limits: {
    responders: number;
    reports_per_month: number;
  };
  created_at?: any;
}

export default function SuperadminOrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      const token = await auth.currentUser?.getIdToken();
      if (!token) return;
      const data = await apiGet("/admin/billing/organizations", token);
      setOrganizations(data);
    } catch (err) {
      setError("Failed to load organizations. Are you a superadmin?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex bg-black min-h-screen text-white">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex bg-black min-h-screen text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar title="Superadmin: Organizations" />
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl">
              {error}
            </div>
          )}

          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">Manage Organizations</h2>
            <button className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-zinc-200 transition-colors">
              + New Organization
            </button>
          </div>

          <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl overflow-hidden backdrop-blur-xl">
            <table className="w-full text-left border-collapse">
                <thead>
                <tr className="border-b border-zinc-800 text-zinc-500 text-sm uppercase tracking-wider">
                    <th className="px-6 py-4 font-medium">Organization Name</th>
                    <th className="px-6 py-4 font-medium">Plan</th>
                    <th className="px-6 py-4 font-medium">Status</th>
                    <th className="px-6 py-4 font-medium">Limits (R/M)</th>
                    <th className="px-6 py-4 font-medium">Mode</th>
                    <th className="px-6 py-4 font-medium">Actions</th>
                </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800 font-medium">
                {organizations.map((org) => (
                    <tr key={org.id} className="hover:bg-zinc-800/30 transition-colors">
                    <td className="px-6 py-4">
                        <div className="font-bold">{org.name}</div>
                        <div className="text-xs text-zinc-500">{org.id}</div>
                    </td>
                    <td className="px-6 py-4 capitalize">
                        <span className={`px-2 py-1 rounded-lg text-xs ${
                        org.plan === 'enterprise' ? 'bg-emerald-500/10 text-emerald-500' : 
                        org.plan === 'pro' ? 'bg-purple-500/10 text-purple-500' : 'bg-blue-500/10 text-blue-500'
                        }`}>
                        {org.plan}
                        </span>
                    </td>
                    <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${org.subscription_status === 'active' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                        <span className="capitalize">{org.subscription_status}</span>
                        </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-zinc-400">
                        {org.limits.responders} / {org.limits.reports_per_month}
                    </td>
                    <td className="px-6 py-4">
                        {org.manual_override ? (
                        <span className="text-amber-500 text-xs font-bold uppercase tracking-tight">Manual</span>
                        ) : (
                        <span className="text-zinc-500 text-xs font-bold uppercase tracking-tight">Stripe Auto</span>
                        )}
                    </td>
                    <td className="px-6 py-4">
                        <Link 
                        href={`/superadmin/organizations/${org.id}`}
                        className="text-primary hover:text-primary/70 transition-colors"
                        >
                        Edit Subscription
                        </Link>
                    </td>
                    </tr>
                ))}
                </tbody>
            </table>
            {organizations.length === 0 && !error && (
                <div className="p-12 text-center text-zinc-500">
                No organizations found.
                </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
