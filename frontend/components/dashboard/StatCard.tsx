import React from "react";
import { LucideIcon, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface StatCardProps {
  title: string;
  value: number | string;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  subtitle?: string;
}

export default function StatCard({
  title,
  value,
  change = "+3.4%",
  isPositive = true,
  icon: Icon,
  subtitle = "since last hour",
}: StatCardProps) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col justify-between hover:border-slate-200 transition-all">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500">{title}</span>
        <div className="h-7 w-7 rounded-lg border border-slate-200/80 flex items-center justify-center text-slate-500">
          <Icon className="h-3.5 w-3.5" />
        </div>
      </div>

      {/* Middle Value */}
      <div className="my-2.5">
        <div className="text-2xl font-bold tracking-tight text-slate-900 font-sans">
          {typeof value === "number" ? value.toLocaleString() : value}
        </div>
      </div>

      {/* Bottom Trend Badge */}
      <div className="flex items-center gap-1 text-[11px] font-medium">
        <span
          className={`flex items-center ${
            isPositive ? "text-emerald-500" : "text-rose-500"
          }`}
        >
          {isPositive ? (
            <ArrowUpRight className="h-3.5 w-3.5 stroke-[2.5]" />
          ) : (
            <ArrowDownRight className="h-3.5 w-3.5 stroke-[2.5]" />
          )}
          <span>{change}</span>
        </span>
        <span className="text-slate-400">{subtitle}</span>
      </div>
    </div>
  );
}
