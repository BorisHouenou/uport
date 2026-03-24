import type { Metadata } from "next";

export const metadata: Metadata = { title: "Origin Determination" };

export default function OriginPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Origin Determination</h1>
        <p className="text-slate-500 text-sm mt-1">
          Determine Rules of Origin compliance across all applicable trade agreements
        </p>
      </div>
      {/* Sprint 3–4: OriginWizard component */}
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-12 text-center text-slate-400">
        Origin determination wizard — Sprint 3
      </div>
    </div>
  );
}
