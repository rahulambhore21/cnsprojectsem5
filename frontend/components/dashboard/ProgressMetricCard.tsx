import React from "react";
import { LucideIcon } from "lucide-react";

interface ProgressMetricCardProps {
  icon: LucideIcon;
  percent: string;
  percentColor?: string;
  title: string;
  value: string;
  subtitle: string;
}

export default function ProgressMetricCard({
  icon: Icon,
  percent = "+15%",
  percentColor = "#a855f7",
  title,
  value,
  subtitle,
}: ProgressMetricCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex flex-col justify-between hover:border-slate-200 transition-all">
      {/* Top Header with Icon on Left + Circular Progress Badge on Right */}
      <div className="flex items-center justify-between">
        <div className="h-10 w-10 rounded-xl border border-slate-200/80 flex items-center justify-center text-slate-700">
          <Icon className="h-5 w-5" />
        </div>

        {/* Circular Progress Indicator with center label */}
        <div className="relative h-10 w-10 flex items-center justify-center">
          <svg className="w-10 h-10 transform -rotate-90">
            <circle
              cx="20"
              cy="20"
              r="15"
              stroke="#f1f5f9"
              strokeWidth="3"
              fill="transparent"
            />
            <circle
              cx="20"
              cy="20"
              r="15"
              stroke={percentColor}
              strokeWidth="3"
              strokeDasharray="94"
              strokeDashoffset="28"
              strokeLinecap="round"
              fill="transparent"
            />
          </svg>
          <span
            className="absolute text-[10px] font-bold"
            style={{ color: percentColor }}
          >
            {percent}
          </span>
        </div>
      </div>

      {/* Bottom Content */}
      <div className="mt-4">
        <span className="text-xs font-medium text-slate-400 block">{title}</span>
        <div className="text-xl font-bold tracking-tight text-slate-900 font-sans mt-0.5">
          {value}
        </div>
        <p className="text-[11px] text-slate-400 mt-1">{subtitle}</p>
      </div>
    </div>
  );
}
