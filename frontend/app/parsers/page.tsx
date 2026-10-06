"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Layers,
  Cpu,
  CheckCircle2,
  FileCode,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";
import { ParserItem } from "@/lib/types";
import Link from "next/link";

export default function ParsersPage() {
  const [parsers, setParsers] = useState<ParserItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedParser, setSelectedParser] = useState<ParserItem | null>(null);

  const loadParsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getParsers();
      setParsers(res.parsers);
    } catch (err) {
      console.error("Failed to load parsers:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadParsers();
  }, [loadParsers]);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header
        title="Parser Rules"
        onRefresh={loadParsers}
      />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* Quick Actions & Metrics Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)]">
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="h-4 w-4 text-blue-600" />
              <span>Registered Schema Adapters ({parsers.length})</span>
            </h3>
            <p className="text-xs text-slate-500">
              Deterministic parsers execute first with high throughput; custom dynamic parsers process newly onboarded formats.
            </p>
          </div>

          <Link
            href="/parser-studio"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Onboard New Format</span>
          </Link>
        </div>

        {/* Parsers Table */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="overflow-x-auto border border-slate-100 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-3 px-4">Parser Name</th>
                  <th className="py-3 px-4">Target Vendor</th>
                  <th className="py-3 px-4">Log Format</th>
                  <th className="py-3 px-4">Engine Type</th>
                  <th className="py-3 px-4">Version</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono">
                {parsers.map((p) => (
                  <tr key={p.parser_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-sans font-bold text-slate-800 flex items-center gap-2">
                      <FileCode className={`h-4 w-4 ${p.is_builtin ? "text-blue-600" : "text-purple-600"}`} />
                      <span>{p.name}</span>
                    </td>
                    <td className="py-3 px-4 font-sans text-slate-600 font-medium">
                      {p.vendor}
                    </td>
                    <td className="py-3 px-4 uppercase text-[11px] text-slate-600">
                      <span className="px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200/80 font-medium">
                        {p.format}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-sans">
                      {p.is_builtin ? (
                        <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 text-[11px] font-semibold">
                          Built-in Deterministic
                        </span>
                      ) : (
                        <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 text-[11px] font-semibold flex items-center gap-1 w-fit">
                          <Cpu className="h-3 w-3" />
                          <span>AI-Generated</span>
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-500 text-[11px]">v{p.version}</td>
                    <td className="py-3 px-4 font-sans">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700">
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                        <span>Active</span>
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-sans">
                      <button
                        onClick={() => setSelectedParser(p)}
                        className="px-3 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                      >
                        Inspect Rules
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Parser Detail Modal */}
        {selectedParser && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
            <div className="bg-white border border-slate-200 rounded-2xl w-full max-w-xl p-6 space-y-4 shadow-2xl">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-5 w-5 text-blue-600" />
                  <h3 className="text-base font-bold text-slate-900">{selectedParser.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedParser(null)}
                  className="text-slate-400 hover:text-slate-700 text-xs px-2.5 py-1 rounded-lg bg-slate-100 font-semibold"
                >
                  Close
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Vendor</span>
                  <span className="text-slate-900 font-bold">{selectedParser.vendor}</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Format</span>
                  <span className="text-slate-900 font-mono uppercase font-bold">{selectedParser.format}</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-slate-800 block mb-2">
                  {selectedParser.is_builtin ? "Deterministic Normalization Profile" : "User-Approved Schema Mappings"}
                </span>
                {selectedParser.mapping && Object.keys(selectedParser.mapping).length > 0 ? (
                  <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 overflow-x-auto max-h-56">
                    <table className="w-full text-left font-mono text-[11px]">
                      <thead>
                        <tr className="text-slate-400 border-b border-slate-200 font-bold">
                          <th className="pb-1.5">Source Key</th>
                          <th className="pb-1.5">Universal Schema Field</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200/80">
                        {Object.entries(selectedParser.mapping).map(([k, v]) => (
                          <tr key={k}>
                            <td className="py-1 text-purple-700 font-semibold">{k}</td>
                            <td className="py-1 text-blue-700 font-semibold">{v}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-100 leading-relaxed">
                    Compiled Python deterministic parser class. Maps raw syntax directly into Pydantic UniversalEvent structure with strict validation.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
