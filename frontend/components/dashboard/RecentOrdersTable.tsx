"use client";

import Link from "next/link";
import { RefreshCw, ArrowRight } from "lucide-react";
import { UniversalEvent } from "@/lib/types";

interface RecentOrdersTableProps {
  events: UniversalEvent[];
  onRefresh?: () => void;
}

const VENDOR_AVATAR_COLORS: Record<string, string> = {
  Cisco: "bg-blue-100 text-blue-700",
  Fortinet: "bg-red-100 text-red-700",
  "Palo Alto": "bg-orange-100 text-orange-700",
  Generic: "bg-slate-100 text-slate-700",
  Suricata: "bg-amber-100 text-amber-700",
  AWS: "bg-purple-100 text-purple-700",
  Custom: "bg-emerald-100 text-emerald-700",
};

export default function RecentOrdersTable({
  events,
  onRefresh,
}: RecentOrdersTableProps) {
  const displayEvents = events.slice(0, 5);

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] h-full flex flex-col justify-between hover:border-slate-200 transition-all">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold text-slate-800">Recent Ingested Events</h3>
        <button
          onClick={onRefresh}
          className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          title="Refresh"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="text-[11px] font-semibold text-slate-400 border-b border-slate-100">
              <th className="pb-2.5 font-medium">Source</th>
              <th className="pb-2.5 font-medium">Origin IP</th>
              <th className="pb-2.5 font-medium">Timestamp</th>
              <th className="pb-2.5 font-medium">Status</th>
              <th className="pb-2.5 text-right font-medium">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {displayEvents.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-8 text-center text-slate-400 font-sans">
                  No events ingested yet.
                </td>
              </tr>
            ) : (
              displayEvents.map((ev) => {
                const vendor = ev.source.vendor || "Generic";
                const avatarStyle =
                  VENDOR_AVATAR_COLORS[vendor] || "bg-slate-100 text-slate-700";

                return (
                  <tr key={ev.event_id} className="hover:bg-slate-50/70 transition-colors">
                    {/* Profile / Source with Avatar */}
                    <td className="py-3">
                      <div className="flex items-center gap-2.5">
                        <div
                          className={`h-7 w-7 rounded-full flex items-center justify-center font-bold text-[10px] uppercase shrink-0 ${avatarStyle}`}
                        >
                          {vendor.slice(0, 2)}
                        </div>
                        <div className="font-semibold text-slate-800 text-xs">
                          {vendor}
                        </div>
                      </div>
                    </td>

                    {/* Address / Origin IP */}
                    <td className="py-3 text-slate-600 font-mono text-[11px]">
                      {ev.network.source_ip || "Internal"}
                    </td>

                    {/* Date */}
                    <td className="py-3 text-slate-400 font-mono text-[11px]">
                      {ev.timestamp ? ev.timestamp.slice(5, 10).replace("-", ".") : "Today"}
                    </td>

                    {/* Status Badge matching reference */}
                    <td className="py-3">
                      {ev.event.action === "ALLOW" ? (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-emerald-50 text-emerald-700">
                          Allowed
                        </span>
                      ) : ev.event.action === "DENY" || ev.event.action === "BLOCK" ? (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-rose-50 text-rose-700">
                          Blocked
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-medium bg-amber-50 text-amber-700">
                          Processed
                        </span>
                      )}
                    </td>

                    {/* Price / Inspect button */}
                    <td className="py-3 text-right">
                      <Link
                        href={`/logs/${ev.event_id}`}
                        className="text-blue-600 hover:text-blue-700 font-semibold text-[11px] hover:underline inline-flex items-center gap-0.5"
                      >
                        <span>Inspect</span>
                        <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer link to Explorer */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-end">
        <Link
          href="/logs"
          className="text-xs text-slate-500 hover:text-blue-600 font-medium transition-colors"
        >
          View all events →
        </Link>
      </div>
    </div>
  );
}
