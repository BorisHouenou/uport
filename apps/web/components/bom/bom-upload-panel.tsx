"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileDropzone } from "@/components/forms/file-dropzone";
import { BOMItemsTable } from "./bom-items-table";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useUploadBOM, useBOMItems, useCreateProduct, useProducts, useCreateShipment } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { ArrowRight, PackageSearch, Plus, ChevronDown } from "lucide-react";
import toast from "react-hot-toast";

const COUNTRIES = [
  { code: "CA", name: "Canada" },
  { code: "US", name: "United States" },
  { code: "MX", name: "Mexico" },
  { code: "DE", name: "Germany" },
  { code: "FR", name: "France" },
  { code: "GB", name: "United Kingdom" },
  { code: "JP", name: "Japan" },
  { code: "KR", name: "South Korea" },
];

export function BOMUploadPanel() {
  const router = useRouter();

  // Product selection state
  const [productId, setProductId] = useState<string | null>(null);
  const [showNewProduct, setShowNewProduct] = useState(false);
  const [newProductName, setNewProductName] = useState("");
  const [newProductOrigin, setNewProductOrigin] = useState("CA");

  // Origin check state
  const [showOriginDialog, setShowOriginDialog] = useState(false);
  const [destination, setDestination] = useState("US");

  const { data: products = [] } = useProducts();
  const createProduct = useCreateProduct();
  const uploadBOM = useUploadBOM();
  const createShipment = useCreateShipment();
  const { data: bomData, isLoading: bomLoading } = useBOMItems(productId);

  const handleCreateProduct = async () => {
    if (!newProductName.trim()) { toast.error("Enter a product name"); return; }
    try {
      const p = await createProduct.mutateAsync({
        name: newProductName.trim(),
        origin_country: newProductOrigin,
      });
      setProductId(p.id);
      setShowNewProduct(false);
      setNewProductName("");
      toast.success(`Product "${p.name}" created`);
    } catch {
      toast.error("Failed to create product");
    }
  };

  const handleUpload = async (file: File) => {
    if (!productId) { toast.error("Select or create a product first"); return; }
    await uploadBOM.mutateAsync({ productId, file });
    toast.success("BOM uploaded — classifying HS codes…");
  };

  const handleRunOriginCheck = async () => {
    if (!productId) return;
    try {
      const shipment = await createShipment.mutateAsync({
        product_id: productId,
        destination_country: destination,
        origin_country: (products as any[]).find(p => p.id === productId)?.origin_country || "CA",
      });
      router.push(`/origin?shipment_id=${shipment.id}&run=1`);
    } catch {
      toast.error("Failed to create shipment");
    }
  };

  const selectedProduct = (products as any[]).find(p => p.id === productId);

  return (
    <div className="space-y-6">
      {/* Step 1: Product selector */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PackageSearch className="h-5 w-5 text-brand-600" />
            Select Product
          </CardTitle>
          <CardDescription>Choose an existing product or create a new one to attach this BOM to.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Existing products */}
          {(products as any[]).length > 0 && (
            <div className="grid gap-2">
              {(products as any[]).map((p: any) => (
                <button
                  key={p.id}
                  onClick={() => setProductId(p.id)}
                  className={`flex items-center justify-between rounded-lg border px-4 py-3 text-left text-sm transition-colors ${
                    productId === p.id
                      ? "border-brand-500 bg-brand-50 text-brand-700"
                      : "border-slate-200 bg-white hover:border-slate-300"
                  }`}
                >
                  <div>
                    <p className="font-medium text-slate-900">{p.name}</p>
                    {p.hs_code && <p className="text-xs text-slate-500">HS {p.hs_code} · {p.origin_country}</p>}
                  </div>
                  {productId === p.id && <div className="h-2 w-2 rounded-full bg-brand-500" />}
                </button>
              ))}
            </div>
          )}

          {/* New product form */}
          {showNewProduct ? (
            <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 space-y-3">
              <p className="text-xs font-medium text-slate-600">New product</p>
              <input
                type="text"
                placeholder="Product name (e.g. Laptop 14'')"
                value={newProductName}
                onChange={e => setNewProductName(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                autoFocus
              />
              <div className="flex items-center gap-2">
                <select
                  value={newProductOrigin}
                  onChange={e => setNewProductOrigin(e.target.value)}
                  className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                >
                  {COUNTRIES.map(c => (
                    <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                  ))}
                </select>
                <Button size="sm" onClick={handleCreateProduct} loading={createProduct.isPending}>
                  Create
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setShowNewProduct(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowNewProduct(true)}
              className="flex w-full items-center gap-2 rounded-lg border border-dashed border-slate-300 px-4 py-3 text-sm text-slate-500 hover:border-brand-400 hover:text-brand-600 transition-colors"
            >
              <Plus className="h-4 w-4" /> New product
            </button>
          )}
        </CardContent>
      </Card>

      {/* Step 2: BOM upload (only when product selected) */}
      {productId && (
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
      )}

      {/* Step 3: BOM results + Run Origin Check */}
      {productId && (bomData?.items?.length > 0 || bomLoading) && (
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

              {!showOriginDialog ? (
                <Button size="sm" className="gap-1.5" onClick={() => setShowOriginDialog(true)}>
                  Run Origin Check <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              ) : (
                <div className="flex items-center gap-2">
                  <select
                    value={destination}
                    onChange={e => setDestination(e.target.value)}
                    className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  >
                    {COUNTRIES.filter(c => c.code !== (selectedProduct?.origin_country || "CA")).map(c => (
                      <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                    ))}
                  </select>
                  <Button
                    size="sm"
                    className="gap-1.5"
                    onClick={handleRunOriginCheck}
                    loading={createShipment.isPending}
                  >
                    Go <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setShowOriginDialog(false)}>
                    Cancel
                  </Button>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <BOMItemsTable items={bomData?.items ?? []} isLoading={bomLoading} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
