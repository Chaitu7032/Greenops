import React from "react";
import { CheckCircle2, Clock, AlertTriangle, XCircle, ShieldCheck, Zap } from "lucide-react";

interface BadgeProps {
  status: "APPROVED" | "DEFERRED" | "FLAGGED" | "COMPLETED" | "PENDING" | "ACTIVE" | "HOTFIX" | "BLOCKING" | "ROUTINE" | string;
  className?: string;
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({ status, className = "", size = "md" }) => {
  const norm = (status || "").toUpperCase();

  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs";

  if (norm === "APPROVED" || norm === "COMPLETED" || norm === "ACTIVE" || norm === "SUCCESS") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-emerald-950/70 text-emerald-400 border border-emerald-800/80 shadow-sm ${sizeClasses} ${className}`}
      >
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
        <span className="tracking-tight">{status}</span>
      </span>
    );
  }

  if (norm === "DEFERRED") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-amber-950/60 text-amber-400 border border-amber-800/80 shadow-sm ${sizeClasses} ${className}`}
      >
        <Clock className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
        <span className="tracking-tight">{status}</span>
      </span>
    );
  }

  if (norm === "FLAGGED" || norm === "FAILED" || norm === "BLOCKED") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-rose-950/70 text-rose-400 border border-rose-800/80 shadow-sm ${sizeClasses} ${className}`}
      >
        <AlertTriangle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
        <span className="tracking-tight">{status}</span>
      </span>
    );
  }

  if (norm === "HOTFIX") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-bold rounded-md bg-rose-950/80 text-rose-300 border border-rose-700/80 shadow-sm ${sizeClasses} ${className}`}
      >
        <Zap className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
        <span className="tracking-tight">{status}</span>
      </span>
    );
  }

  if (norm === "BLOCKING") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-semibold rounded-md bg-amber-950/70 text-amber-300 border border-amber-700/80 shadow-sm ${sizeClasses} ${className}`}
      >
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
        <span className="tracking-tight">{status}</span>
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 font-medium rounded-md bg-surface-muted text-zinc-300 border border-surface-border ${sizeClasses} ${className}`}
    >
      <span className="tracking-tight">{status}</span>
    </span>
  );
};
