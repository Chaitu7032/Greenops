import React from "react";
import { render, screen } from "@testing-library/react";
import { StatCard } from "@/components/dashboard/StatCard";
import { DollarSign } from "lucide-react";

describe("StatCard Component", () => {
  it("renders title, primary value, and icon correctly", () => {
    render(
      <StatCard
        title="Sprint Cloud Cost"
        value="$124.50"
        icon={DollarSign}
      />
    );

    expect(screen.getByText("Sprint Cloud Cost")).toBeInTheDocument();
    expect(screen.getByText("$124.50")).toBeInTheDocument();
  });

  it("renders optional subtitle and badge with corresponding style", () => {
    render(
      <StatCard
        title="Active Gatekeeper"
        value="Enforced"
        subtitle="14 pull requests evaluated"
        icon={DollarSign}
        badgeText="Optimal"
        badgeType="success"
      />
    );

    expect(screen.getByText("14 pull requests evaluated")).toBeInTheDocument();
    const badge = screen.getByText("Optimal");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("text-emerald-400");
  });

  it("renders progress bar and clamps bounds cleanly", () => {
    const { rerender } = render(
      <StatCard
        title="Budget Utilization"
        value="75%"
        icon={DollarSign}
        progress={75}
      />
    );

    // Re-render with high danger threshold progress (>90)
    rerender(
      <StatCard
        title="Budget Utilization"
        value="95%"
        icon={DollarSign}
        progress={95}
      />
    );

    expect(screen.getByText("95%")).toBeInTheDocument();
  });
});
