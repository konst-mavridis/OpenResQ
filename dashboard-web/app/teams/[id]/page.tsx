"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import Sidebar from "../../components/Sidebar";
import Topbar from "../../components/Topbar";
import { apiGet } from "../../lib/api";
import { auth } from "../../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

interface Member {
  uid: string;
  name: string;
  role: string;
  incidents_resolved: number;
}

interface TeamDetails {
  id: string;
  displayName: string;
  leader_uid: string;
  leader_name?: string;
  members: Member[];
}

export default function TeamDetailsPage() {
  const params = useParams();
  const teamId = params.id as string;
  
  const [team, setTeam] = useState<TeamDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchTeamDetails = async (user: User) => {
    try {
      setLoading(true);
      setError("");
      const token = await user.getIdToken();
      
      // Expected backend endpoint: GET /teams/{id}
      const data = await apiGet(`/teams/${teamId}`, token);
      setTeam(data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch team details. Make sure your backend implements GET /teams/{id}");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        fetchTeamDetails(user);
      } else {
        setLoading(false);
      }
    });
    return unsubscribe;
  }, [teamId]);

  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <Link href="/teams" className="text-sm text-foreground/60 hover:underline mb-2 inline-block">
                &larr; Back to Teams
              </Link>
              <h1 className="text-2xl font-semibold">
                {team?.displayName || "Team Details"}
              </h1>
            </div>
            
            {team && (auth.currentUser?.uid === team.leader_uid || /* or is admin */ true) && (
              <Link
                href={`/teams/${teamId}/manage`}
                className="text-sm bg-(--color-primary) text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity"
              >
                Manage Team
              </Link>
            )}
          </div>

          {error && <div className="p-4 bg-red-500/10 text-red-500 rounded-lg text-sm">{error}</div>}

          {loading ? (
            <div className="p-8 text-center text-foreground/60">Loading team data...</div>
          ) : team ? (
            <div className="grid md:grid-cols-2 gap-6">
              
              <div className="bg-(--background) border border-border rounded-xl p-6 space-y-4">
                <h2 className="text-lg font-semibold">Overview</h2>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-foreground/70">Leader Name</span>
                    <span className="font-medium">{team.leader_name || "Unknown"}</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-foreground/70">Total Members</span>
                    <span className="font-medium">{team.members?.length || 0}</span>
                  </div>
                  <div className="flex justify-between border-b border-border pb-2">
                    <span className="text-foreground/70">Total Incidents Resolved</span>
                    <span className="font-medium">
                      {team.members?.reduce((acc, m) => acc + (m.incidents_resolved || 0), 0) || 0}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-(--background) border border-border rounded-xl p-0 overflow-hidden md:col-span-2">
                <div className="p-6 border-b border-border">
                  <h2 className="text-lg font-semibold">Team Members & Activity</h2>
                  <p className="text-sm text-foreground/60">See how many incidents each member has resolved.</p>
                </div>
                
                {team.members && team.members.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-foreground/5 border-b border-border">
                        <tr>
                          <th className="text-left px-6 py-3 font-medium">Name</th>
                          <th className="text-left px-6 py-3 font-medium">Role</th>
                          <th className="text-right px-6 py-3 font-medium">Incidents Resolved</th>
                        </tr>
                      </thead>
                      <tbody>
                        {team.members.map((member) => (
                          <tr key={member.uid} className="border-b border-border last:border-0 hover:bg-foreground/5 transition-colors">
                            <td className="px-6 py-4 font-medium">{member.name}</td>
                            <td className="px-6 py-4 text-foreground/70">{member.role}</td>
                            <td className="px-6 py-4 text-right font-medium">
                              {member.incidents_resolved || 0}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-foreground/60 text-sm">No members found in this team.</div>
                )}
              </div>

            </div>
          ) : null}
        </main>
      </div>
    </div>
  );
}
