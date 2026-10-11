import React from "react";
import { DollarSign, Leaf, AlertTriangle, ShieldCheck, Gauge } from "lucide-react";
import { formatCurrency } from "@/lib/formatters";

interface BudgetGaugeProps {
  type: "financial" | "carbon";
  allocated: number | string;
  consumed: number | string;
  remaining: number | string;
  percentage: number;
  isOverBudget: boolean;
}

export const BudgetGauge: React.FC<BudgetGaugeProps> = ({
  type,
  allocated,
  consumed,
  remaining,
  percentage,
  isOverBudget,
}) => {
  const isFinancial = type === "financial";
  const title = isFinancial ? "Sprint Financial Cloud Budget" : "Sprint Cloud Carbon Budget";
  const Icon = isFinancial ? DollarSign : Leaf;

  const formattedAllocated = isFinancial ? formatCurrency(allocated) : `${allocated} kg`;
  const formattedConsumed = isFinancial ? formatCurrency(consumed) : `${consumed} kg`;
  const formattedRemaining = isFinancial ? formatCurrency(remaining) : `${remaining} kg`;

  const clampedPercentage = Math.min(100, Math.max(0, percentage));

  return (
    <div className="relative p-6 rounded-xl bg-surface-card border border-surface-border shadow-sm flex flex-col justify-between overflow-hidden hover-card-glow transition-all">
      {/* Top subtle highlight */}
      <div
        className={`absolute top-0 left-0 right-0 h-[2px] ${
          isOverBudget
            ? "bg-rose-500"
            : percentage > 80
            ? "bg-amber-500"
            : isFinancial
            ? "bg-emerald-500"
            : "bg-teal-500"
        }`}
      />

      <div>
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`p-2.5 rounded-lg border ${
                isFinancial
                  ? "bg-emerald-950/70 border-emerald-800/80 text-emerald-400"
                  : "bg-teal-950/70 border-teal-800/80 text-teal-400"
              }`}
            >
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
              <p className="text-[11px] text-zinc-400">
                Authoritative SPM Sprint Ledger • Linear Burn Thresholds
              </p>
            </div>
          </div>

          {isOverBudget ? (
            <span className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded bg-rose-950/80 text-rose-300 border border-rose-800/80">
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              Ceiling Exceeded
            </span>
          ) : percentage > 80 ? (
            <span className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded bg-amber-950/80 text-amber-300 border border-amber-800/80">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
              Warning Tier (&gt;80%)
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/80">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Governed &amp; Normal
            </span>
          )}
        </div>

        {/* Big numbers display */}
        <div className="mt-6 flex items-baseline justify-between">
          <div>
            <span className="text-3xl sm:text-4xl font-extrabold text-zinc-100 tabular-nums">
              {formattedConsumed}
            </span>
            <span className="text-xs sm:text-sm text-zinc-400 ml-2 font-mono">
              / {formattedAllocated} allocated
            </span>
          </div>

          <div className="text-right">
            <span
              className={`text-xl sm:text-2xl font-bold tabular-nums ${
                isOverBudget
                  ? "text-rose-400"
                  : percentage > 80
                  ? "text-amber-400"
                  : "text-emerald-400"
              }`}
            >
              {percentage.toFixed(1)}%
            </span>
            <span className="block text-[10px] text-zinc-400 uppercase tracking-wider">
              Consumed
            </span>
          </div>
        </div>

        {/* Visual Governance Progress Meter with threshold ticks */}
        <div className="mt-4 space-y-1.5">
          <div className="relative w-full bg-surface-muted rounded-full h-3 overflow-hidden p-0.5 border border-surface-border">
            <div
              className={`h-full rounded-full transition-all duration-700 ${
                isOverBudget
                  ? "bg-rose-500 shadow-[0_0_12px_rgba(239,68,68,0.5)]"
                  : percentage > 80
                  ? "bg-amber-500 shadow-[0_0_12px_rgba(245,158,11,0.5)]"
                  : isFinancial
                  ? "bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-400"
                  : "bg-gradient-to-r from-teal-600 via-teal-500 to-emerald-400"
              }`}
              style={{ width: `${clampedPercentage}%` }}
            />
          </div>

          {/* Threshold markers */}
          <div className="flex justify-between text-[10px] font-mono text-zinc-400 px-0.5">
            <span>0%</span>
            <span className="text-zinc-400">50%</span>
            <span className="text-amber-400">80% Warning</span>
            <span className="text-rose-400">100% Hard Cap</span>
          </div>
        </div>
      </div>

      {/* Bottom details */}
      <div className="mt-6 pt-4 border-t border-surface-border/80 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-zinc-400 block text-[11px]">Remaining Runway</span>
          <span className="font-semibold text-zinc-200 tabular-nums">
            {formattedRemaining}
          </span>
        </div>
        <div className="text-right">
          <span className="text-zinc-400 block text-[11px]">Gatekeeper Policy</span>
          <span
            className={`font-semibold text-[11px] ${
              isOverBudget ? "text-rose-400" : "text-emerald-400"
            }`}
          >
            {isOverBudget ? "Auto-Deferral Active" : "Approved to Execute"}
          </span>
        </div>
      </div>
    </div>
  );
};
