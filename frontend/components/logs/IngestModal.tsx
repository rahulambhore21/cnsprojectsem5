"use client";

import { useState } from "react";
import { X, Upload, Play, CheckCircle2, AlertTriangle } from "lucide-react";
import { api } from "@/lib/api";
import { UniversalEvent } from "@/lib/types";
import Link from "next/link";

interface IngestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function IngestModal({ isOpen, onClose, onSuccess }: IngestModalProps) {
  const [tab, setTab] = useState<"paste" | "upload">("paste");
  const [rawLog, setRawLog] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    event?: UniversalEvent;
    total_lines?: number;
    processed_count?: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleProcessText = async () => {
    if (!rawLog.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.processEvent(rawLog.trim());
      if (res.success) {
        setResult({ success: true, message: res.message, event: res.event });
        if (onSuccess) onSuccess();
      } else {
        setError(res.message || "Failed to process log.");
      }
    } catch (err: any) {
      setError(err.message || "Network or parser error.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await api.uploadLogFile(file);
      setResult({
        success: true,
        message: `Successfully processed ${res.processed_count} of ${res.total_lines} lines.`,
        total_lines: res.total_lines,
        processed_count: res.processed_count,
        event: res.processed_events?.[0],
      });
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setError(err.message || "Failed to upload log file.");
    } finally {
      setLoading(false);
    }
  };

  const handleSampleSelect = (sample: string) => {
    setRawLog(sample);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4">
      <div className="bg-white border border-slate-200 rounded-3xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-7 py-5 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center border border-blue-100">
              <Play className="h-4 w-4 fill-current" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Pre-process Raw Log</h2>
              <p className="text-xs text-slate-500 font-medium">Detect format, normalize to universal schema, and verify hash</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-700 p-1.5 rounded-xl hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="flex border-b border-slate-100 bg-slate-50/70 px-7 pt-2">
          <button
            onClick={() => { setTab("paste"); setResult(null); setError(null); }}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition-colors ${
              tab === "paste"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Paste Raw Log
          </button>
          <button
            onClick={() => { setTab("upload"); setResult(null); setError(null); }}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition-colors ${
              tab === "upload"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            Upload File (.log / .txt / .json)
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-7 overflow-y-auto space-y-4 flex-1">
          {tab === "paste" ? (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-700">Raw Log Payload</label>
                <div className="flex items-center gap-1.5">
                  <span className="text-[11px] text-slate-400 font-medium">Sample:</span>
                  <button
                    onClick={() => handleSampleSelect('%ASA-4-106023: Deny tcp src inside:192.168.1.10/49221 dst outside:8.8.8.8/443 by access-group "acl_out"')}
                    className="text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium"
                  >
                    Cisco
                  </button>
                  <button
                    onClick={() => handleSampleSelect('date=2026-10-06 time=10:31:22 devname=FG100D srcip=192.168.1.10 srcport=49221 dstip=8.8.8.8 dstport=443 proto=6 action=deny')}
                    className="text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium"
                  >
                    Fortinet
                  </button>
                  <button
                    onClick={() => handleSampleSelect('{"timestamp": "2026-10-06T10:31:22Z", "src_ip": "192.168.1.10", "dst_ip": "8.8.8.8", "protocol": "TCP", "action": "DENY"}')}
                    className="text-[11px] px-2.5 py-0.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 font-medium"
                  >
                    JSON
                  </button>
                </div>
              </div>
              <textarea
                value={rawLog}
                onChange={(e) => setRawLog(e.target.value)}
                placeholder="Paste raw log here (e.g. %ASA-4-106023: Deny tcp..., CEF:0|..., JSON...)"
                rows={5}
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-mono text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
              />
            </div>
          ) : (
            <div>
              <label className="text-xs font-bold text-slate-700 mb-2 block">Select Log File</label>
              <div className="border-2 border-dashed border-slate-200 hover:border-slate-300 rounded-2xl p-8 text-center bg-slate-50/50">
                <Upload className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                <p className="text-xs text-slate-700 font-semibold">Click to upload or drag and drop</p>
                <p className="text-[11px] text-slate-400 mt-1">.log, .txt, .json or .csv up to 10MB</p>
                <input
                  type="file"
                  accept=".log,.txt,.json,.csv"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="mt-3 text-xs text-slate-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer font-medium"
                />
              </div>
            </div>
          )}

          {/* Feedback & Error */}
          {error && (
            <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-start gap-2.5">
              <AlertTriangle className="h-4 w-4 shrink-0 text-red-600 mt-0.5" />
              <div>
                <p className="font-bold">Processing Failed</p>
                <p className="text-[11px] text-red-600 mt-0.5">{error}</p>
                {error.includes("UNKNOWN") && (
                  <Link
                    href="/parser-studio"
                    onClick={onClose}
                    className="inline-block mt-2 text-[11px] text-blue-600 hover:underline font-bold"
                  >
                    Onboard this custom format in AI Parser Studio →
                  </Link>
                )}
              </div>
            </div>
          )}

          {result && (
            <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                <span className="font-bold">{result.message}</span>
              </div>
              {result.event && (
                <div className="bg-white p-3.5 rounded-xl border border-emerald-200 font-mono text-[11px] space-y-1 text-slate-700 shadow-xs">
                  <div><strong>Event ID:</strong> {result.event.event_id}</div>
                  <div><strong>Vendor:</strong> {result.event.source.vendor} ({result.event.processing.parser})</div>
                  <div><strong>Network:</strong> {result.event.network.source_ip}:{result.event.network.source_port} → {result.event.network.destination_ip}:{result.event.network.destination_port}</div>
                  <div><strong>Action:</strong> <span className={result.event.event.action === "DENY" ? "text-rose-600 font-bold" : "text-emerald-600 font-bold"}>{result.event.event.action}</span></div>
                  <div><strong>SHA-256:</strong> <span className="text-slate-500 font-semibold">{result.event.integrity.sha256.slice(0, 24)}... (Verified ✓)</span></div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-7 py-4 border-t border-slate-100 bg-slate-50/50 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200/80 transition-colors"
          >
            Close
          </button>
          <button
            onClick={tab === "paste" ? handleProcessText : handleFileUpload}
            disabled={loading || (tab === "paste" && !rawLog.trim()) || (tab === "upload" && !file)}
            className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm"
          >
            {loading ? "Processing Pipeline..." : "Pre-process & Store"}
          </button>
        </div>
      </div>
    </div>
  );
}
