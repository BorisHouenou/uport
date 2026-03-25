import type { Metadata } from "next";
import { BOMUploadPanel } from "@/components/bom/bom-upload-panel";

export const metadata: Metadata = { title: "Bill of Materials" };

export default function BOMPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Bill of Materials</h1>
        <p className="mt-1 text-sm text-slate-500">
          Upload a BOM to classify HS codes and calculate regional value content automatically.
        </p>
      </div>
      <BOMUploadPanel />
    </div>
  );
}
