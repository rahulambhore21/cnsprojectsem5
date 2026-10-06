"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Search,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  RotateCcw,
  ArrowRight,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";
import { UniversalEvent } from "@/lib/types";

export default function LogExplorerPage() {
  const [events, setEvents] = useState<UniversalEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState("");
  const [vendor, setVendor] = useState("all");
  const [format, setFormat] = useState("all");
  const [action, setAction] = useState("all");
  const [severity, setSeverity] = useState("all");
  const [sourceIp, setSourceIp] = useState("");
  const [destinationIp, setDestinationIp] = useState("");

  const loadEvents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getEvents({
        q: search.trim() || undefined,
        vendor: vendor !== "all" ? vendor : undefined,
        format: format !== "all" ? format : undefined,
        action: action !== "all" ? action : undefined,
        severity: severity !== "all" ? severity : undefined,
        source_ip: sourceIp.trim() || undefined,
        destination_ip: destinationIp.trim() || undefined,
        page,
        limit: 15,
      });
      setEvents(res.events);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  }, [search, vendor, format, action, severity, sourceIp, destinationIp, page]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const handleResetFilters = () => {
    setSearch("");
    setVendor("all");
    setFormat("all");
    setAction("all");
    setSeverity("all");
    setSourceIp("");
    setDestinationIp("");
    setPage(1);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header
        title="Log Explorer"
        onRefresh={loadEvents}
      />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-5">
        {/* Filter Controls Card matching white rounded card theme */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex flex-col md:flex-row items-center gap-3">
            {/* Search Input */}
            <div className="relative flex-1 w-full">
              <Search className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search raw payload, IPs, usernames, device names, event ID..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200/80 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all font-mono"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto">
              <button
                onClick={handleResetFilters}
                className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 text-xs font-semibold transition-colors"
                title="Reset all filters"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Reset</span>
              </button>

              <button
                onClick={loadEvents}
                className="flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
                <span>Search</span>
              </button>
            </div>
          </div>

          {/* Secondary Filters Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 pt-2 border-t border-slate-100">
            {/* Vendor Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Vendor</label>
              <select
                value={vendor}
                onChange={(e) => { setVendor(e.target.value); setPage(1); }}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="all">All Vendors</option>
                <option value="Cisco">Cisco</option>
                <option value="Fortinet">Fortinet</option>
                <option value="Palo Alto">Palo Alto</option>
                <option value="Generic">Generic</option>
                <option value="Suricata">Suricata</option>
                <option value="AWS">AWS</option>
                <option value="Custom">Custom / AI</option>
              </select>
            </div>

            {/* Format Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Format</label>
              <select
                value={format}
                onChange={(e) => { setFormat(e.target.value); setPage(1); }}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="all">All Formats</option>
                <option value="syslog">Syslog</option>
                <option value="kv">Key-Value</option>
                <option value="csv">CSV (PAN-OS)</option>
                <option value="json">JSON</option>
                <option value="cef">CEF</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            {/* Action Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Action</label>
              <select
                value={action}
                onChange={(e) => { setAction(e.target.value); setPage(1); }}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="all">All Actions</option>
                <option value="ALLOW">ALLOW / PASS</option>
                <option value="DENY">DENY / BLOCK</option>
                <option value="CLOSE">CLOSE</option>
                <option value="ALERT">ALERT</option>
              </select>
            </div>

            {/* Severity Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Severity</label>
              <select
                value={severity}
                onChange={(e) => { setSeverity(e.target.value); setPage(1); }}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="all">All Severities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            {/* Source IP Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Source IP</label>
              <input
                type="text"
                value={sourceIp}
                onChange={(e) => { setSourceIp(e.target.value); setPage(1); }}
                placeholder="e.g. 192.168.1"
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-mono focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Destination IP Filter */}
            <div>
              <label className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Destination IP</label>
              <input
                type="text"
                value={destinationIp}
                onChange={(e) => { setDestinationIp(e.target.value); setPage(1); }}
                placeholder="e.g. 8.8.8.8"
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs text-slate-700 font-mono focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Results Card & Table */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <div>
              Found <strong className="text-slate-900 font-mono">{total.toLocaleString()}</strong> normalized events
            </div>
            <div className="flex items-center gap-2">
              <span>Page {page} of {pages || 1}</span>
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <button
                disabled={page >= pages || loading}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto border border-slate-100 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Vendor</th>
                  <th className="py-3 px-4">Category / Type</th>
                  <th className="py-3 px-4">Origin → Destination</th>
                  <th className="py-3 px-4">Proto</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Parser</th>
                  <th className="py-3 px-4">Integrity</th>
                  <th className="py-3 px-4 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {events.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="py-12 text-center text-slate-400 font-sans">
                      No logs found matching your filters.
                    </td>
                  </tr>
                ) : (
                  events.map((ev) => (
                    <tr key={ev.event_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 text-slate-500 truncate max-w-[150px]">
                        {ev.timestamp.replace("T", " ").replace("Z", "")}
                      </td>
                      <td className="py-3 px-4 font-sans font-semibold text-slate-800">
                        {ev.source.vendor || "Generic"}
                      </td>
                      <td className="py-3 px-4 font-sans text-slate-500 capitalize">
                        {ev.event.category}/{ev.event.type}
                      </td>
                      <td className="py-3 px-4 text-slate-700">
                        {ev.network.source_ip ? (
                          <span>
                            {ev.network.source_ip}{ev.network.source_port ? `:${ev.network.source_port}` : ""}
                            {" → "}
                            {ev.network.destination_ip}{ev.network.destination_port ? `:${ev.network.destination_port}` : ""}
                          </span>
                        ) : (
                          <span className="text-slate-400 italic font-sans">—</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-slate-500">
                        {ev.network.protocol || "—"}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        {ev.event.action === "ALLOW" ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700">
                            ALLOW
                          </span>
                        ) : ev.event.action === "DENY" || ev.event.action === "BLOCK" ? (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-700">
                            DENY
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 text-amber-700">
                            {ev.event.action}
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-sans capitalize">
                        <span
                          className={`text-[11px] font-medium ${
                            ev.event.severity === "critical"
                              ? "text-rose-600 font-bold"
                              : ev.event.severity === "high"
                              ? "text-orange-600 font-semibold"
                              : ev.event.severity === "medium"
                              ? "text-amber-600"
                              : "text-blue-600"
                          }`}
                        >
                          {ev.event.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-500 text-[11px]">
                        {ev.processing.parser}
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                          <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                          <span>SHA-256 ✓</span>
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-sans">
                        <Link
                          href={`/logs/${ev.event_id}`}
                          className="px-3 py-1 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 text-xs font-semibold transition-colors inline-flex items-center gap-1"
                        >
                          <span>Inspect</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Bottom Pagination */}
          <div className="flex items-center justify-between text-xs text-slate-500 pt-2">
            <div>
              Showing {events.length} of {total.toLocaleString()} total events
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1 || loading}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
              >
                Previous
              </button>
              <span className="text-slate-800 font-semibold font-mono">
                {page} / {pages || 1}
              </span>
              <button
                disabled={page >= pages || loading}
                onClick={() => setPage((p) => p + 1)}
                className="px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 disabled:opacity-40 disabled:cursor-not-allowed font-medium"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
