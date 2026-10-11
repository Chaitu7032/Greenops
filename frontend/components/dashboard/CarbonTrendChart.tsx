"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { CarbonTimeSeriesPoint } from "@/types";
import { Leaf, Activity } from "lucide-react";

interface CarbonTrendChartProps {
  data: CarbonTimeSeriesPoint[];
  title?: string;
}

export const CarbonTrendChart: React.FC<CarbonTrendChartProps> = ({
  data,
  title = "Scope-2 Carbon Emissions Trend (kgCO₂e)",
}) => {
  if (!data || data.length === 0) {
    return (
      <div className="p-8 rounded-xl bg-surface-card border border-surface-border flex flex-col items-center justify-center h-72 text-zinc-500 text-xs">
        <Leaf className="w-8 h-8 text-zinc-600 mb-2 stroke-[1.5]" />
        <span>No carbon emission telemetry available for current timeframe.</span>
      </div>
    );
  }

  return (
    <div className="p-6 rounded-xl bg-surface-card border border-surface-border flex flex-col justify-between shadow-sm hover-card-glow transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-zinc-100">{title}</h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-950/60 text-teal-400 border border-teal-800/60">
              Scope-2 Standard
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-0.5">
            Daily CI/CD compute carbon footprint combined with regional grid emissions
          </p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 12, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="carbonEnterpriseGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#14B8A6" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#14B8A6" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#16221E" vertical={false} />
            <XAxis
              dataKey="date"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#1C2A26" }}
            />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: "#1C2A26" }}
              tickFormatter={(v) => `${v}kg`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0A0F0D",
                borderColor: "#1C2A26",
                borderRadius: "8px",
                fontSize: "12px",
                boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.7)",
              }}
              labelStyle={{ color: "#E2E8F0", fontWeight: 600, marginBottom: "4px" }}
              formatter={(value: any, name: any) => [
                name === "emissions_kg"
                  ? `${Number(value).toFixed(3)} kg CO₂e`
                  : `${Number(value).toFixed(1)} g/kWh`,
                name === "emissions_kg" ? "Daily Emissions" : "Avg Grid Intensity",
              ]}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", paddingTop: "12px" }}
              iconType="circle"
            />
            <Area
              type="monotone"
              dataKey="emissions_kg"
              name="Emissions (kg CO₂e)"
              stroke="#14B8A6"
              fillOpacity={1}
              fill="url(#carbonEnterpriseGradient)"
              strokeWidth={2}
              activeDot={{ r: 5, fill: "#2DD4BF" }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
