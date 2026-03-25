"use client";

import { useState } from "react";
import { FileDropzone } from "@/components/forms/file-dropzone";
import { BOMItemsTable } from "./bom-items-table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useUploadBOM, useBOMItems } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { ArrowRight, PackageSearch } from "lucide-react";
import toast from "react-hot-toast";

const DEMO_PRODUCT_ID = "00000000-0000-0000-0000-000000000001";

export function BOMUploadPanel() {
  const [productId] = useState(DEMO_PRODUCT_ID);
  const [taskId, setTaskId] = useState<string | null>(null);

  const uploadBOM = useUploadBOM();
  const { data: bomData, isLoading } = useBOMItems(productId);

  const handleUpload = async (file: File) => {
    const result = await uploadBOM.mutateAsync({ productId, file });
    setTaskId(result.task_id);
    toast.success("BOM uploaded — classifying HS codes…");
  };

  return (
    <div className="space-y-6">
      {/* Upload card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PackageSearch className="h-5 w-5 text-brand-600" />
            Upload Bill of Materials
          </CardTitle>
          <CardDescription>
            Supports CSV, Excel (.xlsx), and JSON exports from any ERP system.
            We auto-detect column names and classify HS codes with AI.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FileDropzone
            onUpload={handleUpload}
            label="Drop your BOM file here"
            hint="CSV, Excel (.xlsx/.xls), or JSON · Max 10 MB · Any ERP format"
          />

          {/* Column mapping hint */}
          <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-4">
            <p className="text-xs font-medium text-slate-600 mb-2">Expected columns (flexible naming):</p>
            <div className="grid grid-cols-3 gap-1 text-xs text-slate-500">
              {[
                ["description / product / item", "Required"],
                ["quantity / qty / amount",       "Optional"],
                ["unit_cost / price / value",      "Optional"],
                ["origin_country / coo / made_in", "Recommended"],
                ["hs_code / tariff_code / hts",    "Optional (AI fills in)"],
                ["currency",                        "Optional (default USD)"],
              ].map(([col, req]) => (
                <div key={col} className="flex items-start gap-1">
                  <code className="font-mono text-brand-600">{col}</code>
                  <span className="text-slate-400">· {req}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results table */}
      {(bomData?.items?.length > 0 || isLoading) && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>BOM Line Items</CardTitle>
                <CardDescription>
                  {bomData?.total_items ?? "—"} items · Foreign content:{" "}
                  <span className="font-semibold text-slate-700">
                    {bomData?.foreign_content_pct ?? "—"}%
                  </span>
                </CardDescription>
              </div>
              <Button size="sm" className="gap-1.5">
                Run Origin Check <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <BOMItemsTable items={bomData?.items ?? []} isLoading={isLoading} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
