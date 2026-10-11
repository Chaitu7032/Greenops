"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Menu,
  Leaf,
  Search,
  RefreshCw,
  Bell,
  CheckCircle2,
  X,
  ExternalLink,
  Zap,
  LayoutDashboard,
  GitPullRequest,
  FolderGit2,
  CalendarDays,
  ShieldCheck,
  Settings,
} from "lucide-react";
import { MenuDrawer } from "@/components/layout/MenuDrawer";

export const NAV_LINKS = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Pipelines", href: "/pipelines", icon: GitPullRequest },
  { name: "Repositories", href: "/repositories", icon: FolderGit2 },
  { name: "Sprints", href: "/sprints", icon: CalendarDays },
  { name: "Policies", href: "/policies", icon: ShieldCheck },
  { name: "Settings", href: "/settings", icon: Settings },
];

export const TopNavbar: React.FC = () => {
  const pathname = usePathname();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNotifications, setShowNotifications] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>("Just now");

  useEffect(() => {
    const updateSync = () => {
      const now = new Date();
      setLastSyncTime(
        now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    };
    updateSync();
    const interval = setInterval(updateSync, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      window.location.reload();
    } finally {
      setTimeout(() => setIsRefreshing(false), 800);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-40 h-16 bg-surface-sidebar/95 backdrop-blur-md border-b border-surface-border px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4 transition-all">
        {/* Left: Hamburger Menu + Brand Logo + Desktop Nav Links */}
        <div className="flex items-center gap-4 lg:gap-6">
          {/* Hamburger Menu Icon Button */}
          <button
            onClick={() => setDrawerOpen(true)}
            className="p-2 -ml-2 rounded-xl text-zinc-300 hover:text-emerald-400 hover:bg-surface-hover border border-surface-border hover:border-emerald-500/30 transition-all focus:outline-none"
            aria-label="Open navigation menu"
            title="Open Platform Navigation Drawer"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Brand Logo */}
          <Link href="/dashboard" className="flex items-center gap-2.5 group flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-md shadow-emerald-950/60 transition-transform group-hover:scale-105">
              <Leaf className="w-4 h-4 text-zinc-950 fill-zinc-950" />
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-sm tracking-tight text-zinc-100 group-hover:text-emerald-400 transition-colors">
                  GreenOps
                </span>
                <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.2 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 hidden sm:inline-block">
                  SaaS
                </span>
              </div>
              <span className="text-[10px] text-zinc-400 tracking-wide hidden sm:block">
                Carbon &amp; FinOps Gate
              </span>
            </div>
          </Link>

          {/* Horizontal Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 pl-2 border-l border-surface-border/80">
            {NAV_LINKS.map((link) => {
              const isActive =
                pathname === link.href ||
                (link.href !== "/dashboard" && pathname.startsWith(link.href));
              const Icon = link.icon;

              return (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? "bg-surface-muted text-emerald-400 font-semibold border border-emerald-800/40 shadow-sm"
                      : "text-zinc-400 hover:text-zinc-100 hover:bg-surface-hover"
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? "text-emerald-400" : "text-zinc-400"}`} />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right: Search + Gatekeeper Pill + Refresh + Alerts + Profile */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Global Search */}
          <div className="relative w-48 xl:w-64 hidden md:block">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search telemetry..."
              className="w-full pl-8 pr-12 py-1 rounded-lg bg-surface-card border border-surface-border text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 transition-all"
            />
            <kbd className="absolute right-2 top-1/2 -translate-y-1/2 px-1 py-0.2 rounded bg-surface-muted border border-surface-border text-[9px] font-mono text-zinc-400">
              ⌘K
            </kbd>
          </div>

          {/* Live Gatekeeper Pulse Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/60 text-xs">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <span className="font-semibold text-emerald-300 text-[11px] tracking-tight">
              Gatekeeper Guarding
            </span>
          </div>

          {/* Telemetry Refresh */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            title={`Telemetry synced at ${lastSyncTime}`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border hover:bg-surface-hover hover:border-surface-border-highlight text-xs font-medium text-zinc-300 transition-all disabled:opacity-50"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 text-emerald-400 ${
                isRefreshing ? "animate-spin" : ""
              }`}
            />
            <span className="hidden sm:inline text-[11px]">Sync</span>
          </button>

          {/* Notifications Popover */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg bg-surface-card border border-surface-border hover:bg-surface-hover text-zinc-400 hover:text-zinc-200 transition-colors focus:outline-none"
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-400 ring-2 ring-surface-sidebar" />
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 rounded-xl bg-surface-card border border-surface-border shadow-2xl p-4 z-50 animate-fade-in text-xs space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-surface-border">
                  <span className="font-semibold text-zinc-100">
                    Governance Alerts
                  </span>
                  <button
                    onClick={() => setShowNotifications(false)}
                    className="text-zinc-400 hover:text-zinc-200"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="space-y-2.5">
                  <div className="p-2.5 rounded-lg bg-surface-muted/60 border border-surface-border space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-emerald-400 flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> PR #104 Approved
                      </span>
                      <span className="text-[10px] text-zinc-400">2m ago</span>
                    </div>
                    <p className="text-[11px] text-zinc-300">
                      Calculated $0.024 spend, Scope-2 0.61g CO₂e within sprint budget.
                    </p>
                  </div>

                  <div className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-900/40 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-amber-400 flex items-center gap-1">
                        <Zap className="w-3 h-3" /> Off-Peak Deferred
                      </span>
                      <span className="text-[10px] text-zinc-400">12m ago</span>
                    </div>
                    <p className="text-[11px] text-zinc-300">
                      High grid intensity (&gt;380g). PR #105 queued for 02:00 UTC.
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-surface-border text-center">
                  <Link
                    href="/pipelines"
                    onClick={() => setShowNotifications(false)}
                    className="text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-1 text-[11px]"
                  >
                    View full telemetry stream <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* User Profile */}
          <div className="flex items-center gap-2 pl-2 border-l border-surface-border">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-700 to-teal-500 border border-emerald-400/30 flex items-center justify-center text-xs font-bold text-zinc-950 shadow-inner">
              GO
            </div>
            <div className="hidden xl:flex flex-col text-left">
              <span className="text-xs font-semibold text-zinc-200">
                Lead Architect
              </span>
              <span className="text-[10px] text-zinc-400">GreenOps Admin</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hamburger Menu Drawer */}
      <MenuDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </>
  );
};
