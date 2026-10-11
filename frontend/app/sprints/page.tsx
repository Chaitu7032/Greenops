"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Sprint, BurnDownPoint } from "@/types";
import { BurnDownChart } from "@/components/dashboard/BurnDownChart";
import { formatCurrency, formatDate } from "@/lib/formatters";
import { Calendar, Target, CheckCircle2, Clock, RefreshCw, Layers, ShieldCheck, DollarSign, Leaf } from "lucide-react";

export default function SprintsPage() {
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [selectedSprintId, setSelectedSprintId] = useState<string>("");
  const [burnDown, setBurnDown] = useState<BurnDownPoint[]>([]);
  const [loading, setLoading] = useState(true);

  const loadSprints = async () => {
    try {
      setLoading(true);
      const data = await api.getSprints();
      setSprints(data);
      if (data.length > 0) {
        const active = data.find((s) => s.status === "ACTIVE") || data[0];
        setSelectedSprintId(active.id);
        const bd = await api.getSprintBurnDown(active.id);
        setBurnDown(bd);
      }
    } catch (e) {
      console.error("Error loading sprints:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSprints();
  }, []);

  const handleSelectSprint = async (sprintId: string) => {
    setSelectedSprintId(sprintId);
    const bd = await api.getSprintBurnDown(sprintId);
    setBurnDown(bd);
  };

  const selectedSprint = sprints.find((s) => s.id === selectedSprintId);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
              Sprint Governance &amp; Budget Ledger
            </h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-muted text-emerald-400 border border-surface-border">
              SPM Integration
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Automated mapping of pull request compute costs and Scope-2 carbon consumption to active project management sprints.
          </p>
        </div>

        <button
          onClick={loadSprints}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card border border-surface-border hover:bg-surface-hover text-xs font-semibold text-zinc-300 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Sprints Selection Grid */}
      <div>
        <h2 className="text-sm font-semibold text-zinc-300 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-emerald-400" />
          Select SPM Sprint to Inspect Burn-Down Trajectory
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {sprints.map((sprint) => {
            const isSelected = sprint.id === selectedSprintId;
            const isActive = sprint.status === "ACTIVE";

            return (
              <div
                key={sprint.id}
                onClick={() => handleSelectSprint(sprint.id)}
                className={`p-5 rounded-xl cursor-pointer transition-all border ${
                  isSelected
                    ? "bg-surface-card border-emerald-500 shadow-md shadow-emerald-950/40 ring-1 ring-emerald-500/30"
                    : "bg-surface-card/60 border-surface-border hover:border-zinc-700 hover:bg-surface-card"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-zinc-100">{sprint.name}</span>
                  <span
                    className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      isActive
                        ? "bg-emerald-950/80 text-emerald-400 border border-emerald-800/80"
                        : "bg-surface-muted text-zinc-400 border border-surface-border"
                    }`}
                  >
                    {sprint.status}
                  </span>
                </div>

                <div className="mt-3 text-xs text-zinc-400 flex items-center gap-1.5 font-mono text-[11px]">
                  <Calendar className="w-3.5 h-3.5 text-zinc-500" />
                  <span>
                    {formatDate(sprint.start_date)} – {formatDate(sprint.end_date)}
                  </span>
                </div>

                <div className="mt-4 pt-3 border-t border-surface-border/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-zinc-400">Budget: </span>
                    <span className="font-bold text-zinc-200 tabular-nums font-mono">
                      {formatCurrency(sprint.budget_usd)}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Leaf className="w-3.5 h-3.5 text-teal-400" />
                    <span className="text-zinc-400">Carbon: </span>
                    <span className="font-bold text-teal-400 tabular-nums font-mono">
                      {sprint.carbon_budget_kg} kg
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Sprint Burn-Down Chart */}
      {selectedSprint && (
        <BurnDownChart
          data={burnDown}
          title={`Financial Burn-Down Trajectory: ${selectedSprint.name} (${formatCurrency(selectedSprint.budget_usd)} Allocated)`}
        />
      )}
    </div>
  );
}
