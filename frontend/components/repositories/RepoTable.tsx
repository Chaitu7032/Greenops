import React from "react";
import { RepositoryRanking } from "@/types";
import { formatCurrency, formatCarbon } from "@/lib/formatters";
import { FolderGit2, Clock, Leaf, DollarSign, ChevronRight, Globe, Layers } from "lucide-react";
import Link from "next/link";

interface RepoTableProps {
  rankings: RepositoryRanking[];
  title?: string;
  showLinkToAll?: boolean;
}

export const RepoTable: React.FC<RepoTableProps> = ({
  rankings,
  title = "Repository Consumption & SPM Governance Ranking",
  showLinkToAll = true,
}) => {
  if (!rankings || rankings.length === 0) {
    return (
      <div className="p-8 rounded-xl bg-surface-card border border-surface-border text-center text-zinc-500 text-xs">
        No tracked repositories found in active organization.
      </div>
    );
  }

  // Calculate highest spend for relative bar visualization
  const maxSpend = Math.max(...rankings.map((r) => Number(r.total_cost_usd) || 1), 1);

  return (
    <div className="rounded-xl bg-surface-card border border-surface-border overflow-hidden shadow-sm hover-card-glow transition-all">
      <div className="px-6 py-4 border-b border-surface-border flex flex-col sm:flex-row sm:items-center justify-between gap-2 bg-surface-muted/40">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
              Microservice Attribution
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Ranked by cumulative compute spend, Scope-2 carbon footprint, and deferral rate
          </p>
        </div>

        {showLinkToAll && (
          <Link
            href="/repositories"
            className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition-colors"
          >
            Hardware Specs <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-zinc-300">
          <thead className="bg-surface-canvas text-[11px] font-semibold uppercase tracking-wider text-zinc-400 border-b border-surface-border">
            <tr>
              <th className="px-5 py-3">Rank / Microservice</th>
              <th className="px-5 py-3 text-center">Total CI Runs</th>
              <th className="px-5 py-3 text-center">Deferred Jobs</th>
              <th className="px-5 py-3">Avg Duration</th>
              <th className="px-5 py-3">Compute Cost</th>
              <th className="px-5 py-3">Carbon Footprint</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-border/60">
            {rankings.map((repo, idx) => {
              const spendPercentage = ((Number(repo.total_cost_usd) || 0) / maxSpend) * 100;

              return (
                <tr
                  key={repo.id}
                  className="hover:bg-surface-hover/70 transition-colors group"
                >
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-[11px] font-bold text-emerald-400/80 w-5">
                        #{idx + 1}
                      </span>
                      <div className="p-2 rounded-lg bg-surface-muted border border-surface-border text-emerald-400 group-hover:border-emerald-500/30 transition-colors">
                        <FolderGit2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-semibold text-zinc-100 group-hover:text-emerald-300 transition-colors">
                          {repo.name}
                        </div>
                        <div className="text-[11px] text-zinc-500 font-mono">
                          {repo.full_name}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="px-5 py-3.5 text-center font-bold text-zinc-100 tabular-nums">
                    {repo.total_runs}
                  </td>

                  <td className="px-5 py-3.5 text-center">
                    {repo.deferred_count > 0 ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-amber-950/60 text-amber-300 border border-amber-800/60 tabular-nums">
                        {repo.deferred_count} deferred
                      </span>
                    ) : (
                      <span className="text-zinc-500 text-[11px]">—</span>
                    )}
                  </td>

                  <td className="px-5 py-3.5 text-zinc-300 tabular-nums font-mono">
                    {repo.avg_duration_minutes} min
                  </td>

                  <td className="px-5 py-3.5">
                    <div className="space-y-1">
                      <span className="font-bold text-zinc-100 tabular-nums">
                        {formatCurrency(repo.total_cost_usd)}
                      </span>
                      <div className="w-24 bg-surface-muted rounded-full h-1 overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, Math.max(5, spendPercentage))}%` }}
                        />
                      </div>
                    </div>
                  </td>

                  <td className="px-5 py-3.5">
                    <span className="font-semibold text-teal-400 tabular-nums font-mono">
                      {repo.total_carbon_kg} kg CO₂e
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
