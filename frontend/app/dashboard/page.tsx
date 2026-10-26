"use client";

import React, { useEffect, useState } from "react";
import {
  DollarSign,
  Leaf,
  GitPullRequest,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Zap,
  Sparkles,
  RefreshCw,
  TrendingDown,
  Info,
  ShieldCheck,
  Activity,
  Layers,
  Globe,
} from "lucide-react";
import { api } from "@/lib/api";
import {
  DashboardOverview,
  RepositoryRanking,
  BurnDownPoint,
  CarbonTimeSeriesPoint,
  PipelineRun,
  Sprint,
} from "@/types";
import { StatCard } from "@/components/dashboard/StatCard";
import { BudgetGauge } from "@/components/dashboard/BudgetGauge";
import { BurnDownChart } from "@/components/dashboard/BurnDownChart";
import { CarbonTrendChart } from "@/components/dashboard/CarbonTrendChart";
import { PipelineTable } from "@/components/pipelines/PipelineTable";
import { RepoTable } from "@/components/repositories/RepoTable";
import { formatCurrency, formatCarbon } from "@/lib/formatters";
import { LeafProgress } from "@/components/ui/LeafProgress";

export default function DashboardPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [rankings, setRankings] = useState<RepositoryRanking[]>([]);
  const [burnDown, setBurnDown] = useState<BurnDownPoint[]>([]);
  const [carbonTrend, setCarbonTrend] = useState<CarbonTimeSeriesPoint[]>([]);
  const [recentRuns, setRecentRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [activeSprintName, setActiveSprintName] = useState("Active Sprint");

  const loadData = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const [ov, rank, carb, runs, sprints] = await Promise.all([
        api.getDashboardOverview(),
        api.getRepositoryRankings(),
        api.getCarbonAnalytics(),
        api.getPipelines({ limit: 8 }),
        api.getSprints(),
      ]);

      setOverview(ov);
      setRankings(rank);
      setCarbonTrend(carb);
      setRecentRuns(runs);

      const activeSp = sprints.find((s) => s.status === "ACTIVE");
      if (activeSp) {
        setActiveSprintName(activeSp.name);
        const bd = await api.getSprintBurnDown(activeSp.id);
        setBurnDown(bd);
      }
    } catch (err) {
      console.error("Error loading dashboard data:", err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      loadData(true);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleSeedDemo = async () => {
    try {
      setSeeding(true);
      await api.seedDemoData();
      await loadData();
    } catch (e) {
      console.error("Seeding error:", e);
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Environmental & FinOps Command Banner */}
      <div className="relative rounded-2xl border border-surface-border p-6 sm:p-8 overflow-hidden shadow-xl bg-surface-card/80">
        {/* Background photo layer inside banner */}
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-35"
          style={{ backgroundImage: "url('/images/greenops_bg.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-surface-canvas via-surface-canvas/80 to-emerald-950/40" />

        {/* Ambient forest green glow */}
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-emerald-500/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-800/80 tracking-wide">
                SPM GOVERNANCE PLATFORM
              </span>
              <span className="text-xs font-medium text-zinc-400">
                • {activeSprintName} Active
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-zinc-100">
              GreenOps Command Center
            </h1>

            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
              Real-time CI/CD spend enforcement, regional electricity-grid carbon tracking (Electricity Maps), and sprint burn-down governance for cloud infrastructure.
            </p>
          </div>

          {/* Quick Actions & Live Telemetry Button */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => loadData()}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-surface-muted/90 hover:bg-surface-hover border border-surface-border text-xs font-semibold text-zinc-200 transition-all shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-emerald-400 ${loading ? "animate-spin" : ""}`} />
              <span>Sync Telemetry</span>
            </button>

            <button
              onClick={handleSeedDemo}
              disabled={seeding}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-xs font-bold text-zinc-950 shadow-md shadow-emerald-950/80 transition-all transform active:scale-95"
            >
              <Sparkles className="w-3.5 h-3.5 fill-zinc-950" />
              <span>{seeding ? "Seeding Database..." : "Seed SPM Demo Telemetry"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* SPM Academic Targets & Authoritative Precision Notice */}
      <div className="p-4 rounded-xl bg-surface-card/60 border border-surface-border flex items-start gap-3 text-xs text-zinc-400">
        <Info className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <span className="font-semibold text-zinc-200">SPM Governance Targets: </span>
          Guiding engineering teams to a 15–25% reduction in non-essential CI compute spend &amp; 30% reduction in Scope-2 CO₂ emissions by deferring routine jobs to clean energy grid windows. All calculations derived from authoritative PostgreSQL ledger entries.
        </div>
      </div>

      {/* LeafProgress Loading Animation */}
      {loading && !overview ? (
        <div className="py-20 flex flex-col items-center justify-center">
          <LeafProgress size={88} label="Synchronizing SPM Telemetry..." sublabel="Connecting to SQLite ledger & live grid intensity" />
        </div>
      ) : (
        <>
          {/* Top 4 KPI Metric Cards */}
          {overview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="CI/CD Pipelines Evaluated"
            value={overview.total_runs_count}
            subtitle={`${overview.approved_runs_count} Approved • ${overview.deferred_runs_count} Deferred`}
            icon={GitPullRequest}
            badgeText="Automated Gate"
            badgeType="success"
            progress={overview.total_runs_count > 0 ? (overview.approved_runs_count / overview.total_runs_count) * 100 : 0}
          />

          <StatCard
            title="Quantified FinOps Savings"
            value={formatCurrency(overview.estimated_savings_usd)}
            subtitle="Prevented runaway runs & deferred cost"
            icon={DollarSign}
            badgeText="Avoided Spend"
            badgeType="success"
            progress={Math.min(100, Math.max(5, Number(overview.financial_percentage)))}
          />

          <StatCard
            title="Scope-2 Carbon Avoided"
            value={`${overview.carbon_avoided_kg} kg`}
            subtitle="Shifted compute to lower-carbon hours"
            icon={Leaf}
            badgeText="Clean Energy"
            badgeType="success"
            progress={Math.min(100, Math.max(5, Number(overview.carbon_percentage)))}
          />

          <StatCard
            title={`Grid Carbon (${overview.grid_region})`}
            value={`${Number(overview.current_grid_intensity).toFixed(1)} g`}
            subtitle={
              overview.is_grid_data_stale
                ? "Cached / regional baseline fallback"
                : "Live Electricity Maps API stream"
            }
            icon={Zap}
            badgeText={overview.is_grid_data_stale ? "Stale Cached" : "Live Grid"}
            badgeType={overview.is_grid_data_stale ? "warning" : "neutral"}
            progress={Math.min(100, (Number(overview.current_grid_intensity) / 500) * 100)}
          />
        </div>
      )}

      {/* Sprint Financial & Carbon Budget Governance Gauges */}
      {overview && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <BudgetGauge
            type="financial"
            allocated={overview.financial_budget_usd}
            consumed={overview.financial_consumed_usd}
            remaining={overview.financial_remaining_usd}
            percentage={overview.financial_percentage}
            isOverBudget={overview.financial_over_budget}
          />

          <BudgetGauge
            type="carbon"
            allocated={overview.carbon_budget_kg}
            consumed={overview.carbon_consumed_kg}
            remaining={overview.carbon_remaining_kg}
            percentage={overview.carbon_percentage}
            isOverBudget={overview.carbon_over_budget}
          />
        </div>
      )}

      {/* Charts Section: Sprint Burn-Down & Carbon Emissions Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BurnDownChart
          data={burnDown}
          title={`Sprint Financial Burn-Down (${activeSprintName})`}
        />
        <CarbonTrendChart data={carbonTrend} />
      </div>

      {/* Microservice Repositories Consumption Ranking */}
      <RepoTable rankings={rankings} />

      {/* Live CI/CD Pipeline Telemetry Audit Table */}
      <PipelineTable runs={recentRuns} />
        </>
      )}
    </div>
  );
}
