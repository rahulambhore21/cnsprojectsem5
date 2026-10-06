import {
  DashboardStats,
  EventDistribution,
  TopSource,
  UniversalEvent,
  AIAnalysisResponse,
  ParserItem,
  SourceItem
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}/api${endpoint}`;
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, {
      ...options,
      headers: options.body instanceof FormData ? undefined : headers,
      cache: "no-store",
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errorData = await res.json();
        errorMsg = errorData.detail || errorData.message || errorMsg;
      } catch {
        // ignore fallback
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request<{ status: string; database: { status: string } }>("/health"),

  // Dashboard
  getStats: () => request<DashboardStats>("/dashboard/stats"),
  getRecentEvents: () => request<{ events: UniversalEvent[] }>("/dashboard/recent-events"),
  getEventDistribution: () => request<EventDistribution>("/dashboard/event-distribution"),
  getTopSources: () => request<{ sources: TopSource[] }>("/dashboard/top-sources"),

  // Events
  getEvents: (params: {
    q?: string;
    vendor?: string;
    format?: string;
    action?: string;
    severity?: string;
    source_ip?: string;
    destination_ip?: string;
    page?: number;
    limit?: number;
  } = {}) => {
    const query = new URLSearchParams();
    if (params.q) query.set("q", params.q);
    if (params.vendor && params.vendor !== "all") query.set("vendor", params.vendor);
    if (params.format && params.format !== "all") query.set("format", params.format);
    if (params.action && params.action !== "all") query.set("action", params.action);
    if (params.severity && params.severity !== "all") query.set("severity", params.severity);
    if (params.source_ip) query.set("source_ip", params.source_ip);
    if (params.destination_ip) query.set("destination_ip", params.destination_ip);
    if (params.page) query.set("page", params.page.toString());
    if (params.limit) query.set("limit", params.limit.toString());

    return request<{
      events: UniversalEvent[];
      total: number;
      page: number;
      limit: number;
      pages: number;
    }>(`/events?${query.toString()}`);
  },

  getEvent: (eventId: string) => request<UniversalEvent>(`/events/${eventId}`),

  processEvent: (rawLog: string, sourceHint?: string) =>
    request<{ success: boolean; event: UniversalEvent; message: string }>("/events/process", {
      method: "POST",
      body: JSON.stringify({ raw_log: rawLog, source_hint: sourceHint }),
    }),

  uploadLogFile: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<{
      success: boolean;
      total_lines: number;
      processed_count: number;
      failed_count: number;
      processed_events: UniversalEvent[];
    }>("/logs/upload", {
      method: "POST",
      body: formData,
    });
  },

  // AI Parser Studio
  analyzeWithAI: (rawLog: string, contextHint?: string) =>
    request<AIAnalysisResponse>("/parser-studio/analyze", {
      method: "POST",
      body: JSON.stringify({ raw_log: rawLog, context_hint: contextHint }),
    }),

  approveParser: (approvalData: {
    name: string;
    vendor: string;
    format: string;
    sample_log: string;
    mapping: Record<string, string>;
    event_type?: string;
  }) =>
    request<{ success: boolean; parser_id: string; message: string }>("/parser-studio/approve", {
      method: "POST",
      body: JSON.stringify(approvalData),
    }),

  // Parsers & Sources
  getParsers: () => request<{ parsers: ParserItem[]; total: number }>("/parsers"),
  getSources: () => request<{ sources: SourceItem[]; total: number }>("/sources"),

  // Demo
  seedDemoData: () =>
    request<{ success: boolean; message: string; seeded_count: number; vendors: string[] }>("/demo/seed", {
      method: "POST",
    }),
  getSampleLogs: () => request<Record<string, string[]>>("/demo/samples"),
};
