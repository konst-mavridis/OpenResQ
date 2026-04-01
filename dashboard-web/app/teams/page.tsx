"use client";

import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import { apiGet, apiPost } from "../lib/api";
import { auth } from "../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";
import Link from "next/link"; // added Link import

interface Team {
  id: string;
  name?: string;
  display_name?: string;
  displayName?: string;
  latitude: number | string;
  longitude: number | string;
  distance_km: number;
  leader_name?: string;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Teams - OpenResQ";
  }, []);

  const fetchTeams = async (user: User) => {
    try {
      setLoading(true);
      setError("");
      
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            try {
              const token = await user.getIdToken();
              // Make sure the path matches your backend router prefix for teams, e.g. /teams/nearby
              const response = await apiGet(`/teams/nearby?lat=${lat}&lng=${lng}`, token);
              // Handle endpoints that directly return lists
              setTeams(Array.isArray(response) ? response : []);
            } catch (err) {
              console.error(err);
              setError("Failed to fetch teams from backend.");
            } finally {
              setLoading(false);
            }
          },
          (err) => {
            console.error(err);
            setError("Location access denied. We need your location to find nearby teams.");
            setLoading(false);
          }
        );
      } else {
        setError("Geolocation not supported by this browser.");
        setLoading(false);
      }
    } catch (e) {
      console.error(e);
      setError("An unexpected error occurred.");
      setLoading(false);
    }
  };

  const handleCreateTeam = async () => {
    const name = window.prompt("Enter a name for the new team:");
    if (!name || !name.trim()) return;

    try {
      setLoading(true);
      const currentUser = auth.currentUser;
      if (!currentUser) {
        setLoading(false);
        return;
      }
      
      if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(
          async (position) => {
            try {
              const lat = position.coords.latitude;
              const lng = position.coords.longitude;
              const token = await currentUser.getIdToken();
              
              await apiPost(`/teams/create`, { 
                name: name.trim(),
                latitude: lat,
                longitude: lng
              }, token);
              
              fetchTeams(currentUser);
            } catch (err) {
              console.error(err);
              alert("Failed to create team. Ensure your backend supports this endpoint.");
              setLoading(false);
            }
          },
          (err) => {
            console.error(err);
            alert("Location access is required to create a team.");
            setLoading(false);
          }
        );
      } else {
        alert("Geolocation is not supported by this browser.");
        setLoading(false);
      }
    } catch (e) {
      console.error(e);
      alert("An unexpected error occurred.");
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        fetchTeams(user);
      } else {
        setLoading(false);
      }
    });
    return unsubscribe;
  }, []);

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-semibold">Nearby Teams</h1>
            <div className="flex gap-2">
              <button 
                onClick={handleCreateTeam}
                disabled={loading}
                className="text-sm bg-(--background) border border-border text-foreground px-4 py-2 rounded-lg hover:bg-foreground/5 disabled:opacity-50"
              >
                Create Team
              </button>
              <button 
                onClick={() => { if (auth.currentUser) fetchTeams(auth.currentUser) }}
                disabled={loading}
                className="text-sm bg-(--color-primary) text-white px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Refreshing..." : "Refresh"}
              </button>
            </div>
          </div>

          {error && <div className="text-red-500 bg-red-500/10 p-4 rounded-lg text-sm">{error}</div>}

          <div className="bg-(--background) border border-border rounded-xl px-0 py-2 overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-foreground/60">Fetching your location & nearby teams...</div>
            ) : teams.length === 0 && !error ? (
              <div className="p-8 text-center text-foreground/60">No teams found nearby.</div>
            ) : teams.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-foreground/5 border-b border-border">
                    <tr>
                      <th className="text-left px-6 py-3 font-medium">Name</th>
                      <th className="text-left px-6 py-3 font-medium">Distance</th>
                      <th className="text-left px-6 py-3 font-medium">Location (Lat, Lng)</th>
                      <th className="text-left px-6 py-3 font-medium">Leader</th>
                      <th className="text-right px-6 py-3 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teams.map((t) => (
                      <tr key={t.id} className="border-b border-border last:border-0 hover:bg-foreground/5 transition-colors">
                        <td className="px-6 py-4 font-medium">{t.name || t.display_name || t.displayName || "Unknown Team"}</td>
                        <td className="px-6 py-4">{t.distance_km} km</td>
                        <td className="px-6 py-4 text-foreground/70">
                          {typeof t.latitude === 'number' ? t.latitude.toFixed(4) : t.latitude},{" "}
                          {typeof t.longitude === 'number' ? t.longitude.toFixed(4) : t.longitude}
                        </td>
                        <td className="px-6 py-4 text-foreground/70">{t.leader_name || "Unknown Leader"}</td>
                        <td className="px-6 py-4 text-right">
                          <Link href={`/teams/${t.id}`} className="text-(--color-primary) font-medium text-xs hover:underline">
                            View Details
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        </main>
      </div>
    </div>
  );
}
