"use client";

import { useCallback, useEffect, useState } from "react";
import { auth } from "../lib/firebase";
import { apiGet } from "../lib/api";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

interface BillingStatus {
  plan: string;
  status: string;
  current_period_end: number | null;
  manual_override: boolean;
  limits: {
    responders: number;
    reports_per_month: number;
  };
  usage: {
    responders: number;
    incidents_this_month: number;
  };
  features: string[];
}

export default function BillingPage() {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchBillingStatus = useCallback(async (retries = 0) => {
    try {
      setLoading(true);
      const token = await auth.currentUser?.getIdToken();
      if (!token) {
        console.log("No auth token available");
        return;
      }

      // Force fresh fetch with cache busting
      const data = await apiGet(`/billing/status?timestamp=${Date.now()}`, token);
      console.log("Billing status fetched:", data);
      setStatus(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching billing status:", err);

      // Retry up to 3 times with delay for eventual consistency
      if (retries < 3) {
        console.log(`Retrying status fetch (attempt ${retries + 1}/3)...`);
        await new Promise((resolve) => setTimeout(resolve, 1000));
        return fetchBillingStatus(retries + 1);
      }

      setError("Failed to load billing status");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initializePage = async () => {
      // Check for upgrade success
      const params = new URLSearchParams(window.location.search);
      const upgradeSuccess = params.get("upgrade");
      const sessionId = params.get("session_id");

      if (upgradeSuccess === "success" && sessionId) {
        try {
          setLoading(true);
          // Complete the upgrade process
          const response = await fetch(
            `/api/billing/upgrade-complete?session_id=${sessionId}`
          );
          const result = await response.json();

          console.log("Upgrade complete response:", result);

          if (result.status === "success") {
            setSuccessMessage(
              `Congratulations! You've successfully upgraded to the ${result.planId} plan.`
            );
            // Clear the URL params
            window.history.replaceState({}, document.title, "/billing");

            if (!result.org_updated) {
              console.warn("Backend could not locate the org to update — will retry fetching status");
            }

            // Force token refresh so the updated org data is returned
            await auth.currentUser?.getIdToken(true);
            // Wait a moment for Firestore consistency
            await new Promise((resolve) => setTimeout(resolve, 2000));
          }
        } catch (err) {
          console.error("Error completing upgrade:", err);
          setError("Upgrade completed but we had an issue updating your info");
        }
      }

      // Fetch billing status with retries to wait for backend updates
      await fetchBillingStatus();
    };

    initializePage();
  }, [fetchBillingStatus]);

  const getLocation = (): Promise<{ latitude: number; longitude: number }> => {
    return new Promise((resolve, reject) => {
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            resolve({
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            });
          },
          (error) => {
            console.warn("Geolocation permission denied:", error);
            // Resolve with null values if denied
            resolve({ latitude: 0, longitude: 0 });
          }
        );
      } else {
        console.warn("Geolocation not supported");
        reject(new Error("Geolocation not supported"));
      }
    });
  };

  const handleUpgrade = async (planId: string) => {
    setUpgrading(planId);
    try {
      const user = auth.currentUser;
      if (!user) {
        setError("User not authenticated");
        return;
      }

      // Get location
      const location = await getLocation();

      if (!user.email) {
        setError("User email not available");
        return;
      }

      // Call upgrade API with location
      const response = await fetch("/api/billing/upgrade-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          planId,
          uid: user.uid,
          email: user.email,
          latitude: location.latitude,
          longitude: location.longitude,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create checkout session");
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (err) {
      setError(
        `Failed to upgrade plan: ${err instanceof Error ? err.message : String(err)}`
      );
      console.error(err);
    } finally {
      setUpgrading(null);
    }
  };

  if (loading) {
    return (
      <div className="flex bg-black min-h-screen">
        <Sidebar className="hidden lg:block w-64" />
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  const plans = [
    { id: "basic", name: "Basic", price: 100, color: "blue" },
    { id: "pro", name: "Pro", price: 250, color: "purple" },
    { id: "enterprise", name: "Enterprise", price: null, priceLabel: "Contact Us", billingLabel: "Custom pricing", color: "emerald" },
  ];

  return (
    <div className="flex bg-black min-h-screen text-white">
      <Sidebar className="hidden lg:block w-64" />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar title="Billing & Subscription" />
        <main className="flex-1 overflow-y-auto p-6 space-y-8">
          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-500 px-4 py-3 rounded-xl">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="bg-emerald-500/20 border border-emerald-500 text-emerald-500 px-4 py-3 rounded-xl flex items-center justify-between">
              <span>{successMessage}</span>
              <button 
                onClick={() => fetchBillingStatus()}
                className="text-emerald-400 hover:text-emerald-300 underline text-sm ml-4"
              >
                Refresh Now
              </button>
            </div>
          )}

          {/* Current Status Card */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-3xl p-8 backdrop-blur-xl">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <h2 className="text-sm font-medium text-zinc-500 uppercase tracking-wider mb-1">Current Plan</h2>
                <div className="flex items-center gap-3">
                  <h3 className="text-3xl font-bold capitalize">{status?.plan} Plan</h3>
                  <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${status?.status === 'active' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'}`}>
                    {status?.status?.toUpperCase()}
                  </span>
                  <button
                    onClick={() => fetchBillingStatus()}
                    className="ml-auto text-xs text-zinc-400 hover:text-white bg-zinc-800 hover:bg-zinc-700 px-3 py-1 rounded-lg transition"
                  >
                    Refresh
                  </button>
                </div>
                {status?.current_period_end && (
                  <p className="text-zinc-400 mt-2">
                    Next billing date: {new Date(status.current_period_end * 1000).toLocaleDateString()}
                  </p>
                )}
                {status?.manual_override && (
                  <p className="text-amber-400 text-sm mt-1 flex items-center gap-2">
                    <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />
                    Manual override active
                  </p>
                )}
              </div>
              <div className="flex flex-col items-end gap-2">
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-xs text-zinc-500 uppercase font-medium">Responders</p>
                    <p className="text-xl font-bold">{status?.usage.responders} / {status?.limits.responders}</p>
                  </div>
                  <div className="h-10 w-px bg-zinc-800" />
                  <div className="text-right">
                    <p className="text-xs text-zinc-500 uppercase font-medium">Reports</p>
                    <p className="text-xl font-bold">{status?.usage.incidents_this_month} / {status?.limits.reports_per_month}</p>
                  </div>
                </div>
                {/* Progress bar (e.g. responders) */}
                <div className="w-48 h-1.5 bg-zinc-800 rounded-full overflow-hidden mt-1">
                  <div 
                    className="h-full bg-primary" 
                    style={{ width: `${Math.min(100, (status?.usage.responders || 0) / (status?.limits.responders || 1) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Upgrade Options */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Upgrade Your Organization</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {plans.map((p) => (
                <div 
                  key={p.id} 
                  className={`bg-zinc-900/50 border ${status?.plan === p.id ? 'border-primary' : 'border-zinc-800'} rounded-3xl p-8 flex flex-col hover:border-zinc-600 transition-all duration-300`}
                >
                  <h3 className="text-xl font-bold mb-1">{p.name}</h3>
                  {typeof p.price === "number" ? (
                    <div className="flex items-baseline gap-1 mb-6">
                      <span className="text-3xl font-bold">EUR {p.price}</span>
                      <span className="text-zinc-500">/month</span>
                    </div>
                  ) : (
                    <div className="mb-6 space-y-1">
                      <span className="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-sm font-semibold text-emerald-300">
                        {p.priceLabel}
                      </span>
                      <p className="text-sm text-zinc-500">{p.billingLabel}</p>
                    </div>
                  )}
                  <ul className="space-y-3 mb-8 flex-1">
                    <li className="flex items-center gap-2 text-zinc-400">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-emerald-500">
                        <path d="M13.3333 4L6 11.3333L2.66666 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {p.id === "enterprise" ? "Unlimited Responders" : `${p.id === "pro" ? "50" : "25"} Responders`}
                    </li>
                    <li className="flex items-center gap-2 text-zinc-400">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-emerald-500">
                        <path d="M13.3333 4L6 11.3333L2.66666 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {p.id === "enterprise" ? "Unlimited Reports" : `${p.id === "pro" ? "10,000" : "1,000"} Reports`}
                    </li>
                    <li className="flex items-center gap-2 text-zinc-400">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="text-emerald-500">
                        <path d="M13.3333 4L6 11.3333L2.66666 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      {p.id === "basic" ? "Basic Features" : p.id === "pro" ? "Advanced Features" : "Custom Deployment"}
                    </li>
                  </ul>
                  <button
                    disabled={status?.plan === p.id || upgrading !== null}
                    onClick={() => handleUpgrade(p.id)}
                    className={`w-full py-3 rounded-xl font-bold transition-all duration-300 ${
                      status?.plan === p.id 
                        ? 'bg-zinc-800 text-zinc-500 cursor-default' 
                        : 'bg-white text-black hover:bg-zinc-200 disabled:opacity-50'
                    }`}
                  >
                    {upgrading === p.id ? (
                        <span className="flex items-center justify-center gap-2">
                        <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                        Processing...
                        </span>
                    ) : status?.plan === p.id ? "Current Plan" : "Select Plan"}
                  </button>
                </div>
              ))}
            </div>
          </div>

          <p className="text-center text-zinc-500 text-sm">
            Need a custom plan for your city or enterprise? <button className="text-primary hover:underline">Contact our sales team</button>.
          </p>
        </main>
      </div>
    </div>
  );
}
