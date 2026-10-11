"use client";

import React from "react";
import { TopNavbar } from "@/components/layout/TopNavbar";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="relative min-h-screen bg-surface-canvas text-zinc-100 flex flex-col antialiased selection:bg-emerald-500/20 selection:text-emerald-300 overflow-x-hidden">
      {/* Environmental Forest & Grid Background Image */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-[0.40] scale-100"
          style={{ backgroundImage: "url('/images/greenops_bg.jpg')" }}
        />
        {/* Soft atmospheric gradient for crisp contrast */}
        <div className="absolute inset-0 bg-gradient-to-b from-surface-canvas/70 via-surface-canvas/80 to-surface-canvas/95" />
        <div className="absolute inset-0 bg-gradient-to-tr from-emerald-950/30 via-transparent to-teal-950/30" />
      </div>

      {/* Top Navigation Bar with Hamburger Drawer & Module Links */}
      <div className="relative z-40">
        <TopNavbar />
      </div>

      {/* Full-width Main Content Area */}
      <main className="relative z-10 flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6">
        {children}
      </main>

      {/* Enterprise Footer */}
      <footer className="relative z-10 border-t border-surface-border py-6 px-4 sm:px-8 text-center text-xs text-zinc-400 bg-surface-sidebar/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-medium text-zinc-300">
              GreenOps CI/CD Governance &amp; Cloud Carbon Gatekeeper
            </span>
          </div>
          <div className="flex items-center gap-4 text-[11px] text-zinc-400">
            <span>PostgreSQL Decimal Precision</span>
            <span>•</span>
            <span>Scope-2 Grid Integration</span>
            <span>•</span>
            <span>SPM Capstone</span>
          </div>
        </div>
      </footer>
    </div>
  );
};


