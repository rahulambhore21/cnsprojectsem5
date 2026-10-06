"use client";

import { useState, useEffect } from "react";
import {
  Sparkles,
  Database,
  CheckCircle2,
  Copy,
  Check,
  Server,
  BookOpen,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [seeding, setSeeding] = useState(false);
  const [seedStatus, setSeedStatus] = useState<string | null>(null);
  const [samples, setSamples] = useState<Record<string, string[]>>({});
  const [health, setHealth] = useState<any>(null);
  const [copiedIndex, setCopiedIndex] = useState<string | null>(null);

  useEffect(() => {
    loadInfo();
  }, []);

  const loadInfo = async () => {
    try {
      const [healthData, samplesData] = await Promise.allSettled([
        api.getHealth(),
        api.getSampleLogs(),
      ]);
      if (healthData.status === "fulfilled") setHealth(healthData.value);
      if (samplesData.status === "fulfilled") setSamples(samplesData.value);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setSeedStatus(null);
    try {
      const res = await api.seedDemoData();
      if (res.success) {
        setSeedStatus(`Successfully seeded ${res.seeded_count} realistic events across ${res.vendors.join(", ")}.`);
      }
    } catch (err: any) {
      alert("Failed to seed data: " + err.message);
    } finally {
      setSeeding(false);
    }
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(id);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header title="Settings & SIH Guide" />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* SIH 2-Minute Presentation Guide Banner */}
        <div className="p-6 rounded-2xl bg-white border border-blue-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex items-center gap-2.5 text-slate-900 font-bold text-sm">
            <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
              <BookOpen className="h-5 w-5" />
            </div>
            <span>SIH 2026 Live Demonstration Flow (NTRO Problem Statement SIH26156)</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            Follow this step-by-step walkthrough during your evaluation to showcase full conformance with SIH requirements:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs pt-1">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-blue-700 font-bold block mb-1">Step 1: Dashboard</span>
              <p className="text-[11px] text-slate-600 font-medium">
                Show live MongoDB counts: Total Events, Blocked, Threats, and multi-vendor distribution.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-emerald-700 font-bold block mb-1">Step 2: Log Explorer</span>
              <p className="text-[11px] text-slate-600 font-medium">
                Filter by Cisco or Fortinet. Open an event to show lossless preservation and SHA-256 integrity.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-purple-700 font-bold block mb-1">Step 3: AI Parser Studio</span>
              <p className="text-[11px] text-slate-600 font-medium">
                Paste an unknown custom log, click &quot;Analyze with AI&quot;, review extracted mappings, and approve.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-amber-700 font-bold block mb-1">Step 4: Dynamic Parse</span>
              <p className="text-[11px] text-slate-600 font-medium">
                Feed a second log into the pipeline and observe dynamic parsing by the newly approved custom parser.
              </p>
            </div>
          </div>
        </div>

        {/* Demo Data Management */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Database className="h-4 w-4 text-purple-600" />
                <span>Demo Data Management</span>
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Populate or reset MongoDB with 55+ realistic security logs across all required formats.
              </p>
            </div>

            <button
              onClick={handleSeed}
              disabled={seeding}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold shadow-sm disabled:opacity-50 transition-all"
            >
              <Sparkles className="h-4 w-4" />
              <span>{seeding ? "Populating Database..." : "Load Demo Data (One-Click)"}</span>
            </button>
          </div>

          {seedStatus && (
            <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2 font-medium">
              <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0" />
              <span>{seedStatus}</span>
            </div>
          )}
        </div>

        {/* System & Architecture Status */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Server className="h-4 w-4 text-blue-600" />
            <span>Infrastructure Health & Tech Stack</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Backend Core</span>
              <span className="text-slate-800 font-mono font-bold">FastAPI 0.136 + Python 3.13 (Port 8000)</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">Database</span>
              <span className="text-emerald-700 font-mono font-bold">
                MongoDB ({health?.database?.status || "Connected on :27017"})
              </span>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">AI Engine</span>
              <span className="text-purple-700 font-mono font-bold">
                OpenAI Structured Output + Local Heuristic Fallback
              </span>
            </div>
          </div>
        </div>

        {/* Interactive Sample Log Library */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Sample Log Library (Quick Copy)</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Click any sample below to copy to clipboard for testing in Log Ingest or AI Parser Studio.
            </p>
          </div>

          <div className="space-y-4">
            {Object.entries(samples).map(([category, logs]) => (
              <div key={category} className="space-y-2">
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                  {category} Logs ({logs.length})
                </span>
                <div className="space-y-1.5 font-mono text-[11px]">
                  {logs.slice(0, 2).map((log, idx) => {
                    const id = `${category}-${idx}`;
                    return (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between gap-3 hover:border-slate-300 transition-colors"
                      >
                        <span className="text-slate-700 truncate">{log}</span>
                        <button
                          onClick={() => copyToClipboard(log, id)}
                          className="shrink-0 text-slate-400 hover:text-slate-800 p-1 rounded-lg hover:bg-slate-200 transition-colors"
                          title="Copy payload"
                        >
                          {copiedIndex === id ? (
                            <Check className="h-3.5 w-3.5 text-emerald-600" />
                          ) : (
                            <Copy className="h-3.5 w-3.5" />
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
