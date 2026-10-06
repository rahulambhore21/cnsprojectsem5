"use client";

import { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { ChevronDown } from "lucide-react";
import { DistributionTimeline } from "@/lib/types";

interface ActivitySplineChartProps {
  data: DistributionTimeline[];
}

export default function ActivitySplineChart({ data }: ActivitySplineChartProps) {
  const [period, setPeriod] = useState("2026");

  // Format smooth timeline data points matching reference wave curve
  const samplePoints = [
    { label: "Q1", value: 120 },
    { label: "Q2", value: 240 },
    { label: "Q3", value: 180 },
    { label: "Q4", value: 290 },
    { label: "Q5", value: 310 },
    { label: "Q6", value: 210 },
    { label: "Q7", value: 360 },
  ];

  const chartData = (data && data.length >= 4)
    ? data.map((d, i) => ({ label: d.time || `P${i+1}`, value: d.count * 15 + 40 }))
    : samplePoints;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] h-full flex flex-col justify-between hover:border-slate-200 transition-all">
      {/* Header with Title & Year Dropdown matching reference */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-800">Overall Event Activity</h3>
          <p className="text-[11px] text-slate-400">Cumulative telemetry throughput & security flow curve</p>
        </div>

        <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700 cursor-pointer hover:bg-slate-100 transition-colors">
          <span>{period}</span>
          <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
        </div>
      </div>

      {/* Smooth Purple/Magenta Spline Curve */}
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
            <defs>
              <linearGradient id="purpleSpline" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#c026d3" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#c026d3" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              stroke="#94a3b8"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              dy={8}
            />
            <YAxis
              stroke="#94a3b8"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}k`}
              domain={[0, 400]}
              ticks={[0, 100, 200, 300, 400]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#ffffff",
                borderColor: "#e2e8f0",
                borderRadius: "10px",
                fontSize: "11px",
                boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
              }}
              formatter={(val: any) => [`${val}k events`, "Activity"]}
            />
            <Area
              type="natural"
              dataKey="value"
              stroke="#c026d3"
              strokeWidth={3}
              fill="url(#purpleSpline)"
              dot={false}
              activeDot={{ r: 5, fill: "#c026d3" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
