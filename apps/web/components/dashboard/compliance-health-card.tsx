"use client";

import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

export function ComplianceHealthCard() {
  const score = 94; // TODO: fetch from API

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-slate-500">Compliance Score</p>
        <div className="rounded-lg bg-brand-50 p-2">
          <ShieldCheck className="h-4 w-4 text-brand-600" />
        </div>
      </div>
      <div className="mt-3 flex items-end gap-2">
        <p className="text-3xl font-bold text-slate-900">{score}%</p>
        <span
          className={cn(
            "mb-1 rounded-full px-2 py-0.5 text-xs font-medium",
            score >= 90 ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"
          )}
        >
          {score >= 90 ? "Excellent" : "Good"}
        </span>
      </div>
      <p className="mt-1 text-xs text-slate-400">Across all active agreements</p>
    </div>
  );
}
