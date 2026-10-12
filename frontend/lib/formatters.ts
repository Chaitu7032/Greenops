/**
 * Utility formatters for financial amounts, Scope-2 carbon, durations, and dates.
 */

export function formatCurrency(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) {
    return "$0.00";
  }
  const num = Number(amount);
  if (num < 0.01 && num > 0) {
    return `$${num.toFixed(4)}`;
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatCarbon(carbonGrams: number | string | null | undefined): string {
  if (carbonGrams === null || carbonGrams === undefined || isNaN(Number(carbonGrams))) {
    return "0 gCO₂e";
  }
  const grams = Number(carbonGrams);
  if (grams >= 1000) {
    return `${(grams / 1000).toFixed(2)} kgCO₂e`;
  }
  return `${Math.round(grams)} gCO₂e`;
}

export function formatDuration(seconds: number | string | null | undefined): string {
  if (seconds === null || seconds === undefined || isNaN(Number(seconds))) {
    return "0s";
  }
  const totalSecs = Math.round(Number(seconds));
  if (totalSecs < 60) {
    return `${totalSecs}s`;
  }
  const mins = Math.floor(totalSecs / 60);
  const remainingSecs = totalSecs % 60;
  if (remainingSecs === 0) {
    return `${mins}m`;
  }
  return `${mins}m ${remainingSecs}s`;
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "N/A";
  try {
    const d = new Date(dateStr);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }).format(d);
  } catch {
    return dateStr;
  }
}

export function formatNumber(val: number | string | null | undefined): string {
  if (val === null || val === undefined || isNaN(Number(val))) {
    return "0";
  }
  return new Intl.NumberFormat("en-US").format(Number(val));
}
