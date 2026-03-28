"use client";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

const mockOrgs = [
  { name: "Municipality A", type: "Municipality", plan: "Pro", regions: 2 },
  { name: "Rescue Group X", type: "NGO", plan: "Basic", regions: 1 },
  { name: "Civil Protection Y", type: "Agency", plan: "Enterprise", regions: 5 },
];

export default function OrganizationsPage() {
  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <h1 className="text-2xl font-semibold">Organizations</h1>

          <div className="bg-(--background) border border-border rounded-xl p-4">
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 border-b border-border">
                <tr>
                  <th className="text-left px-4 py-2">Name</th>
                  <th className="text-left px-4 py-2">Type</th>
                  <th className="text-left px-4 py-2">Plan</th>
                  <th className="text-left px-4 py-2">Regions</th>
                  <th className="text-left px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockOrgs.map((o) => (
                  <tr key={o.name} className="border-b border-border last:border-0">
                    <td className="px-4 py-2">{o.name}</td>
                    <td className="px-4 py-2">{o.type}</td>
                    <td className="px-4 py-2">{o.plan}</td>
                    <td className="px-4 py-2">{o.regions}</td>
                    <td className="px-4 py-2">
                      <button className="text-primary text-xs hover:underline">
                        View / Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </div>
  );
}
