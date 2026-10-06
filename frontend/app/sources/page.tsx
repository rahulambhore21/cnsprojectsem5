"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Database,
  Radio,
  ArrowRight,
  Shield,
  Activity,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";
import { SourceItem } from "@/lib/types";
import Link from "next/link";

export default function SourcesPage() {
  const [sources, setSources] = useState<SourceItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSources = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getSources();
      setSources(res.sources);
    } catch (err) {
      console.error("Failed to load sources:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadSources();
  }, [loadSources]);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header
        title="Data Sources"
        onRefresh={loadSources}
      />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* Source Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-center justify-between">
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400">Total Sources</span>
              <div className="text-2xl font-bold font-sans text-slate-900 mt-1">{sources.length}</div>
            </div>
            <div className="p-3 rounded-xl bg-blue-50 text-blue-600">
              <Database className="h-5 w-5" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-center justify-between">
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400">Active Telemetry</span>
              <div className="text-2xl font-bold font-sans text-emerald-600 mt-1">
                {sources.filter((s) => s.status === "active").length}
              </div>
            </div>
            <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600">
              <Radio className="h-5 w-5" />
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-center justify-between">
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400">Ingested Volume</span>
              <div className="text-2xl font-bold font-sans text-purple-600 mt-1">
                {sources.reduce((acc, s) => acc + s.event_count, 0).toLocaleString()}
              </div>
            </div>
            <div className="p-3 rounded-xl bg-purple-50 text-purple-600">
              <Activity className="h-5 w-5" />
            </div>
          </div>
        </div>

        {/* Sources Table Card */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Device & Vendor Registry</h3>
              <p className="text-xs text-slate-500 mt-0.5">All network appliances and agents streaming telemetry into ULPF</p>
            </div>
          </div>

          <div className="overflow-x-auto border border-slate-100 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-3 px-4">Source ID</th>
                  <th className="py-3 px-4">Vendor / Appliance</th>
                  <th className="py-3 px-4">Log Format</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Events Ingested</th>
                  <th className="py-3 px-4">Last Seen</th>
                  <th className="py-3 px-4 text-right">View Logs</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {sources.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-12 text-center text-slate-400 font-sans">
                      No active sources detected. Click &quot;Seed Demo&quot; to initialize sample sources.
                    </td>
                  </tr>
                ) : (
                  sources.map((s) => (
                    <tr key={s.source_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 text-slate-500 text-[11px]">{s.source_id}</td>
                      <td className="py-3 px-4 font-sans font-bold text-slate-800 flex items-center gap-2">
                        <Shield className="h-4 w-4 text-blue-600" />
                        <span>{s.vendor}</span>
                      </td>
                      <td className="py-3 px-4 uppercase text-[11px] text-slate-600">
                        <span className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200/80 font-medium">
                          {s.format}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-sans">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700">
                          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                          <span>Active</span>
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-900 font-bold font-sans">
                        {s.event_count.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-slate-500 text-[11px]">
                        {s.last_seen ? s.last_seen.replace("T", " ").slice(0, 19) : "Just now"}
                      </td>
                      <td className="py-3 px-4 text-right font-sans">
                        <Link
                          href={`/logs?vendor=${encodeURIComponent(s.vendor)}`}
                          className="px-3 py-1 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 text-xs font-semibold transition-colors inline-flex items-center gap-1"
                        >
                          <span>Explore</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
