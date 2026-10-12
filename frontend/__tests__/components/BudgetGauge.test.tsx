import React from "react";
import { render, screen } from "@testing-library/react";
import { BudgetGauge } from "@/components/dashboard/BudgetGauge";

describe("BudgetGauge Component", () => {
  it("renders financial budget mode with allocated, consumed, and remaining values", () => {
    render(
      <BudgetGauge
        type="financial"
        allocated={250.0}
        consumed={125.0}
        remaining={125.0}
        percentage={50.0}
        isOverBudget={false}
      />
    );

    expect(screen.getByText("Sprint Financial Cloud Budget")).toBeInTheDocument();
    expect(screen.getByText("Governed & Normal")).toBeInTheDocument();
    // Consumed & remaining both render $125.00
    const matchedValues = screen.getAllByText("$125.00");
    expect(matchedValues.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("/ $250.00 allocated")).toBeInTheDocument();
    expect(screen.getByText("50.0%")).toBeInTheDocument();
    expect(screen.getByText("Approved to Execute")).toBeInTheDocument();
  });

  it("renders carbon budget mode with kg units", () => {
    render(
      <BudgetGauge
        type="carbon"
        allocated={50.0}
        consumed={10.0}
        remaining={40.0}
        percentage={20.0}
        isOverBudget={false}
      />
    );

    expect(screen.getByText("Sprint Cloud Carbon Budget")).toBeInTheDocument();
    expect(screen.getByText("10 kg")).toBeInTheDocument();
    expect(screen.getByText("/ 50 kg allocated")).toBeInTheDocument();
    expect(screen.getByText("40 kg")).toBeInTheDocument();
    expect(screen.getByText("20.0%")).toBeInTheDocument();
  });

  it("displays over budget warning banner when isOverBudget is true", () => {
    render(
      <BudgetGauge
        type="financial"
        allocated={100.0}
        consumed={135.0}
        remaining={0}
        percentage={135.0}
        isOverBudget={true}
      />
    );

    expect(screen.getByText("Ceiling Exceeded")).toBeInTheDocument();
    expect(screen.getByText("135.0%")).toBeInTheDocument();
    expect(screen.getByText("Auto-Deferral Active")).toBeInTheDocument();
  });

  it("handles warning tier when percentage exceeds 80% without exceeding ceiling", () => {
    render(
      <BudgetGauge
        type="financial"
        allocated={100.0}
        consumed={85.0}
        remaining={15.0}
        percentage={85.0}
        isOverBudget={false}
      />
    );

    expect(screen.getByText("Warning Tier (>80%)")).toBeInTheDocument();
    expect(screen.getByText("85.0%")).toBeInTheDocument();
  });

  it("handles zero usage and boundary values gracefully", () => {
    render(
      <BudgetGauge
        type="financial"
        allocated={100.0}
        consumed={0}
        remaining={100.0}
        percentage={0}
        isOverBudget={false}
      />
    );

    const zeroValues = screen.getAllByText("$0.00");
    expect(zeroValues.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("/ $100.00 allocated")).toBeInTheDocument();
    expect(screen.getByText("0.0%")).toBeInTheDocument();
  });
});
