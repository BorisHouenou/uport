"use client";

import { TrendingUp } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

export function SavingsSummaryCard() {
  // TODO Sprint 5–6: fetch from /api/v1/savings/summary
  const mockSavings = 134000;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">Annual Savings</p>
        <div className="rounded-lg bg-green-50 p-2">
          <TrendingUp className="h-4 w-4 text-green-600" />
        </div>
      </div>
      <p className="mt-3 text-3xl font-bold text-slate-900">{formatCurrency(mockSavings)}</p>
      <p className="mt-1 text-xs text-slate-400">Average per SME exporter</p>
    </div>
  );
}
