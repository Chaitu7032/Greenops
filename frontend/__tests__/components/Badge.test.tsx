import React from "react";
import { render, screen } from "@testing-library/react";
import { Badge } from "@/components/ui/Badge";

describe("Badge Component", () => {
  it("renders APPROVED status with green styling and check icon", () => {
    render(<Badge status="APPROVED" />);
    const label = screen.getByText("APPROVED");
    expect(label).toBeInTheDocument();
    // The parent badge wrapper contains the semantic styling
    expect(label.parentElement).toHaveClass("text-emerald-400");
    expect(label.parentElement).toHaveClass("bg-emerald-950/70");
  });

  it("renders DEFERRED status with clock styling", () => {
    render(<Badge status="DEFERRED" />);
    const label = screen.getByText("DEFERRED");
    expect(label).toBeInTheDocument();
    expect(label.parentElement).toHaveClass("text-amber-400");
    expect(label.parentElement).toHaveClass("bg-amber-950/60");
  });

  it("renders FLAGGED status with alert styling", () => {
    render(<Badge status="FLAGGED" />);
    const label = screen.getByText("FLAGGED");
    expect(label).toBeInTheDocument();
    expect(label.parentElement).toHaveClass("text-rose-400");
    expect(label.parentElement).toHaveClass("bg-rose-950/70");
  });

  it("renders urgency level HOTFIX with priority indicator", () => {
    render(<Badge status="HOTFIX" />);
    const label = screen.getByText("HOTFIX");
    expect(label).toBeInTheDocument();
    expect(label.parentElement).toHaveClass("text-rose-300");
    expect(label.parentElement).toHaveClass("font-bold");
  });

  it("renders custom status text and handles case insensitivity", () => {
    render(<Badge status="completed" />);
    const label = screen.getByText("completed");
    expect(label).toBeInTheDocument();
    expect(label.parentElement).toHaveClass("text-emerald-400");
  });

  it("supports small size variant", () => {
    render(<Badge status="ACTIVE" size="sm" />);
    const label = screen.getByText("ACTIVE");
    expect(label.parentElement).toHaveClass("text-[10px]");
  });
});
