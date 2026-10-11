"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Repository, RepositoryRanking } from "@/types";
import { RepoTable } from "@/components/repositories/RepoTable";
import { FolderGit2, Cpu, Zap, Globe, RefreshCw, Server, Layers, ShieldCheck } from "lucide-react";
import { formatCurrency } from "@/lib/formatters";

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [rankings, setRankings] = useState<RepositoryRanking[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [repoList, rankList] = await Promise.all([
        api.getRepositories(),
        api.getRepositoryRankings(),
      ]);
      setRepos(repoList);
      setRankings(rankList);
    } catch (e) {
      console.error("Error loading repos:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">
              Microservice Repositories &amp; Hardware Specs
            </h1>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-surface-muted text-emerald-400 border border-surface-border">
              {repos.length} Repositories
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Compute runner profiles, server wattage power models (PUE), minute cost rates, and FinOps consumption per repository.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-card border border-surface-border hover:bg-surface-hover text-xs font-semibold text-zinc-300 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Repository Governance Rankings */}
      <RepoTable rankings={rankings} showLinkToAll={false} />

      {/* Repository Hardware & Energy Profiles */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-zinc-100 flex items-center gap-2">
              <Server className="w-4 h-4 text-emerald-400" />
              Infrastructure Runner Specifications &amp; Energy Models
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Configured CI runner specs, baseline idle draws, max utilization wattages, and regional grid assignments
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="p-5 rounded-xl bg-surface-card border border-surface-border flex flex-col justify-between hover-card-glow transition-all"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2 rounded-lg bg-surface-muted border border-surface-border text-emerald-400">
                      <FolderGit2 className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="font-semibold text-sm text-zinc-100">{repo.name}</span>
                      <div className="text-[11px] text-zinc-500 font-mono">{repo.full_name}</div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-surface-muted text-zinc-300 border border-surface-border">
                    {repo.default_branch}
                  </span>
                </div>

                <div className="mt-4 space-y-2.5 text-xs text-zinc-300 pt-3 border-t border-surface-border/60">
                  <div className="flex items-center justify-between py-0.5">
                    <span className="text-zinc-400 flex items-center gap-1.5 text-[11px]">
                      <Globe className="w-3.5 h-3.5 text-teal-400" /> Runner Region
                    </span>
                    <span className="font-mono text-zinc-200 font-semibold px-2 py-0.5 rounded bg-surface-muted text-[11px]">
                      {repo.runner_region}
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-0.5">
                    <span className="text-zinc-400 flex items-center gap-1.5 text-[11px]">
                      <Cpu className="w-3.5 h-3.5 text-emerald-400" /> Hardware Allocation
                    </span>
                    <span className="font-mono text-zinc-200 text-[11px]">
                      {repo.cpu_cores} vCPUs • {Number(repo.memory_gb).toFixed(0)} GB RAM
                    </span>
                  </div>

                  <div className="flex items-center justify-between py-0.5">
                    <span className="text-zinc-400 flex items-center gap-1.5 text-[11px]">
                      <Zap className="w-3.5 h-3.5 text-amber-400" /> Power Draw Profile
                    </span>
                    <span className="font-mono text-zinc-200 text-[11px]">
                      {repo.power_idle_watts}W idle / {repo.power_max_watts}W max (PUE {repo.pue})
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-surface-border/60">
                    <span className="text-zinc-400 text-[11px]">Instance Minute Rate</span>
                    <span className="font-mono font-bold text-emerald-400 text-xs">
                      ${Number(repo.cost_per_minute).toFixed(4)} / min
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
