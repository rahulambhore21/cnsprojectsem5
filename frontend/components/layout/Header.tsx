"use client";

import { useState, useEffect } from "react";
import {
  Calendar,
  Sun,
  Moon,
  PlusCircle,
  Sparkles,
  RefreshCw,
  CheckCircle2,
} from "lucide-react";
import { api } from "@/lib/api";
import IngestModal from "@/components/logs/IngestModal";

interface HeaderProps {
  title?: string;
  onRefresh?: () => void;
}

export default function Header({
  title = "Analytics",
  onRefresh,
}: HeaderProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState<string | null>(null);
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.setAttribute("data-theme", "dark");
    } else {
      document.documentElement.removeAttribute("data-theme");
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    setSeedSuccess(null);
    try {
      const res = await api.seedDemoData();
      if (res.success) {
        setSeedSuccess(`Seeded ${res.seeded_count} events!`);
        setTimeout(() => setSeedSuccess(null), 4000);
        if (onRefresh) onRefresh();
      }
    } catch {
      alert("Failed to seed demo data. Ensure backend is running.");
    } finally {
      setSeeding(false);
    }
  };

  return (
    <>
      <header className="h-20 bg-transparent px-8 flex items-center justify-between shrink-0">
        {/* Left: Bold Title + Date Badge matching reference design */}
        <div className="flex items-center gap-6">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 font-sans">
            {title}
          </h1>

          {/* Date range pill badge */}
          <div className="hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-white border border-slate-200/80 shadow-xs text-xs font-medium text-slate-600">
            <span>01.10.2026 - 06.10.2026</span>
            <Calendar className="h-3.5 w-3.5 text-slate-400" />
          </div>
        </div>

        {/* Right side controls matching reference design */}
        <div className="flex items-center gap-4">
          {/* Quick Refresh */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              title="Refresh Analytics"
              className="p-2 rounded-xl bg-white hover:bg-slate-50 text-slate-500 hover:text-slate-800 border border-slate-200/80 shadow-xs transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          )}

          {/* Theme Switcher Toggle matching screenshot pill */}
          <button
            onClick={toggleTheme}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-full bg-white border border-slate-200/80 shadow-xs text-xs text-slate-500 hover:text-slate-800 transition-colors"
            title="Toggle Light / Dark mode"
          >
            <Sun className={`h-3.5 w-3.5 ${!isDark ? "text-amber-500" : "text-slate-400"}`} />
            <div className="w-8 h-4 rounded-full bg-slate-200 p-0.5 flex items-center transition-colors">
              <div
                className={`w-3 h-3 rounded-full bg-blue-600 transition-transform ${
                  isDark ? "translate-x-4" : "translate-x-0"
                }`}
              />
            </div>
            <Moon className={`h-3.5 w-3.5 ${isDark ? "text-indigo-400" : "text-slate-400"}`} />
          </button>

          {/* Seed Demo Button */}
          <button
            onClick={handleSeed}
            disabled={seeding}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white hover:bg-slate-50 text-purple-700 border border-purple-200/80 shadow-xs transition-colors disabled:opacity-50"
          >
            <Sparkles className="h-3.5 w-3.5 text-purple-600" />
            <span>{seeding ? "Seeding..." : "Seed Demo"}</span>
          </button>

          {/* Pre-process Log CTA */}
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm transition-colors"
          >
            <PlusCircle className="h-4 w-4" />
            <span>Pre-process Log</span>
          </button>

          {/* User Profile matching reference avatar */}
          <div className="flex items-center gap-3 pl-2 border-l border-slate-200">
            <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-amber-400 to-pink-500 p-0.5 shadow-xs">
              <div className="h-full w-full rounded-full bg-white flex items-center justify-center font-bold text-xs text-slate-800">
                RA
              </div>
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-bold text-slate-800 leading-tight">Rahul Ambhore</div>
              <div className="text-[10px] text-slate-400 font-medium">SOC Analyst</div>
            </div>
          </div>
        </div>
      </header>

      {/* Seed Success Toast */}
      {seedSuccess && (
        <div className="fixed top-20 right-8 z-50 flex items-center gap-2 text-xs text-emerald-800 bg-emerald-50 border border-emerald-200 px-4 py-2.5 rounded-xl shadow-lg animate-bounce">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <span className="font-semibold">{seedSuccess}</span>
        </div>
      )}

      {/* Ingest Modal */}
      <IngestModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => {
          if (onRefresh) onRefresh();
        }}
      />
    </>
  );
}
