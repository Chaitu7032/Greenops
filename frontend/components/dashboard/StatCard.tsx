import React from "react";
import { LucideIcon, TrendingUp, TrendingDown } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badgeText?: string;
  badgeType?: "success" | "warning" | "danger" | "neutral";
  progress?: number;
  trend?: {
    value: string;
    isPositive?: boolean;
    label: string;
  };
  sparklineData?: number[];
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeText,
  badgeType = "neutral",
  progress,
  trend,
  sparklineData,
}) => {
  const badgeClasses = {
    success: "bg-emerald-950/80 text-emerald-400 border-emerald-800/80",
    warning: "bg-amber-950/80 text-amber-400 border-amber-800/80",
    danger: "bg-rose-950/80 text-rose-400 border-rose-800/80",
    neutral: "bg-surface-muted text-zinc-300 border-surface-border",
  }[badgeType];

  return (
    <div className="relative p-5 rounded-xl bg-surface-card border border-surface-border shadow-sm hover-card-glow transition-all flex flex-col justify-between overflow-hidden">
      {/* Subtle top edge accent for visual precision */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent" />

      <div>
        <div className="flex items-center justify-between gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">
            {title}
          </span>
          <div className="p-2 rounded-lg bg-surface-muted/90 text-emerald-400 border border-surface-border flex-shrink-0">
            <Icon className="w-4 h-4" />
          </div>
        </div>

        <div className="mt-3 flex items-baseline justify-between gap-2">
          <div className="text-2xl sm:text-3xl font-bold tracking-tight text-zinc-100 tabular-nums">
            {value}
          </div>

          {badgeText && (
            <span
              className={`text-[10px] font-semibold px-2 py-0.5 rounded border tracking-tight ${badgeClasses}`}
            >
              {badgeText}
            </span>
          )}
        </div>

        {subtitle && (
          <p className="mt-1.5 text-xs text-zinc-400 line-clamp-1">
            {subtitle}
          </p>
        )}
      </div>

      {/* Sparkline or Progress Bar */}
      {sparklineData && sparklineData.length > 0 ? (
        <div className="mt-4 pt-2 border-t border-surface-border/60 flex items-center justify-between">
          <div className="w-24 h-6">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 100 24">
              <path
                d={`M 0,${24 - (sparklineData[0] || 0)} ${sparklineData
                  .map((d, i) => `L ${(i / (sparklineData.length - 1)) * 100},${24 - d}`)
                  .join(" ")}`}
                fill="none"
                stroke="#10B981"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          {trend && (
            <div className="flex items-center gap-1 text-[10px] font-medium text-emerald-400">
              <TrendingDown className="w-3 h-3" />
              <span>{trend.value}</span>
            </div>
          )}
        </div>
      ) : progress !== undefined ? (
        <div className="mt-4 pt-2 border-t border-surface-border/60">
          <div className="w-full bg-surface-muted rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                progress > 90
                  ? "bg-rose-500"
                  : progress > 75
                  ? "bg-amber-500"
                  : "bg-emerald-500"
              }`}
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
        </div>
      ) : null}
    </div>
  );
};
