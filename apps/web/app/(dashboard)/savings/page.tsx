import type { Metadata } from "next";
import { SavingsDashboard } from "@/components/savings/savings-dashboard";
import { Button } from "@/components/ui/button";
import { Download } from "lucide-react";

export const metadata: Metadata = { title: "Savings" };

export default function SavingsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#0A0F1E] tracking-tight">Savings Dashboard</h1>
          <p className="mt-1 text-sm text-slate-400">
            Tariff savings captured through preferential trade agreement rates
          </p>
        </div>
        <Button className="btn-primary gap-2">
          <Download className="h-4 w-4" />
          Export Report
        </Button>
      </div>
      <SavingsDashboard />
    </div>
  );
}
