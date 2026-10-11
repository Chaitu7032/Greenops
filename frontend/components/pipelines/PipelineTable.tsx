"use client";

import React, { useState } from "react";
import { PipelineRun } from "@/types";
import { Badge } from "@/components/ui/Badge";
import {
  formatCurrency,
  formatCarbon,
  formatDuration,
  formatDate,
} from "@/lib/formatters";
import {
  GitPullRequest,
  GitCommit,
  User,
  Clock,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Zap,
  DollarSign,
  Leaf,
  Layers,
} from "lucide-react";
import Link from "next/link";

interface PipelineTableProps {
  runs: PipelineRun[];
  title?: string;
  showAllLink?: boolean;
}

export const PipelineTable: React.FC<PipelineTableProps> = ({
  runs,
  title = "Recent CI/CD Pipelines & Policy Gatekeeper Decisions",
  showAllLink = true,
}) => {
  const [expandedRunId, setExpandedRunId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedRunId(expandedRunId === id ? null : id);
  };

  if (!runs || runs.length === 0) {
    return (
      <div className="p-8 rounded-xl bg-surface-card border border-surface-border text-center text-zinc-500 text-xs">
        No CI pipeline runs recorded yet. Trigger a pull request webhook or seed demo data.
      </div>
    );
  }

  return (
    <div className="rounded-xl bg-surface-card border border-surface-border overflow-hidden shadow-sm hover-card-glow transition-all">
      <div className="px-6 py-4 border-b border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-surface-muted/40">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
              Audit Stream
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Real-time PR diff analysis, duration estimation, compute FinOps costs, and Scope-2 carbon enforcement
          </p>
        </div>

        {showAllLink && (
          <Link
            href="/pipelines"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors"
          >
            Full Telemetry <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-zinc-300">
          <thead className="bg-surface-canvas text-[11px] font-semibold uppercase tracking-wider text-zinc-400 border-b border-surface-border">
            <tr>
              <th className="px-5 py-3">PR / Commit SHA</th>
              <th className="px-5 py-3">Repository</th>
              <th className="px-5 py-3">Author</th>
              <th className="px-5 py-3">Urgency</th>
              <th className="px-5 py-3">Duration (Est / Act)</th>
              <th className="px-5 py-3">Cost / Scope-2</th>
              <th className="px-5 py-3">Policy Gate Decision</th>
              <th className="px-5 py-3 text-right">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/60">
            {runs.map((run) => {
              const isExpanded = expandedRunId === run.id;
              const durEst = formatDuration(run.estimated_duration_seconds);
              const durAct = run.actual_duration_seconds
                ? formatDuration(run.actual_duration_seconds)
                : null;
              const costEst = formatCurrency(run.estimated_cost_usd);
              const costAct = run.actual_cost_usd
                ? formatCurrency(run.actual_cost_usd)
                : null;
              const carbEst = formatCarbon(run.estimated_carbon_g);
              const carbAct = run.actual_carbon_g
                ? formatCarbon(run.actual_carbon_g)
                : null;

              // Initial for avatar
              const authorInitial = (run.author || "A")[0].toUpperCase();

              return (
                <React.Fragment key={run.id}>
                  <tr
                    onClick={() => toggleExpand(run.id)}
                    className={`hover:bg-surface-hover/80 transition-colors cursor-pointer group ${
                      isExpanded ? "bg-surface-muted/60" : ""
                    }`}
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <div className="text-zinc-500 group-hover:text-emerald-400 transition-colors">
                          {isExpanded ? (
                            <ChevronDown className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <ChevronRight className="w-3.5 h-3.5" />
                          )}
                        </div>
                        <div className="p-1.5 rounded bg-surface-muted border border-surface-border text-emerald-400">
                          <GitPullRequest className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="font-semibold text-zinc-100 group-hover:text-emerald-300 transition-colors">
                            {run.pr_number ? `PR #${run.pr_number}` : "Workflow Run"}
                          </div>
                          <div className="text-[11px] text-zinc-500 font-mono flex items-center gap-1">
                            <GitCommit className="w-3 h-3 text-zinc-600" />
                            <span>{(run.commit_sha || "").substring(0, 7)}</span>
                            {run.workflow_name && (
                              <span className="text-zinc-400 font-sans">
                                • {run.workflow_name}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <span className="font-medium text-zinc-200">
                        {run.repository_name || "Repository"}
                      </span>
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-5 h-5 rounded-full bg-surface-muted border border-surface-border flex items-center justify-center text-[10px] font-bold text-zinc-300">
                          {authorInitial}
                        </div>
                        <span className="text-zinc-300 font-medium">
                          {run.author}
                        </span>
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <Badge status={run.urgency || "ROUTINE"} size="sm" />
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="space-y-0.5">
                        <div className="font-mono text-zinc-200 font-medium">
                          {durAct ? (
                            <span className="text-emerald-400 font-semibold">{durAct}</span>
                          ) : (
                            <span>{durEst}</span>
                          )}
                        </div>
                        {durAct && (
                          <div className="text-[10px] text-zinc-500 font-mono">
                            Est: {durEst}
                          </div>
                        )}
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="space-y-0.5">
                        <div className="font-semibold text-zinc-100 tabular-nums">
                          {costAct || costEst}
                        </div>
                        <div className="text-[11px] text-teal-400 tabular-nums font-mono">
                          {carbAct || carbEst}
                        </div>
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="flex flex-col gap-1 items-start">
                        <Badge status={run.policy_decision} size="sm" />
                        {run.policy_reason && (
                          <span
                            className="text-[10px] text-zinc-400 max-w-xs truncate"
                            title={run.policy_reason}
                          >
                            {run.policy_reason}
                          </span>
                        )}
                      </div>
                    </td>

                    <td className="px-5 py-3.5 text-right font-mono text-[11px] text-zinc-400">
                      {formatDate(run.created_at)}
                    </td>
                  </tr>

                  {/* Expanded Telemetry Inspection Drawer */}
                  {isExpanded && (
                    <tr className="bg-surface-canvas/90">
                      <td colSpan={8} className="px-6 py-4 border-y border-surface-border">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                          {/* File Classification */}
                          <div className="p-3.5 rounded-lg bg-surface-card border border-surface-border space-y-2">
                            <div className="font-semibold text-zinc-200 flex items-center gap-1.5 pb-1 border-b border-surface-border">
                              <Layers className="w-3.5 h-3.5 text-emerald-400" />
                              PR Diff Composition
                            </div>
                            <div className="space-y-1 text-zinc-400 text-[11px]">
                              <div className="flex justify-between">
                                <span>Files Changed:</span>
                                <span className="font-mono text-zinc-200 font-semibold">{run.changed_files_count || 0}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Lines Added / Deleted:</span>
                                <span className="font-mono text-zinc-200 font-semibold">+{run.lines_added || 0} / -{run.lines_deleted || 0}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Test Files Modified:</span>
                                <span className="font-mono text-zinc-200">{run.test_files_count || 0}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>CI Configuration Files:</span>
                                <span className="font-mono text-zinc-200">{run.configuration_files_count ? `${run.configuration_files_count} (Full Matrix)` : "0 (Default Matrix)"}</span>
                              </div>
                            </div>
                          </div>

                          {/* Estimator Engine Breakdown */}
                          <div className="p-3.5 rounded-lg bg-surface-card border border-surface-border space-y-2">
                            <div className="font-semibold text-zinc-200 flex items-center gap-1.5 pb-1 border-b border-surface-border">
                              <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
                              FinOps Engine Breakdown
                            </div>
                            <div className="space-y-1 text-zinc-400 text-[11px]">
                              <div className="flex justify-between">
                                <span>Duration Estimator Model:</span>
                                <span className="font-mono text-emerald-400">Historical Median + Heuristic</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Estimated Compute Cost:</span>
                                <span className="font-mono text-zinc-200 font-semibold">{costEst}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Actual Measured Cost:</span>
                                <span className="font-mono text-zinc-200 font-semibold">{costAct || "Pending Action"}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Estimator Variance:</span>
                                <span className="font-mono text-emerald-400">
                                  {costAct
                                    ? `$${(Number(run.actual_cost_usd) - Number(run.estimated_cost_usd)).toFixed(4)}`
                                    : "0.0000"}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Carbon & Policy Audit */}
                          <div className="p-3.5 rounded-lg bg-surface-card border border-surface-border space-y-2">
                            <div className="font-semibold text-zinc-200 flex items-center gap-1.5 pb-1 border-b border-surface-border">
                              <Leaf className="w-3.5 h-3.5 text-teal-400" />
                              Scope-2 Carbon &amp; Policy Rationale
                            </div>
                            <div className="space-y-1 text-zinc-400 text-[11px]">
                              <div className="flex justify-between">
                                <span>Estimated Scope-2 Carbon:</span>
                                <span className="font-mono text-teal-300 font-semibold">{carbEst}</span>
                              </div>
                              <div className="flex justify-between">
                                <span>Actual Scope-2 Carbon:</span>
                                <span className="font-mono text-teal-300 font-semibold">{carbAct || "Pending Action"}</span>
                              </div>
                              <div className="pt-1">
                                <span className="block text-zinc-500">Evaluation Rationale:</span>
                                <span className="font-sans text-zinc-300 text-[10px] leading-relaxed block mt-0.5">
                                  {run.policy_reason || "All SPM sprint budget and carbon intensity thresholds satisfied."}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
