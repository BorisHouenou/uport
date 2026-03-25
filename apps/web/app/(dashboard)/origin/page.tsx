import type { Metadata } from "next";
import { OriginWizard } from "@/components/origin/origin-wizard";

export const metadata: Metadata = { title: "Origin Determination" };

export default function OriginPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Origin Determination</h1>
        <p className="mt-1 text-sm text-slate-500">
          Evaluate Rules of Origin across all applicable trade agreements and generate a Certificate of Origin.
        </p>
      </div>
      <OriginWizard />
    </div>
  );
}
