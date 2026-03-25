"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRunDetermination } from "@/hooks/use-api";
import toast from "react-hot-toast";
import { ArrowRight, ShieldCheck } from "lucide-react";

const COUNTRIES = [
  { code: "US", name: "United States" },
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
}

export function ShipmentForm({ onSubmit }: ShipmentFormProps) {
  const [shipmentId, setShipmentId] = useState("");
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
    } catch {
      toast.error("Failed to start determination — check shipment ID");
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
          Enter the shipment ID and destination. We will automatically identify applicable trade agreements.
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
                placeholder="e.g. SH-2026-001"
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
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

          {/* Agreement filter (optional) */}
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
