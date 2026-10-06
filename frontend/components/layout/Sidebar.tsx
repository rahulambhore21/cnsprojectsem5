"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  FileText,
  Cpu,
  Users,
  Layers,
  Settings,
  LogOut,
  HelpCircle,
  ShieldAlert,
} from "lucide-react";

const NAV_ITEMS = [
  { name: "Analytics", href: "/dashboard", icon: LayoutGrid },
  { name: "Log Explorer", href: "/logs", icon: FileText },
  { name: "AI Studio", href: "/parser-studio", icon: Cpu, badge: "AI" },
  { name: "Data Sources", href: "/sources", icon: Users },
  { name: "Parser Rules", href: "/parsers", icon: Layers },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-slate-200/70 flex flex-col justify-between shrink-0 select-none shadow-[1px_0_10px_rgba(0,0,0,0.02)] z-20">
      <div>
        {/* Brand Header matching reference logo */}
        <div className="p-6 pb-5 flex items-center gap-3">
          {/* Multi-color cross emblem matching screenshot */}
          <div className="relative h-7 w-7 flex items-center justify-center">
            <span className="absolute h-3.5 w-3.5 rounded-full bg-pink-500 -top-0.5 -left-0.5 opacity-90" />
            <span className="absolute h-3.5 w-3.5 rounded-full bg-blue-600 -top-0.5 -right-0.5 opacity-90" />
            <span className="absolute h-3.5 w-3.5 rounded-full bg-cyan-400 -bottom-0.5 -left-0.5 opacity-90" />
            <span className="absolute h-3.5 w-3.5 rounded-full bg-indigo-600 -bottom-0.5 -right-0.5 opacity-90" />
          </div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-xl tracking-tight text-slate-900">ULPF</span>
            <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-md bg-blue-50 text-blue-600 border border-blue-100">
              SOC
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="px-4 space-y-1 mt-2">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-[#eef4ff] text-blue-600 font-semibold shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`h-[18px] w-[18px] ${
                      isActive ? "text-blue-600 stroke-[2.2]" : "text-slate-500"
                    }`}
                  />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-700">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Divider */}
        <div className="my-4 mx-5 border-t border-slate-100" />

        {/* Secondary Links */}
        <div className="px-4 space-y-1">
          <Link
            href="/settings"
            className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
              pathname === "/settings"
                ? "bg-[#eef4ff] text-blue-600 font-semibold"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
            }`}
          >
            <Settings className="h-[18px] w-[18px] text-slate-500" />
            <span>Settings</span>
          </Link>

          <button
            onClick={() => {
              if (confirm("Reset demo session and return to dashboard?")) {
                window.location.href = "/dashboard";
              }
            }}
            className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium text-slate-600 hover:text-red-600 hover:bg-red-50/50 transition-all text-left"
          >
            <LogOut className="h-[18px] w-[18px] text-slate-500" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>

      {/* Bottom "Need help" card matching reference design */}
      <div className="p-4">
        <div className="bg-[#eef4ff] rounded-2xl p-4 text-center relative overflow-hidden border border-blue-100/60 shadow-xs">
          {/* Subtle Decorative Elements */}
          <div className="flex justify-center mb-2">
            <div className="h-10 w-10 rounded-full bg-white shadow-xs border border-blue-100 flex items-center justify-center">
              <ShieldAlert className="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <p className="text-xs text-slate-700 font-medium">Need help?</p>
          <p className="text-[11px] text-slate-500 mt-0.5">Feel free to contact</p>
          <Link
            href="/settings"
            className="mt-3 block w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
          >
            Get support
          </Link>
        </div>
      </div>
    </aside>
  );
}
