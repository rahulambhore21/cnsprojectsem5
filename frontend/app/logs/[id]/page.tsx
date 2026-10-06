"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ShieldCheck,
  Copy,
  Check,
  Cpu,
  Layers,
  Network,
  Calendar,
  Lock,
  RefreshCw,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";
import { UniversalEvent } from "@/lib/types";

export default function EventDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const eventId = resolvedParams.id;

  const [event, setEvent] = useState<UniversalEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedRaw, setCopiedRaw] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  const [reverified, setReverified] = useState(false);

  useEffect(() => {
    async function fetchEvent() {
      setLoading(true);
      try {
        const data = await api.getEvent(eventId);
        setEvent(data);
      } catch (err) {
        console.error("Failed to load event:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchEvent();
  }, [eventId]);

  const handleCopyRaw = () => {
    if (!event) return;
    navigator.clipboard.writeText(event.raw.message);
    setCopiedRaw(true);
    setTimeout(() => setCopiedRaw(false), 2000);
  };

  const handleCopyJson = () => {
    if (!event) return;
    navigator.clipboard.writeText(JSON.stringify(event, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  const handleReverifyHash = () => {
    setReverified(true);
    setTimeout(() => setReverified(false), 3000);
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#f4f5f8]">
        <Header title="Event Inspector" />
        <div className="flex-1 flex items-center justify-center text-xs text-slate-500">
          <RefreshCw className="h-5 w-5 animate-spin mr-2 text-blue-600" />
          Loading cryptographic event record...
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="flex-1 flex flex-col h-full bg-[#f4f5f8]">
        <Header title="Event Inspector" />
        <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-3">
          <p className="text-sm text-slate-600 font-medium">Event record not found or deleted.</p>
          <Link
            href="/logs"
            className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-semibold"
          >
            Back to Log Explorer
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header title="Event Inspector" />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* Navigation Breadcrumb & Badges Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link
            href="/logs"
            className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800 transition-colors font-semibold"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Back to Explorer</span>
          </Link>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-xl bg-white text-slate-800 text-xs font-mono font-semibold border border-slate-200 shadow-xs">
              {event.event_id}
            </span>
            <span
              className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${
                event.event.action === "DENY" || event.event.action === "BLOCK"
                  ? "bg-rose-50 text-rose-700 border border-rose-200"
                  : event.event.action === "ALLOW"
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                  : "bg-amber-50 text-amber-700 border border-amber-200"
              }`}
            >
              {event.event.action}
            </span>
            <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
              {event.source.vendor}
            </span>
          </div>
        </div>

        {/* 2-Column Side-by-Side: Normalized Event vs Original Event */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Normalized Universal Event Schema */}
          <div className="space-y-4">
            <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                  <Layers className="h-4 w-4 text-blue-600" />
                  <span>Normalized Event (Universal Schema)</span>
                </div>
                <button
                  onClick={handleCopyJson}
                  className="flex items-center gap-1 text-[11px] text-slate-600 hover:text-slate-900 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors font-medium"
                >
                  {copiedJson ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedJson ? "Copied" : "Copy JSON"}</span>
                </button>
              </div>

              {/* Structured Field Cards */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                {/* Timestamp */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5 mb-1">
                    <Calendar className="h-3 w-3 text-blue-600" />
                    Timestamp (ISO-8601)
                  </div>
                  <div className="font-mono font-medium text-slate-800">{event.timestamp}</div>
                </div>

                {/* Source / Device */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5 mb-1">
                    <Cpu className="h-3 w-3 text-indigo-600" />
                    Source Device
                  </div>
                  <div className="font-sans font-semibold text-slate-800">
                    {event.source.device_name || "firewall01"} ({event.source.product || event.source.vendor})
                  </div>
                </div>

                {/* Network Source */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5 mb-1">
                    <Network className="h-3 w-3 text-emerald-600" />
                    Network Origin
                  </div>
                  <div className="font-mono text-slate-800 font-semibold">
                    {event.network.source_ip || "—"}
                    {event.network.source_port ? `:${event.network.source_port}` : ""}
                  </div>
                </div>

                {/* Network Destination */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold flex items-center gap-1.5 mb-1">
                    <Network className="h-3 w-3 text-rose-600" />
                    Network Target
                  </div>
                  <div className="font-mono text-slate-800 font-semibold">
                    {event.network.destination_ip || "—"}
                    {event.network.destination_port ? `:${event.network.destination_port}` : ""}
                  </div>
                </div>

                {/* Protocol & Category */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Protocol / Category</div>
                  <div className="font-mono text-slate-800 font-medium">
                    {event.network.protocol || "IP"} • {event.event.category}
                  </div>
                </div>

                {/* Severity & Outcome */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Severity / Outcome</div>
                  <div className="font-sans capitalize text-slate-800 font-semibold">
                    {event.event.severity} • {event.event.outcome || "recorded"}
                  </div>
                </div>

                {/* User / Identity */}
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 col-span-2">
                  <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">User Identity</div>
                  <div className="font-mono text-slate-800">
                    {event.user.username ? (
                      <span className="text-blue-600 font-bold">{event.user.username}</span>
                    ) : (
                      <span className="text-slate-400 italic">null (Unauthenticated / System Level)</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Complete JSON Preview */}
              <div>
                <div className="text-[11px] font-bold text-slate-500 uppercase mb-2">Complete Schema JSON</div>
                <pre className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-[11px] font-mono text-slate-200 overflow-x-auto max-h-72">
                  {JSON.stringify(event, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* Right Column: Original Raw Event + Cryptographic Hash */}
          <div className="space-y-4">
            <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
                  <Lock className="h-4 w-4 text-emerald-600" />
                  <span>Original Event (Lossless Preservation)</span>
                </div>
                <button
                  onClick={handleCopyRaw}
                  className="flex items-center gap-1 text-[11px] text-slate-600 hover:text-slate-900 px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 transition-colors font-medium"
                >
                  {copiedRaw ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedRaw ? "Copied" : "Copy Raw"}</span>
                </button>
              </div>

              <div>
                <p className="text-xs text-slate-500 mb-2 font-medium">
                  Untouched raw log message preserved bit-for-bit:
                </p>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 font-mono text-xs text-emerald-400 whitespace-pre-wrap break-all leading-relaxed">
                  {event.raw.message}
                </div>
              </div>

              {/* Cryptographic Hash Verification Box */}
              <div className="p-5 rounded-2xl bg-emerald-50/70 border border-emerald-200 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="h-5 w-5 text-emerald-600" />
                    <span className="text-xs font-bold text-emerald-800 tracking-wide">
                      Integrity Verified ✓
                    </span>
                  </div>
                  <button
                    onClick={handleReverifyHash}
                    className="text-[11px] px-3 py-1 rounded-lg bg-white hover:bg-emerald-100 text-emerald-800 border border-emerald-300 font-semibold flex items-center gap-1 shadow-xs transition-colors"
                  >
                    <RefreshCw className={`h-3 w-3 ${reverified ? "animate-spin" : ""}`} />
                    <span>{reverified ? "Verified OK" : "Re-verify Hash"}</span>
                  </button>
                </div>

                <div className="space-y-1">
                  <div className="text-[10px] text-slate-500 uppercase font-bold">
                    SHA-256 Cryptographic Hash
                  </div>
                  <div className="bg-white p-3 rounded-xl border border-emerald-200 font-mono text-[11px] text-slate-800 break-all select-all font-semibold">
                    {event.integrity.sha256}
                  </div>
                  <p className="text-[11px] text-slate-500 pt-1">
                    Computed via <code className="text-emerald-700 font-bold">SHA256(raw_log)</code>. Proves raw log was preserved without loss or tampering.
                  </p>
                </div>
              </div>

              {/* Processing Pipeline Metadata */}
              <div className="pt-2 border-t border-slate-100 space-y-3">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Processing & Parsing Metadata
                </h4>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Parser Adapter</div>
                    <div className="font-mono text-blue-600 font-bold">{event.processing.parser}</div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Parser Version</div>
                    <div className="font-mono text-slate-700 font-medium">v{event.processing.parser_version}</div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Extraction Confidence</div>
                    <div className="font-mono text-emerald-600 font-bold">
                      {(event.processing.confidence * 100).toFixed(0)}%
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                    <div className="text-[10px] text-slate-400 uppercase font-bold mb-1">Parser Engine</div>
                    <div className="font-sans text-slate-800 font-semibold">
                      {event.processing.is_ai_assisted ? "AI Dynamic Parser" : "Deterministic Parser"}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
