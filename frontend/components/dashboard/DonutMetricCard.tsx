"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface Slice {
  name: string;
  value: number;
  color: string;
}

interface DonutMetricCardProps {
  title: string;
  total: number | string;
  subtitle?: string;
  slices: Slice[];
}

export default function DonutMetricCard({
  title,
  total,
  subtitle = "active events",
  slices,
}: DonutMetricCardProps) {
  const filtered = slices.filter((s) => s.value > 0);
  const totalValue = slices.reduce((acc, s) => acc + s.value, 0);

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col justify-between hover:border-slate-200 transition-all">
      {/* Top Header */}
      <div>
        <span className="text-xs font-semibold text-slate-500">{title}</span>
        <div className="text-2xl font-bold tracking-tight text-slate-900 font-sans mt-1">
          {typeof total === "number" ? total.toLocaleString() : total}
        </div>
        <p className="text-[11px] text-slate-400 mt-0.5">{subtitle}</p>
      </div>

      {/* Middle Body: Legend on Left + Donut Chart on Right */}
      <div className="flex items-center justify-between gap-2 my-2">
        {/* Legend */}
        <div className="space-y-1.5 text-[11px] shrink-0">
          {filtered.map((s) => {
            const pct = totalValue > 0 ? ((s.value / totalValue) * 100).toFixed(0) : "0";
            return (
              <div key={s.name} className="flex items-center gap-1.5">
                <span
                  className="h-2 w-2 rounded-full shrink-0"
                  style={{ backgroundColor: s.color }}
                />
                <span className="text-slate-600 font-medium">
                  {pct}% {s.name}
                </span>
              </div>
            );
          })}
        </div>

        {/* Compact Donut */}
        <div className="h-24 w-24 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={filtered.length > 0 ? filtered : [{ name: "None", value: 1, color: "#e2e8f0" }]}
                cx="50%"
                cy="50%"
                innerRadius={28}
                outerRadius={44}
                paddingAngle={filtered.length > 1 ? 4 : 0}
                dataKey="value"
                stroke="none"
              >
                {(filtered.length > 0 ? filtered : [{ name: "None", value: 1, color: "#e2e8f0" }]).map(
                  (entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  )
                )}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#ffffff",
                  borderColor: "#e2e8f0",
                  borderRadius: "10px",
                  fontSize: "11px",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
