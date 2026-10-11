"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  GitPullRequest,
  FolderGit2,
  CalendarDays,
  ShieldCheck,
  Settings,
  Leaf,
} from "lucide-react";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const NAVIGATION_ITEMS = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: "Live",
  },
  {
    name: "Pipelines",
    href: "/pipelines",
    icon: GitPullRequest,
  },
  {
    name: "Repositories",
    href: "/repositories",
    icon: FolderGit2,
  },
  {
    name: "Sprints",
    href: "/sprints",
    icon: CalendarDays,
  },
  {
    name: "Policies",
    href: "/policies",
    icon: ShieldCheck,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = false, onClose }) => {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-64 bg-surface-sidebar border-r border-surface-border flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        <div>
          {/* Brand Header */}
          <div className="h-16 px-5 flex items-center justify-between border-b border-surface-border">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 group focus:outline-none"
              onClick={onClose}
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-md shadow-emerald-950/60 transition-transform group-hover:scale-105">
                <Leaf className="w-4 h-4 text-zinc-950 fill-zinc-950" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-sm tracking-tight text-zinc-100 group-hover:text-emerald-400 transition-colors">
                    GreenOps
                  </span>
                  <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                    SaaS
                  </span>
                </div>
                <span className="text-[10px] text-zinc-400 tracking-wide">
                  Carbon & FinOps Gate
                </span>
              </div>
            </Link>
          </div>

          {/* Navigation Section */}
          <div className="px-3 py-4 space-y-1">
            <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
              Platform Modules
            </div>

            {NAVIGATION_ITEMS.map((item) => {
              const isActive =
                pathname === item.href ||
                (item.href !== "/dashboard" && pathname.startsWith(item.href));
              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-surface-muted text-emerald-400 font-semibold shadow-sm border border-emerald-900/40"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-surface-hover hover:border hover:border-surface-border"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive
                          ? "text-emerald-400"
                          : "text-zinc-400 group-hover:text-zinc-300"
                      }`}
                    />
                    <span>{item.name}</span>
                  </div>

                  {item.badge && (
                    <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-900/40 text-emerald-400 border border-emerald-800/40">
                      {item.badge}
                    </span>
                  )}

                  {isActive && (
                    <span className="absolute left-0 top-2 bottom-2 w-0.5 bg-emerald-400 rounded-r-full" />
                  )}
                </Link>
              );
            })}
          </div>
        </div>

        {/* Bottom System & SPM Governance Footer */}
        <div className="p-3 border-t border-surface-border space-y-2">
          <div className="p-3 rounded-xl bg-surface-card border border-surface-border">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                Gatekeeper Engine
              </span>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="mt-1 flex items-baseline justify-between">
              <span className="text-xs font-semibold text-zinc-200">
                Active Governance
              </span>
              <span className="text-[10px] font-mono text-emerald-400">
                100% Policy
              </span>
            </div>
            <div className="mt-2 w-full bg-zinc-900 rounded-full h-1 overflow-hidden">
              <div className="bg-emerald-500 h-full w-full rounded-full" />
            </div>
          </div>

          <div className="px-2 py-1 flex items-center justify-between text-[10px] text-zinc-400">
            <span>SPM Capstone v1.4</span>
            <span className="font-mono">US-EAST</span>
          </div>
        </div>
      </aside>
    </>
  );
};
