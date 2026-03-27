"use client";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

const mockDevices = [
  { id: "SEN-001", type: "Smoke Sensor", status: "Online", location: "Region 1" },
  { id: "DRN-004", type: "Drone", status: "Offline", location: "Region 2" },
  { id: "GAT-010", type: "Gateway", status: "Online", location: "Region 3" },
];

export default function DevicesPage() {
  return (
    <div className="flex h-full">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />

        <main className="p-8 space-y-6">
          <h1 className="text-2xl font-semibold">Devices</h1>

          <div className="bg-white border border-border rounded-xl p-4">
            <table className="w-full text-sm">
              <thead className="bg-neutral-50 border-b border-border">
                <tr>
                  <th className="text-left px-4 py-2">ID</th>
                  <th className="text-left px-4 py-2">Type</th>
                  <th className="text-left px-4 py-2">Status</th>
                  <th className="text-left px-4 py-2">Location</th>
                  <th className="text-left px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockDevices.map((d) => (
                  <tr key={d.id} className="border-b border-border last:border-0">
                    <td className="px-4 py-2">{d.id}</td>
                    <td className="px-4 py-2">{d.type}</td>
                    <td className="px-4 py-2">{d.status}</td>
                    <td className="px-4 py-2">{d.location}</td>
                    <td className="px-4 py-2">
                      <button className="text-primary text-xs hover:underline">
                        View / Configure
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
