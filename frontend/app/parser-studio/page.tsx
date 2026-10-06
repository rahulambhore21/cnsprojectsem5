"use client";

import { useState } from "react";
import {
  Cpu,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Save,
  Trash2,
  Plus,
  Play,
  RotateCcw,
  Check,
} from "lucide-react";
import Header from "@/components/layout/Header";
import { api } from "@/lib/api";
import { AIAnalysisResponse, AIFieldMapping, UniversalEvent } from "@/lib/types";

const TARGET_SCHEMA_OPTIONS = [
  { value: "network.source_ip", label: "network.source_ip" },
  { value: "network.source_port", label: "network.source_port" },
  { value: "network.destination_ip", label: "network.destination_ip" },
  { value: "network.destination_port", label: "network.destination_port" },
  { value: "network.protocol", label: "network.protocol" },
  { value: "event.action", label: "event.action" },
  { value: "event.severity", label: "event.severity" },
  { value: "event.type", label: "event.type" },
  { value: "event.category", label: "event.category" },
  { value: "source.device_name", label: "source.device_name" },
  { value: "source.vendor", label: "source.vendor" },
  { value: "user.username", label: "user.username" },
  { value: "timestamp", label: "timestamp" },
];

const SAMPLE_UNKNOWN_LOGS = [
  {
    name: "Custom Firewall Event",
    log: "2026-10-06 11:20:31 FW01 source=10.10.1.20 destination=172.16.0.10 protocol=tcp port=443 decision=blocked level=high user=guest",
  },
  {
    name: "Custom Proxy Access Log",
    log: "PROXY-EDGE-02 client=192.168.100.55 server=198.51.100.44 proto=tcp sport=54321 dport=8080 action=blocked severity=critical alert=TorExitNode",
  },
  {
    name: "Custom Router Telemetry",
    log: "SEC-ROUTER-9 src_ip=172.16.2.99 dst_ip=192.168.1.1 protocol=icmp decision=denied level=medium rule=ICMP-Ping-Block",
  },
];

export default function AIParserStudioPage() {
  const [rawLog, setRawLog] = useState(SAMPLE_UNKNOWN_LOGS[0].log);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<AIAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Editable mappings & metadata
  const [mappings, setMappings] = useState<AIFieldMapping[]>([]);
  const [parserName, setParserName] = useState("");
  const [vendorName, setVendorName] = useState("");
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState<string | null>(null);

  // Testing newly created parser
  const [testLog, setTestLog] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<UniversalEvent | null>(null);

  const handleAnalyze = async () => {
    if (!rawLog.trim()) return;
    setAnalyzing(true);
    setError(null);
    setAnalysis(null);
    setSavedSuccess(null);
    setTestResult(null);

    try {
      const res = await api.analyzeWithAI(rawLog.trim());
      setAnalysis(res);
      setMappings(res.mappings);
      setParserName(`${res.detected_vendor} Custom Parser`);
      setVendorName(res.detected_vendor);
    } catch (err: any) {
      setError(err.message || "Failed to analyze log with AI.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleUpdateMapping = (index: number, newTarget: string) => {
    const updated = [...mappings];
    updated[index].target_field = newTarget;
    setMappings(updated);
  };

  const handleRemoveMapping = (index: number) => {
    setMappings(mappings.filter((_, i) => i !== index));
  };

  const handleAddMapping = () => {
    setMappings([
      ...mappings,
      {
        source_field: "custom_field",
        target_field: "network.source_ip",
        confidence: 0.85,
        sample_value: "",
        description: "User defined custom mapping",
      },
    ]);
  };

  const handleApprove = async () => {
    if (!analysis) return;
    setSaving(true);
    setError(null);

    try {
      const mappingDict: Record<string, string> = {};
      mappings.forEach((m) => {
        if (m.source_field && m.target_field) {
          mappingDict[m.source_field] = m.target_field;
        }
      });

      const res = await api.approveParser({
        name: parserName.trim() || `${vendorName} Parser`,
        vendor: vendorName.trim() || "Custom",
        format: analysis.detected_format || "custom",
        sample_log: rawLog.trim(),
        mapping: mappingDict,
        event_type: analysis.event_type || "firewall",
      });

      if (res.success) {
        setSavedSuccess(`Parser approved and registered as ${res.parser_id}! Ready for dynamic parsing.`);
        setTestLog(rawLog.trim());
      }
    } catch (err: any) {
      setError(err.message || "Failed to save parser.");
    } finally {
      setSaving(false);
    }
  };

  const handleTestParser = async () => {
    if (!testLog.trim()) return;
    setTesting(true);
    setTestResult(null);

    try {
      const res = await api.processEvent(testLog.trim());
      if (res.success && res.event) {
        setTestResult(res.event);
      } else {
        alert(res.message || "Failed to parse log.");
      }
    } catch (err: any) {
      alert(err.message || "Parsing error.");
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header title="AI Parser Studio" />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* Intro Banner */}
        <div className="p-5 rounded-2xl bg-white border border-purple-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-purple-50 text-purple-600 shrink-0 border border-purple-100">
            <Cpu className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">AI-Assisted Format Onboarding Engine</h3>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              When encountering proprietary, legacy, or custom logs, ULPF uses structured AI decomposition to detect vendor signatures, identify fields, generate Universal Schema mappings, and instantiate an active parser in MongoDB upon your approval.
            </p>
          </div>
        </div>

        {/* Step 1: Input Raw Unknown Log */}
        <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold">
                1
              </span>
              <h3 className="text-sm font-bold text-slate-900">Provide Unsupported / Custom Log</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-400 font-medium">Load Sample:</span>
              {SAMPLE_UNKNOWN_LOGS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setRawLog(s.log)}
                  className="px-2.5 py-1 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-700 text-[11px] font-medium border border-slate-200/80 transition-colors"
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <textarea
              value={rawLog}
              onChange={(e) => setRawLog(e.target.value)}
              placeholder="Paste previously unsupported log line here..."
              rows={4}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 font-mono text-xs text-slate-800 focus:outline-none focus:border-purple-500 focus:bg-white transition-all"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <button
              onClick={() => {
                setRawLog("");
                setAnalysis(null);
                setSavedSuccess(null);
              }}
              className="text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1 font-medium"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Clear</span>
            </button>

            <button
              onClick={handleAnalyze}
              disabled={analyzing || !rawLog.trim()}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-semibold bg-purple-600 hover:bg-purple-700 text-white shadow-sm disabled:opacity-50 transition-all"
            >
              <Sparkles className={`h-4 w-4 ${analyzing ? "animate-spin" : ""}`} />
              <span>{analyzing ? "Deconstructing Log with AI..." : "Analyze with AI"}</span>
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Step 2 & 3: AI Analysis Results and Field Mapping Table */}
        {analysis && (
          <div className="space-y-6">
            {/* Step 2: Detection Badges Overview */}
            <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center h-6 w-6 rounded-full bg-purple-600 text-white text-xs font-bold">
                  2
                </span>
                <h3 className="text-sm font-bold text-slate-900">AI Format Analysis & Detection</h3>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    Detected Vendor
                  </span>
                  <input
                    type="text"
                    value={vendorName}
                    onChange={(e) => setVendorName(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-xs text-slate-800 font-bold focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    Detected Format
                  </span>
                  <div className="text-xs font-mono text-purple-700 font-bold pt-1">
                    {analysis.detected_format}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    Event Classification
                  </span>
                  <div className="text-xs font-mono text-blue-700 font-bold pt-1 capitalize">
                    {analysis.event_type}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-1">
                    AI Confidence Score
                  </span>
                  <div className="text-xs font-mono text-emerald-600 font-bold pt-1">
                    {(analysis.confidence * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="p-3.5 rounded-xl bg-purple-50/60 border border-purple-100 text-xs text-purple-900">
                <strong className="font-bold">AI Reasoning: </strong>
                <span>{analysis.reasoning}</span>
              </div>
            </div>

            {/* Step 3: Interactive Mapping Table */}
            <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold">
                    3
                  </span>
                  <h3 className="text-sm font-bold text-slate-900">Universal Schema Field Mapping</h3>
                </div>
                <button
                  onClick={handleAddMapping}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add Field</span>
                </button>
              </div>

              <div className="overflow-x-auto border border-slate-100 rounded-xl">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-100">
                    <tr>
                      <th className="py-2.5 px-4">Original Field</th>
                      <th className="py-2.5 px-4">Sample Value</th>
                      <th className="py-2.5 px-4">Target Universal Schema Field</th>
                      <th className="py-2.5 px-4">Confidence</th>
                      <th className="py-2.5 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {mappings.map((m, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/80">
                        <td className="py-2.5 px-4">
                          <input
                            type="text"
                            value={m.source_field}
                            onChange={(e) => {
                              const updated = [...mappings];
                              updated[idx].source_field = e.target.value;
                              setMappings(updated);
                            }}
                            className="bg-transparent border-b border-slate-200 text-purple-700 font-bold focus:outline-none focus:border-purple-500 px-1 py-0.5"
                          />
                        </td>
                        <td className="py-2.5 px-4 text-slate-600 text-[11px] truncate max-w-[150px]">
                          {m.sample_value || "—"}
                        </td>
                        <td className="py-2.5 px-4">
                          <select
                            value={m.target_field}
                            onChange={(e) => handleUpdateMapping(idx, e.target.value)}
                            className="bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1 text-xs text-blue-700 font-bold focus:outline-none focus:border-blue-500 font-sans"
                          >
                            {TARGET_SCHEMA_OPTIONS.map((opt) => (
                              <option key={opt.value} value={opt.value}>
                                {opt.label}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="py-2.5 px-4 text-emerald-600 font-semibold text-[11px]">
                          {(m.confidence * 100).toFixed(0)}%
                        </td>
                        <td className="py-2.5 px-4 text-right">
                          <button
                            onClick={() => handleRemoveMapping(idx)}
                            className="text-slate-400 hover:text-red-500 p-1 rounded transition-colors"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Step 4 & 5: Parser Metadata & Approval */}
              <div className="pt-3 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3 w-full md:w-auto">
                  <label className="text-xs font-bold text-slate-700 shrink-0">Parser Name:</label>
                  <input
                    type="text"
                    value={parserName}
                    onChange={(e) => setParserName(e.target.value)}
                    placeholder="e.g. Custom Firewall Parser"
                    className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 font-medium focus:outline-none focus:border-purple-500 w-full md:w-64"
                  />
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                  <button
                    onClick={() => {
                      setAnalysis(null);
                      setMappings([]);
                    }}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                  >
                    Reject Mapping
                  </button>

                  <button
                    onClick={handleApprove}
                    disabled={saving || mappings.length === 0}
                    className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm disabled:opacity-50 transition-all"
                  >
                    <Save className="h-4 w-4" />
                    <span>{saving ? "Saving Parser..." : "Approve & Register Parser"}</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Saved Confirmation & Immediate Dynamic Test Sandbox */}
            {savedSuccess && (
              <div className="p-6 rounded-2xl bg-emerald-50/80 border border-emerald-200 space-y-4">
                <div className="flex items-center gap-2.5 text-emerald-800 font-bold text-sm">
                  <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                  <span>{savedSuccess}</span>
                </div>

                <div className="space-y-3 pt-2 border-t border-emerald-100">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Dynamic Test Sandbox (Verify Second Log)
                  </h4>
                  <p className="text-xs text-slate-600">
                    Test another similar log through the pipeline now. It will be parsed deterministically by your newly approved custom parser without calling AI:
                  </p>

                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={testLog}
                      onChange={(e) => setTestLog(e.target.value)}
                      placeholder="Paste similar custom log line..."
                      className="flex-1 bg-white border border-slate-200 rounded-xl p-3 text-xs font-mono text-slate-800 focus:outline-none focus:border-emerald-500"
                    />
                    <button
                      onClick={handleTestParser}
                      disabled={testing || !testLog.trim()}
                      className="px-5 py-3 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-1.5 shadow-sm disabled:opacity-50 transition-colors"
                    >
                      <Play className="h-3.5 w-3.5" />
                      <span>{testing ? "Testing..." : "Test Log"}</span>
                    </button>
                  </div>

                  {testResult && (
                    <div className="p-4 rounded-xl bg-white border border-emerald-200 space-y-2 font-mono text-xs shadow-xs">
                      <div className="flex items-center gap-2 text-emerald-700 font-bold font-sans">
                        <Check className="h-4 w-4 text-emerald-600" />
                        <span>Successfully parsed by dynamic parser: {testResult.processing.parser}</span>
                      </div>
                      <div className="text-slate-700">
                        <strong>Source IP:</strong> {testResult.network.source_ip || "—"} |{" "}
                        <strong>Destination IP:</strong> {testResult.network.destination_ip || "—"} |{" "}
                        <strong>Action:</strong> {testResult.event.action} |{" "}
                        <strong>SHA-256:</strong> {testResult.integrity.sha256.slice(0, 20)}...
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
