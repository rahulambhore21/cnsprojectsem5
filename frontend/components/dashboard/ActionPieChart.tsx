"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { DistributionAction } from "@/lib/types";

interface ActionPieChartProps {
  data: DistributionAction[];
}

export default function ActionPieChart({ data }: ActionPieChartProps) {
  const filtered = (data || []).filter((d) => d.count > 0);

  if (filtered.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-500">
        No action events recorded yet.
      </div>
    );
  }

  return (
    <div className="h-64 w-full flex flex-col justify-between">
      <ResponsiveContainer width="100%" height={190}>
        <PieChart>
          <Pie
            data={filtered}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={75}
            paddingAngle={4}
            dataKey="count"
          >
            {filtered.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} stroke="#0f172a" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: "#0f172a",
              borderColor: "#334155",
              borderRadius: "8px",
              fontSize: "12px",
              color: "#f8fafc",
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 px-2">
        {filtered.map((item) => (
          <div key={item.action} className="flex items-center gap-1.5 truncate">
            <span
              className="h-2 w-2 rounded-full shrink-0"
              style={{ backgroundColor: item.color }}
            />
            <span className="truncate">{item.name}:</span>
            <strong className="text-slate-200 font-mono ml-auto">{item.count}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
