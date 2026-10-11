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
  X,
  Zap,
  Activity,
  ChevronRight,
} from "lucide-react";

interface MenuDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NAVIGATION_ITEMS = [
  {
    name: "Overview",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: "Live",
    desc: "Command center & metric KPIs",
  },
  {
    name: "Pipelines",
    href: "/pipelines",
    icon: GitPullRequest,
    desc: "CI/CD pull request telemetry stream",
  },
  {
    name: "Repositories",
    href: "/repositories",
    icon: FolderGit2,
    desc: "Microservices & hardware power profiles",
  },
  {
    name: "Sprints",
    href: "/sprints",
    icon: CalendarDays,
    desc: "Sprint budget ledger & burn-down",
  },
  {
    name: "Policies",
    href: "/policies",
    icon: ShieldCheck,
    desc: "Gatekeeper rules & deferred execution",
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
    desc: "Backend health & GitHub webhooks",
  },
];

export const MenuDrawer: React.FC<MenuDrawerProps> = ({ isOpen, onClose }) => {
  const pathname = usePathname();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity animate-fade-in"
        onClick={onClose}
      />

      {/* Slide-out Drawer */}
      <div className="fixed inset-y-0 left-0 max-w-xs w-full bg-surface-sidebar border-r border-surface-border shadow-2xl flex flex-col justify-between z-50 animate-slide-up sm:max-w-sm">
        <div>
          {/* Header */}
          <div className="h-16 px-5 flex items-center justify-between border-b border-surface-border bg-surface-card/60">
            <Link
              href="/dashboard"
              className="flex items-center gap-2.5 group"
              onClick={onClose}
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-md shadow-emerald-950/60">
                <Leaf className="w-4 h-4 text-zinc-950 fill-zinc-950" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-sm text-zinc-100 group-hover:text-emerald-400 transition-colors">
                    GreenOps
                  </span>
                  <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                    SaaS
                  </span>
                </div>
                <span className="text-[10px] text-zinc-400">
                  Carbon &amp; FinOps Gate
                </span>
              </div>
            </Link>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-surface-hover focus:outline-none transition-colors"
              aria-label="Close menu"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Nav List */}
          <div className="p-3 space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-zinc-400">
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
                  className={`group flex items-start gap-3 p-3 rounded-xl transition-all ${
                    isActive
                      ? "bg-surface-muted text-emerald-400 border border-emerald-900/40 shadow-sm"
                      : "text-zinc-300 hover:text-zinc-100 hover:bg-surface-hover hover:border hover:border-surface-border"
                  }`}
                >
                  <div
                    className={`p-2 rounded-lg border mt-0.5 ${
                      isActive
                        ? "bg-emerald-950/80 border-emerald-800 text-emerald-400"
                        : "bg-surface-muted border-surface-border text-zinc-400 group-hover:text-emerald-400"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-zinc-200 group-hover:text-emerald-300 transition-colors">
                        {item.name}
                      </span>
                      {item.badge && (
                        <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-900/40 text-emerald-400 border border-emerald-800/40">
                          {item.badge}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-400 mt-0.5 truncate">
                      {item.desc}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Footer info */}
        <div className="p-4 border-t border-surface-border bg-surface-card/40 space-y-3">
          <div className="p-3 rounded-xl bg-surface-card border border-surface-border space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold text-zinc-400 uppercase tracking-wider">
                Gatekeeper Engine
              </span>
              <span className="flex items-center gap-1 text-[10px] font-mono text-emerald-400">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Active
              </span>
            </div>
            <div className="text-xs font-semibold text-zinc-200">
              100% Policy Enforced
            </div>
          </div>

          <div className="flex items-center justify-between text-[10px] text-zinc-400 px-1">
            <span>SPM Academic Capstone</span>
            <span className="font-mono">US-EAST</span>
          </div>
        </div>
      </div>
    </div>
  );
};
