import type { Metadata } from "next";
import { SavingsSummaryCard } from "@/components/dashboard/savings-summary-card";
import { RecentCertificatesTable } from "@/components/dashboard/recent-certificates-table";
import { ComplianceHealthCard } from "@/components/dashboard/compliance-health-card";
import { QuickActions } from "@/components/dashboard/quick-actions";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 text-sm mt-1">
          Your Rules of Origin compliance overview
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SavingsSummaryCard />
        <ComplianceHealthCard />
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Recent Certificates */}
      <RecentCertificatesTable />
    </div>
  );
}
