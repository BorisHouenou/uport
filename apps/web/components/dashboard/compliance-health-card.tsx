"use client";

import { ShieldCheck, FileCheck2, Users } from "lucide-react";

function KpiCard({
  label,
  value,
  sub,
  icon: Icon,
  iconBg,
  iconColor,
  badge,
}: {
  label: string;
  value: string;
  sub: string;
  icon: React.ElementType;
  iconBg: string;
  iconColor: string;
  badge?: { label: string; color: string };
}) {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-card card-hover">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
          <div className="mt-2 flex items-end gap-2">
            <p className="text-3xl font-bold text-[#0A0F1E] tracking-tight">{value}</p>
            {badge && (
              <span className={`mb-0.5 rounded-full px-2 py-0.5 text-[10px] font-semibold ${badge.color}`}>
                {badge.label}
              </span>
            )}
          </div>
          <p className="mt-1 text-xs text-slate-400">{sub}</p>
        </div>
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${iconBg}`}>
          <Icon className={`h-5 w-5 ${iconColor}`} />
        </div>
      </div>
    </div>
  );
}

export function ComplianceHealthCard() {
  return (
    <KpiCard
      label="Compliance Rate"
      value="—"
      sub="No determinations yet"
      icon={ShieldCheck}
      iconBg="bg-blue-50"
      iconColor="text-[#2563EB]"
    />
  );
}

export function CertificatesIssuedCard() {
  return (
    <KpiCard
      label="Certificates Issued"
      value="0"
      sub="This month"
      icon={FileCheck2}
      iconBg="bg-violet-50"
      iconColor="text-violet-600"
    />
  );
}

export function ActiveSuppliersCard() {
  return (
    <KpiCard
      label="Active Suppliers"
      value="0"
      sub="Origin declarations on file"
      icon={Users}
      iconBg="bg-amber-50"
      iconColor="text-amber-600"
    />
  );
}
