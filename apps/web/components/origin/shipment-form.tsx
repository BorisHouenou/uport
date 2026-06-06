"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRunDetermination } from "@/hooks/use-api";
import toast from "react-hot-toast";
import { ArrowRight, ShieldCheck } from "lucide-react";

const COUNTRIES = [
  { code: "US", name: "United States" },
  { code: "CA", name: "Canada" },
  { code: "MX", name: "Mexico" },
  { code: "DE", name: "Germany" },
  { code: "FR", name: "France" },
  { code: "GB", name: "United Kingdom" },
  { code: "JP", name: "Japan" },
  { code: "AU", name: "Australia" },
  { code: "KR", name: "South Korea" },
];

const AGREEMENTS = ["cusma", "ceta", "cptpp", "ckfta"];

interface ShipmentFormProps {
  onSubmit: (taskId: string) => void;
  prefilledShipmentId?: string;
}

export function ShipmentForm({ onSubmit, prefilledShipmentId }: ShipmentFormProps) {
  const [shipmentId, setShipmentId] = useState(prefilledShipmentId ?? "");
  const [destination, setDestination] = useState("US");
  const [selectedAgreements, setSelectedAgreements] = useState<string[]>([]);
  const runDetermination = useRunDetermination();

  const toggleAgreement = (code: string) => {
    setSelectedAgreements(prev =>
      prev.includes(code) ? prev.filter(a => a !== code) : [...prev, code]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!shipmentId.trim()) { toast.error("Enter a shipment ID"); return; }
    try {
      const result = await runDetermination.mutateAsync({
        shipment_id: shipmentId,
        agreement_codes: selectedAgreements,
      });
      onSubmit(result.task_id);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.message || "Unknown error";
      toast.error(`Determination failed: ${detail}`);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-brand-600" />
          Shipment Details
        </CardTitle>
        <CardDescription>
          {prefilledShipmentId
            ? "Shipment pre-loaded from your BOM. Select trade agreements and run."
            : "Enter the shipment ID and destination. We will automatically identify applicable trade agreements."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            {/* Shipment ID */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-700">Shipment ID</label>
              <input
                type="text"
                value={shipmentId}
                onChange={e => setShipmentId(e.target.value)}
                placeholder="UUID from shipment record"
                readOnly={!!prefilledShipmentId}
                className={`w-full rounded-lg border px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 ${
                  prefilledShipmentId
                    ? "border-brand-200 bg-brand-50 text-brand-700 cursor-default"
                    : "border-slate-200 bg-white"
                }`}
              />
            </div>

            {/* Destination */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-700">Destination Country</label>
              <select
                value={destination}
                onChange={e => setDestination(e.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              >
                {COUNTRIES.map(c => (
                  <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
                ))}
              </select>
            </div>
          </div>

          {/* Agreement filter */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-700">
              Trade Agreements{" "}
              <span className="font-normal text-slate-400">(optional — leave blank to auto-detect)</span>
            </label>
            <div className="flex flex-wrap gap-2">
              {AGREEMENTS.map(code => (
                <button
                  type="button"
                  key={code}
                  onClick={() => toggleAgreement(code)}
                  className={`rounded-lg border px-3 py-1.5 text-xs font-semibold uppercase tracking-wide transition-colors ${
                    selectedAgreements.includes(code)
                      ? "border-brand-500 bg-brand-600 text-white"
                      : "border-slate-200 bg-white text-slate-600 hover:border-brand-300"
                  }`}
                >
                  {code}
                </button>
              ))}
            </div>
          </div>

          <Button
            type="submit"
            loading={runDetermination.isPending}
            className="w-full"
          >
            Run Origin Determination <ArrowRight className="h-4 w-4" />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
