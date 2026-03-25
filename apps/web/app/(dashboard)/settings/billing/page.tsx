import type { Metadata } from "next";
import { PricingPanel } from "@/components/billing/pricing-panel";

export const metadata: Metadata = { title: "Billing" };

export default function BillingPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Billing & Plans</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage your subscription, upgrade your plan, or update payment details.
        </p>
      </div>
      <PricingPanel />
    </div>
  );
}
