"use client";

import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { Progress } from "@/components/ui/progress";
import { formatCurrency } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface BOMItem {
  id: string;
  description: string;
  hs_code: string | null;
  hs_confidence: number | null;
  origin_country: string;
  quantity: number;
  unit_cost: number;
  currency: string;
  is_originating: boolean | null;
  classified_by: string;
}

interface BOMItemsTableProps {
  items: BOMItem[];
  isLoading?: boolean;
}

function OriginBadge({ is_originating }: { is_originating: boolean | null }) {
  if (is_originating === true)  return <Badge variant="success">Originating</Badge>;
  if (is_originating === false) return <Badge variant="destructive">Non-originating</Badge>;
  return <Badge variant="outline">Unknown</Badge>;
}

function ConfidencePill({ confidence }: { confidence: number | null }) {
  if (confidence === null) return <span className="text-slate-300">—</span>;
  const pct = Math.round(confidence * 100);
  return (
    <div className="flex items-center gap-2 min-w-[80px]">
      <Progress
        value={pct}
        className="h-1.5 flex-1"
        color={pct >= 80 ? "green" : pct >= 60 ? "yellow" : "red"}
      />
      <span className={cn("text-xs font-medium tabular-nums",
        pct >= 80 ? "text-green-600" : pct >= 60 ? "text-yellow-600" : "text-red-600"
      )}>
        {pct}%
      </span>
    </div>
  );
}

export function BOMItemsTable({ items, isLoading }: BOMItemsTableProps) {
  if (isLoading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (items.length === 0) return null;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-100 bg-slate-50">
            {["Description", "HS Code", "Confidence", "Origin", "Status", "Qty", "Unit Cost"].map(h => (
              <th key={h} className="px-4 py-2.5 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-slate-50 transition-colors">
              <td className="px-4 py-3 text-slate-800 max-w-[200px] truncate" title={item.description}>
                {item.description}
              </td>
              <td className="px-4 py-3 font-mono text-xs text-slate-700">
                {item.hs_code || <span className="text-slate-300">—</span>}
                {item.classified_by === "ai" && (
                  <span className="ml-1 rounded-sm bg-brand-50 px-1 py-0.5 text-[10px] text-brand-600 font-medium">AI</span>
                )}
              </td>
              <td className="px-4 py-3">
                <ConfidencePill confidence={item.hs_confidence} />
              </td>
              <td className="px-4 py-3">
                <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-600">
                  {item.origin_country}
                </span>
              </td>
              <td className="px-4 py-3">
                <OriginBadge is_originating={item.is_originating} />
              </td>
              <td className="px-4 py-3 text-slate-600 tabular-nums">{item.quantity}</td>
              <td className="px-4 py-3 text-slate-700 tabular-nums">
                {formatCurrency(item.unit_cost, item.currency)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
