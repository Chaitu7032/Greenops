"use client";

import React from "react";
import { Leaf } from "lucide-react";

interface LeafProgressProps {
  progress?: number; // 0 to 100. If undefined or negative, renders indeterminate spinner
  size?: number;
  label?: string;
  sublabel?: string;
}

export const LeafProgress: React.FC<LeafProgressProps> = ({
  progress,
  size = 72,
  label,
  sublabel,
}) => {
  const strokeWidth = 5;
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const isDeterminate = progress !== undefined && progress >= 0;
  const clampedProgress = isDeterminate ? Math.min(100, Math.max(0, progress)) : 0;
  const strokeDashoffset = isDeterminate
    ? circumference - (clampedProgress / 100) * circumference
    : circumference * 0.25;

  return (
    <div className="flex flex-col items-center justify-center gap-3 p-4 select-none">
      <div
        className="relative flex items-center justify-center"
        style={{ width: size, height: size }}
      >
        {/* Glow halo behind leaf */}
        <div className="absolute inset-0 rounded-full bg-emerald-500/20 blur-md animate-pulse" />

        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className={`transform -rotate-90 ${!isDeterminate ? "animate-spin" : ""}`}
          style={{ animationDuration: !isDeterminate ? "2s" : undefined }}
        >
          {/* Subtle background track circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="rgba(16, 185, 129, 0.15)"
            strokeWidth={strokeWidth}
          />
          {/* Active green progress arc with rounded caps */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="url(#leafProgressGradient)"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
          <defs>
            <linearGradient id="leafProgressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#34D399" />
              <stop offset="50%" stopColor="#10B981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
          </defs>
        </svg>

        {/* Centered breathing GreenOps Leaf icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="p-2.5 rounded-full bg-surface-canvas/90 border border-emerald-500/30 shadow-inner flex items-center justify-center animate-pulse">
            <Leaf className="w-5 h-5 text-emerald-400 fill-emerald-500/20 transform -rotate-12" />
          </div>
        </div>
      </div>

      {(label || isDeterminate) && (
        <div className="text-center">
          <div className="text-xs font-semibold text-zinc-200">
            {label || `${Math.round(clampedProgress)}%`}
          </div>
          {sublabel && (
            <div className="text-[11px] text-zinc-500 font-mono mt-0.5">{sublabel}</div>
          )}
        </div>
      )}
    </div>
  );
};
