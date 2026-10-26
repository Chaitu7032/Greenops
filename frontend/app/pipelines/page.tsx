"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PipelineRun } from "@/types";
import { PipelineTable } from "@/components/pipelines/PipelineTable";
import {
  RefreshCw,
  Filter,
  Search,
  GitPullRequest,
  CheckCircle2,
  Clock,
  AlertTriangle,
  SlidersHorizontal,
} from "lucide-react";

import { LeafProgress } from "@/components/ui/LeafProgress";

export default function PipelinesPage() {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [filterDecision, setFilterDecision] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const loadPipelines = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const data = await api.getPipelines({
        policy_decision: filterDecision || undefined,
        limit: 100,
      });
      setRuns(data);
    } catch (e) {
      console.error("Error loading pipelines:", e);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadPipelines();
    const interval = setInterval(() => {
      loadPipelines(true);
    }, 8000);
    return () => clearInterval(interval);
  }, [filterDecision]);

  // Client-side text search filter
  const filteredRuns = runs.filter((r) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    const prStr = r.pr_number ? `pr #${r.pr_number}` : "workflow";
    const commit = (r.commit_sha || "").toLowerCase();
    const repo = (r.repository_name || "").toLowerCase();
    const author = (r.author || "").toLowerCase();
    const workflow = (r.workflow_name || "").toLowerCase();

    return (
      prStr.includes(term) ||
      commit.includes(term) ||
      repo.includes(term) ||
      author.includes(term) ||
      workflow.includes(term)
    );
  });

  const approvedCount = runs.filter((r) => r.policy_decision === "APPROVED").length;
  const deferredCount = runs.filter((r) => r.policy_decision === "DEFERRED").length;
  const flaggedCount = runs.filter((r) => r.policy_decision === "FLAGGED").length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
              CI/CD Pipeline Telemetry &amp; Gatekeeper Audit
            </h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-muted text-emerald-400 border border-surface-border">
              {runs.length} Evaluated
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Complete audit trail of pull request diffs, duration estimators, actual compute costs, and gatekeeper decisions.
          </p>
        </div>

        <button
          onClick={() => loadPipelines()}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card border border-surface-border hover:bg-surface-hover text-xs font-semibold text-zinc-300 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh Feed</span>
        </button>
      </div>

      {/* Decision Summary KPI Strips */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button
          onClick={() => setFilterDecision("")}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            filterDecision === ""
              ? "bg-surface-muted border-emerald-500/60 shadow-sm"
              : "bg-surface-card border-surface-border hover:border-zinc-700"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">
              Total Runs
            </span>
            <GitPullRequest className="w-3.5 h-3.5 text-zinc-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-zinc-100 tabular-nums">
            {runs.length}
          </div>
        </button>

        <button
          onClick={() => setFilterDecision("APPROVED")}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            filterDecision === "APPROVED"
              ? "bg-emerald-950/40 border-emerald-500 shadow-sm"
              : "bg-surface-card border-surface-border hover:border-emerald-800/60"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
              Approved
            </span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-emerald-400 tabular-nums">
            {approvedCount}
          </div>
        </button>

        <button
          onClick={() => setFilterDecision("DEFERRED")}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            filterDecision === "DEFERRED"
              ? "bg-amber-950/40 border-amber-500 shadow-sm"
              : "bg-surface-card border-surface-border hover:border-amber-800/60"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">
              Deferred (Off-Peak)
            </span>
            <Clock className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-amber-400 tabular-nums">
            {deferredCount}
          </div>
        </button>

        <button
          onClick={() => setFilterDecision("FLAGGED")}
          className={`p-3.5 rounded-xl border text-left transition-all ${
            filterDecision === "FLAGGED"
              ? "bg-rose-950/40 border-rose-500 shadow-sm"
              : "bg-surface-card border-surface-border hover:border-rose-800/60"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">
              Flagged (Over Cap)
            </span>
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <div className="mt-2 text-xl font-bold text-rose-400 tabular-nums">
            {flaggedCount}
          </div>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by PR #, author, commit SHA, branch..."
            className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-surface-canvas border border-surface-border text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/40 transition-all"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
          <div className="flex items-center gap-2 bg-surface-canvas border border-surface-border rounded-lg px-3 py-1.5 text-xs text-zinc-300">
            <Filter className="w-3.5 h-3.5 text-zinc-400" />
            <select
              value={filterDecision}
              onChange={(e) => setFilterDecision(e.target.value)}
              className="bg-transparent text-zinc-200 focus:outline-none cursor-pointer"
            >
              <option value="">All Decisions</option>
              <option value="APPROVED">Approved Only</option>
              <option value="DEFERRED">Deferred Only</option>
              <option value="FLAGGED">Flagged Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      {loading && runs.length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center">
          <LeafProgress size={80} label="Loading Telemetry Runs..." sublabel="Fetching audit records from PostgreSQL / SQLite" />
        </div>
      ) : (
        <PipelineTable runs={filteredRuns} title="Filtered CI/CD Pipeline Runs" showAllLink={false} />
      )}
    </div>
  );
}
