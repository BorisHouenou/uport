"use client";

import { TrendingUp, DollarSign, FileCheck2, Users } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

function KpiCard({
  label,
  value,
  sub,
  icon: Icon,
  iconBg,
  iconColor,
  trend,
}: {
  label: string;
  value: string;
  sub: string;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  trend?: { up: boolean; label: string };
}) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-card card-hover">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
          <p className="mt-2 text-3xl font-bold text-[#0A0F1E] tracking-tight">{value}</p>
          <p className="mt-1 text-xs text-slate-400">{sub}</p>
        </div>
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${iconBg}`}>
          <Icon className={`h-5 w-5 ${iconColor}`} />
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1.5">
          <div className={`flex h-5 w-5 items-center justify-center rounded-full ${trend.up ? "bg-emerald-100" : "bg-red-100"}`}>
            <TrendingUp className={`h-3 w-3 ${trend.up ? "text-emerald-600" : "text-red-500 rotate-180"}`} />
          </div>
          <span className={`text-xs font-medium ${trend.up ? "text-emerald-600" : "text-red-500"}`}>{trend.label}</span>
        </div>
      )}
    </div>
  );
}

export function SavingsSummaryCard() {
  return (
    <KpiCard
      label="Tariff Savings YTD"
      value="$0"
      sub="Add shipments to start tracking"
      icon={DollarSign}
      iconBg="bg-emerald-50"
      iconColor="text-emerald-600"
    />
  );
}
