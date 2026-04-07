"use client";

import { useEffect, useState } from "react";
import { auth } from "../../../lib/firebase";
import { apiGet, apiPost } from "../../../lib/api";
import Sidebar from "../../../components/Sidebar";
import Topbar from "../../../components/Topbar";
import { useParams, useRouter } from "next/navigation";

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
  payments?: any[];
}

export default function OrganizationDetailsPage() {
  const { id } = useParams();
  const router = useRouter();
  const [org, setOrg] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Form state
  const [plan, setPlan] = useState("");
  const [status, setStatus] = useState("");
  const [responders, setResponders] = useState(0);
  const [reports, setReports] = useState(0);

  useEffect(() => {
    fetchOrganization();
  }, [id]);

  const fetchOrganization = async () => {
    try {
      const token = await auth.currentUser?.getIdToken();
      if (!token) return;
      const data = await apiGet(`/admin/billing/organizations/${id}`, token);
      setOrg(data);
      setPlan(data.plan);
      setStatus(data.subscription_status);
      setResponders(data.limits.responders);
      setReports(data.limits.reports_per_month);
    } catch (err) {
      setError("Failed to load organization details");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const token = await auth.currentUser?.getIdToken();
      if (!token) return;
      await apiPost(`/admin/billing/organizations/${id}/subscription`, {
        plan,
        subscription_status: status,
        limits: {
          responders,
          reports_per_month: reports
        }
      }, token);
      
      // router.push("/superadmin/organizations");
      // instead of redirecting, just update the state
      await fetchOrganization();
      alert("Subscription updated successfully!");
    } catch (err) {
      setError("Failed to update subscription");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="flex bg-black min-h-screen text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar title={`Superadmin: ${org?.name || 'Loading...'}`} />
        <main className="flex-1 overflow-y-auto p-6 space-y-8">
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex items-center gap-4 text-zinc-500 mb-2">
                <button 
                  onClick={() => router.back()}
                  className="bg-zinc-900 border border-zinc-800 px-3 py-1.5 rounded-lg hover:border-zinc-500 transition-all font-bold text-sm"
                >
                  ← BACK
                </button>
                <div className="h-4 w-px bg-zinc-800" />
                <span className="text-sm font-bold uppercase tracking-widest">{org?.id}</span>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl">
                {error}
              </div>
            )}

            {/* Manual Subscription Controls */}
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 backdrop-blur-xl">
              <h2 className="text-xl font-bold mb-8">Manual Subscription Control</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Plan */}
                <div>
                  <label className="block text-sm font-bold text-zinc-500 uppercase tracking-widest mb-3">Subscription Plan</label>
                  <select 
                    value={plan} 
                    onChange={(e) => setPlan(e.target.value)}
                    className="w-full bg-zinc-800/50 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-primary transition-colors text-lg"
                  >
                    <option value="basic">Basic Plan (€49)</option>
                    <option value="pro">Pro Plan (€149)</option>
                    <option value="enterprise">Enterprise Plan (€399)</option>
                    <option value="custom">Custom Plan (Overrides)</option>
                  </select>
                </div>

                {/* Status */}
                <div>
                  <label className="block text-sm font-bold text-zinc-500 uppercase tracking-widest mb-3">Subscription Status</label>
                  <select 
                    value={status} 
                    onChange={(e) => setStatus(e.target.value)}
                    className="w-full bg-zinc-800/50 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-primary transition-colors text-lg"
                  >
                    <option value="active">Active</option>
                    <option value="past_due">Past Due / Delinquent</option>
                    <option value="canceled">Canceled</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                {/* Responders Limit */}
                <div>
                  <label className="block text-sm font-bold text-zinc-500 uppercase tracking-widest mb-3">Max Responders</label>
                  <input 
                    type="number" 
                    value={responders} 
                    onChange={(e) => setResponders(parseInt(e.target.value))}
                    className="w-full bg-zinc-800/50 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-primary transition-colors text-lg"
                  />
                  <p className="text-xs text-zinc-500 mt-2">Set to 999999 for unlimited.</p>
                </div>

                {/* Reports Limit */}
                <div>
                  <label className="block text-sm font-bold text-zinc-500 uppercase tracking-widest mb-3">Max Reports / Month</label>
                  <input 
                    type="number" 
                    value={reports} 
                    onChange={(e) => setReports(parseInt(e.target.value))}
                    className="w-full bg-zinc-800/50 border border-zinc-800 rounded-xl px-4 py-3 outline-none focus:border-primary transition-colors text-lg"
                  />
                </div>
              </div>

              <div className="mt-12 flex justify-end">
                <button 
                  onClick={handleSave}
                  disabled={saving}
                  className="bg-primary text-black px-12 py-4 rounded-xl font-bold hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                >
                  {saving ? "SAVING..." : "SAVE CHANGES"}
                </button>
              </div>
            </div>

            {/* Payment History */}
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 backdrop-blur-xl">
              <h2 className="text-xl font-bold mb-6">Payment History</h2>
              <div className="overflow-hidden">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-zinc-800 text-zinc-500 text-sm uppercase tracking-wider">
                      <th className="py-4 font-medium">Date</th>
                      <th className="py-4 font-medium">Amount</th>
                      <th className="py-4 font-medium">Type</th>
                      <th className="py-4 font-medium">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800">
                    {org?.payments?.map((payment, i) => (
                      <tr key={i} className="text-sm">
                        <td className="py-4">{new Date(payment.created_at).toLocaleDateString()}</td>
                        <td className="py-4 font-bold text-zinc-300">€{payment.amount}</td>
                        <td className="py-4 uppercase text-xs tracking-tight text-zinc-400">{payment.type}</td>
                        <td className="py-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${payment.source === 'stripe' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                            {payment.source}
                          </span>
                        </td>
                      </tr>
                    ))}
                    {(!org?.payments || org.payments.length === 0) && (
                      <tr>
                        <td colSpan={4} className="py-8 text-center text-zinc-500 italic">No payment records found.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
