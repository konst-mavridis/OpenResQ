"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Sidebar from "../../../components/Sidebar";
import Topbar from "../../../components/Topbar";
import { apiGet, apiPost } from "../../../lib/api";
import { auth } from "../../../lib/firebase";
import { onAuthStateChanged, User } from "firebase/auth";

interface TeamDetails {
  id: string;
  display_name: string;
  displayName: string;
  leader_uid: string;
  leader_name?: string;
  members: any[];
}

export default function ManageTeamPage() {
  const params = useParams();
  const router = useRouter();
  const teamId = params.id as string;
  
  const [team, setTeam] = useState<TeamDetails | null>(null);
  
  // Form states
  const [displayName, setDisplayName] = useState("");
  const [leaderUid, setLeaderUid] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchTeamDetails = async (user: User) => {
    try {
      setLoading(true);
      setError("");
      const token = await user.getIdToken();
      
      const data = await apiGet(`/teams/${teamId}`, token);
      setTeam(data);
      
      setDisplayName(data.displayName || data.display_name || "");
      setLeaderUid(data.leader_uid || "");
    } catch (err) {
      console.error(err);
      setError("Failed to fetch team details.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!displayName || !leaderUid) {
      setError("Please fill out both the team name and leader UID.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const currentUser = auth.currentUser;
      if (!currentUser) throw new Error("Not logged in");
      const token = await currentUser.getIdToken();
      
      // Expected backend endpoint: POST /teams/{id}/manage or /teams/{id}
      // Note: we're using apiPost which maps to POST requests
      await apiPost(`/teams/${teamId}/manage`, {
        name: name,
        leader_uid: leaderUid
      }, token);

      setSuccess("Team settings updated successfully!");
      
      // Give the user a moment to see the success message
      setTimeout(() => {
        router.push(`/teams/${teamId}`);
      }, 1500);

    } catch (err) {
      console.error(err);
      setError("Failed to update team settings.");
    } finally {
      setSaving(false);
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
              <Link href={`/teams/${teamId}`} className="text-sm text-foreground/60 hover:underline mb-2 inline-block">
                &larr; Back to Team Details
              </Link>
              <h1 className="text-2xl font-semibold">
                Manage Team
              </h1>
            </div>
          </div>

          {loading ? (
             <div className="p-8 text-center text-foreground/60">Loading...</div>
          ) : (
             <div className="bg-(--background) border border-border rounded-xl p-6 max-w-xl space-y-6">
               <h2 className="font-semibold text-lg text-foreground">Edit Configuration</h2>
               
               {error && <div className="text-red-500 bg-red-500/10 p-4 rounded-lg text-sm">{error}</div>}
               {success && <div className="text-green-600 bg-green-500/10 p-4 rounded-lg text-sm">{success}</div>}
               
               <div className="space-y-4">
                 <div className="flex flex-col space-y-2">
                   <label className="text-sm font-medium text-foreground/70">
                     Team Display Name
                   </label>
                   <input
                     type="text"
                     value={displayName}
                     onChange={(e) => setDisplayName(e.target.value)}
                     className="border border-border rounded-lg px-3 py-2 bg-(--background) text-foreground text-sm"
                     placeholder="e.g. Rapid Response Team Alpha"
                   />
                 </div>

                 <div className="flex flex-col space-y-2">
                   <label className="text-sm font-medium text-foreground/70">
                     Team Leader
                   </label>
                   
                   <div className="border border-border rounded-lg overflow-hidden">
                     {team?.members && team.members.length > 0 ? (
                       <ul className="divide-y divide-border">
                         {team.members.map((member) => (
                           <li key={member.uid} className="flex items-center justify-between p-3 hover:bg-foreground/5 transition-colors">
                             <div className="flex flex-col">
                               <div className="flex items-center gap-2">
                                 <span className="font-medium text-sm">{member.name}</span>
                                 {leaderUid === member.uid && (
                                   <span className="bg-(--color-primary) text-white text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wide">Leader</span>
                                 )}
                               </div>
                               <span className="text-xs text-foreground/60">{member.uid}</span>
                             </div>
                             <button
                               onClick={() => setLeaderUid(member.uid)}
                               disabled={leaderUid === member.uid}
                               className={`text-xs px-3 py-1.5 rounded-md font-medium transition-colors ${
                                 leaderUid === member.uid 
                                   ? 'bg-foreground/5 text-foreground/40 cursor-not-allowed hidden' 
                                   : 'bg-foreground/10 hover:bg-foreground/20 text-foreground'
                               }`}
                             >
                               Make Leader
                             </button>
                           </li>
                         ))}
                       </ul>
                     ) : (
                       <div className="p-4 text-center text-sm text-foreground/60">
                         No members found in this team to promote.
                       </div>
                     )}
                   </div>
                   
                   <p className="text-xs text-foreground/50">
                     The assigned leader will be able to manage this team.
                   </p>
                 </div>
               </div>

               <div className="pt-4 flex justify-end">
                 <button
                   onClick={handleSave}
                   disabled={saving}
                   className="px-6 py-2 bg-(--color-primary) text-white rounded-lg hover:opacity-90 disabled:opacity-50 text-sm font-medium"
                 >
                   {saving ? "Saving..." : "Save Changes"}
                 </button>
               </div>
             </div>
          )}
        </main>
      </div>
    </div>
  );
}
