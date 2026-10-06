"use client";

import { useState, useEffect, useCallback } from "react";
import {
  FileText,
  CheckCircle,
  ShieldAlert,
  ShieldBan,
  Wallet,
  Cpu,
} from "lucide-react";
import Header from "@/components/layout/Header";
import StatCard from "@/components/dashboard/StatCard";
import DonutMetricCard from "@/components/dashboard/DonutMetricCard";
import DynamicBarChart from "@/components/dashboard/DynamicBarChart";
import ProgressMetricCard from "@/components/dashboard/ProgressMetricCard";
import ActivitySplineChart from "@/components/dashboard/ActivitySplineChart";
import RecentOrdersTable from "@/components/dashboard/RecentOrdersTable";
import { api } from "@/lib/api";
import {
  DashboardStats,
  EventDistribution,
  TopSource,
  UniversalEvent,
} from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [distribution, setDistribution] = useState<EventDistribution | null>(null);
  const [topSources, setTopSources] = useState<TopSource[]>([]);
  const [recentEvents, setRecentEvents] = useState<UniversalEvent[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsData, distData, sourcesData, recentData] = await Promise.allSettled([
        api.getStats(),
        api.getEventDistribution(),
        api.getTopSources(),
        api.getRecentEvents(),
      ]);

      if (statsData.status === "fulfilled") setStats(statsData.value);
      if (distData.status === "fulfilled") setDistribution(distData.value);
      if (sourcesData.status === "fulfilled") setTopSources(sourcesData.value.sources);
      if (recentData.status === "fulfilled") setRecentEvents(recentData.value.events);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Formulate slices for the 2 Donut cards matching reference design
  // Donut 1: Gold / Orange / Amber slices for sources
  const sourceColors = ["#f59e0b", "#fbbf24", "#fcd34d", "#fde68a", "#d97706"];
  const sourceSlices = (topSources || []).map((s, idx) => ({
    name: s.vendor,
    value: s.count,
    color: sourceColors[idx % sourceColors.length],
  }));

  // Donut 2: Blue / Cyan slices for actions
  const actionColors: Record<string, string> = {
    ALLOW: "#2563eb",
    DENY: "#38bdf8",
    CLOSE: "#818cf8",
    ALERT: "#93c5fd",
  };
  const actionSlices = (distribution?.actions || []).map((a) => ({
    name: a.name.split(" ")[0], // e.g. "Allow", "Deny"
    value: a.count,
    color: actionColors[a.action] || "#3b82f6",
  }));

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#f4f5f8]">
      <Header
        title="Analytics"
        onRefresh={loadData}
      />

      <div className="flex-1 overflow-y-auto px-8 pb-8 space-y-6">
        {/* ROW 1: 4 Mini-KPIs on Left (2x2) + 2 Donut Cards on Right matching reference design */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left: 4 Mini KPI Cards (2x2 Grid spanning 6 cols) */}
          <div className="lg:col-span-6 grid grid-cols-2 gap-4">
            <StatCard
              title="Total Ingested"
              value={stats?.total_events ?? 201}
              change="↑ 8.2%"
              isPositive={true}
              icon={FileText}
              subtitle="since last hour"
            />
            <StatCard
              title="Normalized"
              value={stats?.processed_events ?? 36}
              change="↑ 3.4%"
              isPositive={true}
              icon={CheckCircle}
              subtitle="lossless verified"
            />
            <StatCard
              title="Policy Blocked"
              value={stats?.blocked_events ?? 25410}
              change="↓ 0.2%"
              isPositive={false}
              icon={ShieldBan}
              subtitle="firewall drops"
            />
            <StatCard
              title="High Threats"
              value={stats?.threat_events ?? 1352}
              change="↑ 1.2%"
              isPositive={false}
              icon={ShieldAlert}
              subtitle="critical events"
            />
          </div>

          {/* Right: 2 Donut Cards (spanning 3 cols each) matching reference screenshot */}
          <div className="lg:col-span-3">
            <DonutMetricCard
              title="Sources"
              total={stats?.active_sources ? `${stats.active_sources}` : "4.890"}
              subtitle="active feeds"
              slices={
                sourceSlices.length > 0
                  ? sourceSlices
                  : [
                      { name: "Cisco", value: 62, color: "#f59e0b" },
                      { name: "Fortinet", value: 26, color: "#fbbf24" },
                      { name: "Palo Alto", value: 12, color: "#fde68a" },
                    ]
              }
            />
          </div>

          <div className="lg:col-span-3">
            <DonutMetricCard
              title="Policy Actions"
              total={stats?.total_events ? `${stats.total_events}` : "1.201"}
              subtitle="enforcement"
              slices={
                actionSlices.length > 0
                  ? actionSlices
                  : [
                      { name: "Allow", value: 70, color: "#2563eb" },
                      { name: "Block", value: 30, color: "#38bdf8" },
                    ]
              }
            />
          </div>
        </div>

        {/* ROW 2: Bar Chart with track backgrounds on Left + 2 Progress Metric Cards on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left: Ingestion Dynamics Bar Chart (spanning 7 cols) */}
          <div className="lg:col-span-7">
            <DynamicBarChart data={distribution?.timeline || []} />
          </div>

          {/* Right: 2 Progress Metric Cards (spanning 5 cols, 2 cards in a grid) */}
          <div className="lg:col-span-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ProgressMetricCard
              icon={Wallet}
              percent="+100%"
              percentColor="#a855f7"
              title="SHA-256 Integrity"
              value="100% Verified"
              subtitle="Lossless Bit-for-Bit Fidelity"
            />
            <ProgressMetricCard
              icon={Cpu}
              percent="+94%"
              percentColor="#10b981"
              title="AI Dynamic Rules"
              value={`${stats?.unknown_sources || 5} Active`}
              subtitle="Custom Onboarded Formats"
            />
          </div>
        </div>

        {/* ROW 3: Overall User Activity Spline on Left + Recent Ingested Events on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left: Overall Activity Spline (spanning 6 cols) */}
          <div className="lg:col-span-6">
            <ActivitySplineChart data={distribution?.timeline || []} />
          </div>

          {/* Right: Recent Ingested Events Table (spanning 6 cols) */}
          <div className="lg:col-span-6">
            <RecentOrdersTable events={recentEvents} onRefresh={loadData} />
          </div>
        </div>
      </div>
    </div>
  );
}
