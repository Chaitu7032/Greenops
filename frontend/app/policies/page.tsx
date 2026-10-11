"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Policy, DeferredJob } from "@/types";
import { ShieldCheck, Clock, Zap, Save, RefreshCw, AlertTriangle, CheckCircle2, Play, DollarSign, Leaf } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/formatters";

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [deferredJobs, setDeferredJobs] = useState<DeferredJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [dispatchingId, setDispatchingId] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pols, jobs] = await Promise.all([api.getPolicies(), api.getDeferredJobs()]);
      setPolicies(pols);
      setDeferredJobs(jobs);
    } catch (e) {
      console.error("Error loading policies & deferred jobs:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleManualDispatch = async (jobId: string) => {
    try {
      setDispatchingId(jobId);
      await api.dispatchDeferredJob(jobId);
      await loadData();
    } catch (e) {
      console.error("Dispatch error:", e);
    } finally {
      setDispatchingId(null);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
              Policy Gatekeeper &amp; Deferred Execution Queue
            </h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-muted text-emerald-400 border border-surface-border">
              Automated Governance
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Deterministic thresholds for CI cost limits, grid carbon cutoffs, and scheduled off-peak executions.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card border border-surface-border hover:bg-surface-hover text-xs font-semibold text-zinc-300 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Active Policies Cards */}
      <div>
        <h2 className="text-sm font-semibold text-zinc-300 mb-3 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Enforced Policy Rules &amp; Gatekeeper Thresholds
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {policies.map((p) => (
            <div
              key={p.id}
              className="p-6 rounded-xl bg-surface-card border border-surface-border space-y-4 hover-card-glow transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-2 rounded-lg bg-emerald-950/70 text-emerald-400 border border-emerald-800/80">
                    <ShieldCheck className="w-4 h-4" />
                  </div>
                  <span className="font-bold text-sm text-zinc-100">{p.name}</span>
                </div>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-800/80">
                  ENFORCED
                </span>
              </div>

              <div className="space-y-2.5 text-xs text-zinc-300 pt-2">
                <div className="flex items-center justify-between py-1 border-b border-surface-border/60">
                  <span className="text-zinc-400 flex items-center gap-1.5">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Max Single-Run Cost Limit
                  </span>
                  <span className="font-mono font-bold text-zinc-100">
                    ${Number(p.max_cost_per_run_usd).toFixed(2)}
                  </span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-surface-border/60">
                  <span className="text-zinc-400 flex items-center gap-1.5">
                    <Leaf className="w-3.5 h-3.5 text-teal-400" /> Max Single-Run Carbon Footprint
                  </span>
                  <span className="font-mono font-bold text-teal-400">
                    {Number(p.max_carbon_per_run_g).toFixed(0)} gCO₂e
                  </span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-surface-border/60">
                  <span className="text-zinc-400 flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5 text-amber-400" /> High Grid Carbon Intensity Cutoff
                  </span>
                  <span className="font-mono font-bold text-amber-400">
                    {Number(p.high_grid_intensity_threshold).toFixed(0)} gCO₂e / kWh
                  </span>
                </div>

                <div className="flex items-center justify-between py-1 border-b border-surface-border/60">
                  <span className="text-zinc-400">Sprint Budget Warning / Hard Block</span>
                  <span className="font-mono font-bold text-zinc-200">
                    {Number(p.budget_warning_percent).toFixed(0)}% / {Number(p.budget_block_percent).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-zinc-400">Off-Peak Scheduled Deferral</span>
                  <span className="font-semibold text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {p.allow_deferred_execution ? "Enabled (Redis Queue)" : "Disabled"}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Deferred Jobs Queue */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              Deferred Execution Queue (Scheduled Clean Energy Windows)
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Non-critical pull requests deferred during high-carbon grid hours, queued for automatic dispatch or manual trigger.
            </p>
          </div>
        </div>

        {deferredJobs.length === 0 ? (
          <div className="p-8 rounded-xl bg-surface-card border border-surface-border text-center text-zinc-500 text-xs">
            No deferred jobs currently queued in Redis.
          </div>
        ) : (
          <div className="rounded-xl bg-surface-card border border-surface-border overflow-hidden shadow-sm hover-card-glow transition-all">
            <table className="w-full text-left text-xs text-zinc-300">
              <thead className="bg-surface-canvas text-[11px] font-semibold uppercase tracking-wider text-zinc-400 border-b border-surface-border">
                <tr>
                  <th className="px-5 py-3">PR #</th>
                  <th className="px-5 py-3">Repository</th>
                  <th className="px-5 py-3">Scheduled For</th>
                  <th className="px-5 py-3">Deferral Rationale</th>
                  <th className="px-5 py-3">Queue Status</th>
                  <th className="px-5 py-3 text-right">Manual Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border/60">
                {deferredJobs.map((job) => (
                  <tr key={job.id} className="hover:bg-surface-hover/70 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-zinc-100 font-mono">
                      PR #{job.pr_number}
                    </td>
                    <td className="px-5 py-3.5 text-zinc-200 font-medium">
                      {job.repository_name || "Repository"}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-amber-400">
                      {formatDate(job.scheduled_for)}
                    </td>
                    <td className="px-5 py-3.5 text-zinc-400 max-w-sm text-[11px]">
                      {job.reason}
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge status={job.status} size="sm" />
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      {job.status === "PENDING" && (
                        <button
                          onClick={() => handleManualDispatch(job.id)}
                          disabled={dispatchingId === job.id}
                          className="px-3 py-1.5 rounded-lg bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px] font-semibold hover:bg-emerald-900 transition-all flex items-center gap-1.5 ml-auto shadow-sm"
                        >
                          <Play className={`w-3 h-3 ${dispatchingId === job.id ? "animate-spin" : ""}`} />
                          <span>{dispatchingId === job.id ? "Dispatching..." : "Dispatch Now"}</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
