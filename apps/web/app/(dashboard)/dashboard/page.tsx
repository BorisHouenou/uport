import type { Metadata } from "next";
import { SavingsSummaryCard } from "@/components/dashboard/savings-summary-card";
import { ComplianceHealthCard, CertificatesIssuedCard, ActiveSuppliersCard } from "@/components/dashboard/compliance-health-card";
import { RecentCertificatesTable } from "@/components/dashboard/recent-certificates-table";
import { QuickActions } from "@/components/dashboard/quick-actions";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-[#0A0F1E] tracking-tight">Overview</h1>
        <p className="mt-1 text-sm text-slate-400">
          Your Rules of Origin compliance at a glance
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SavingsSummaryCard />
        <ComplianceHealthCard />
        <CertificatesIssuedCard />
        <ActiveSuppliersCard />
      </div>

      {/* Quick Actions */}
      <div>
        <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Quick Actions</p>
        <QuickActions />
      </div>

      {/* Recent Certificates */}
      <RecentCertificatesTable />
    </div>
  );
}
