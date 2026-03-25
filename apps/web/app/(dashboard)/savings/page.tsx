import type { Metadata } from "next";
import { SavingsDashboard } from "@/components/savings/savings-dashboard";

export const metadata: Metadata = { title: "Savings" };

export default function SavingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Savings Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Tariff savings captured through preferential trade agreement rates.
        </p>
      </div>
      <SavingsDashboard />
    </div>
  );
}
