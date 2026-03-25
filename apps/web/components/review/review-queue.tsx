"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

interface Determination {
  id: string;
  shipment_id: string;
  agreement_code: string;
  agreement_name: string;
  rule_applied: string;
  result: string;
  confidence: number;
  reasoning: string | null;
  preferential_rate: string | null;
  mfn_rate: string | null;
  status: string;
  created_at: string | null;
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 90 ? "bg-green-100 text-green-700" :
    pct >= 75 ? "bg-yellow-100 text-yellow-700" :
                "bg-red-100 text-red-700";
  return <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>{pct}% confidence</span>;
}

function ReviewCard({ det }: { det: Determination }) {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState("");
  const [correctedResult, setCorrectedResult] = useState(det.result);

  const reviewMutation = useMutation({
    mutationFn: (decision: "approved" | "rejected") =>
      apiClient.post(`/origin/${det.id}/review`, {
        decision,
        reviewer_notes: notes || undefined,
        corrected_result: decision === "rejected" ? correctedResult : undefined,
      }).then(r => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["review-queue"] }),
  });

  return (
    <Card className="border-l-4 border-l-amber-400">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold text-slate-800">{det.agreement_code}</span>
              <ConfidenceBadge value={det.confidence} />
              <Badge variant={det.result === "pass" ? "default" : "destructive"} className="text-xs">
                {det.result}
              </Badge>
            </div>
            <p className="mt-1 text-xs text-slate-500 truncate">
              Shipment {det.shipment_id.slice(0, 8)}… · Rule: {det.rule_applied} · {det.created_at?.slice(0, 10)}
            </p>
          </div>
          <button
            className="shrink-0 text-slate-400 hover:text-slate-600"
            onClick={() => setExpanded(e => !e)}
          >
            {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>

        {expanded && (
          <div className="mt-4 space-y-3 border-t border-slate-100 pt-4">
            {det.reasoning && (
              <div>
                <p className="text-xs font-medium text-slate-500 mb-1">AI Reasoning</p>
                <p className="text-sm text-slate-700 whitespace-pre-wrap rounded-lg bg-slate-50 p-3">{det.reasoning}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3 text-xs text-slate-600">
              <div><span className="font-medium">MFN Rate:</span> {det.mfn_rate ?? "—"}</div>
              <div><span className="font-medium">Preferential Rate:</span> {det.preferential_rate ?? "—"}</div>
            </div>

            <div>
              <label className="text-xs font-medium text-slate-500">Review notes (optional)</label>
              <textarea
                className="mt-1 w-full rounded-lg border border-slate-200 p-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
                rows={2}
                placeholder="Add context for the record…"
                value={notes}
                onChange={e => setNotes(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-500">Override result (if rejecting)</label>
              <select
                className="mt-1 w-full rounded-lg border border-slate-200 p-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
                value={correctedResult}
                onChange={e => setCorrectedResult(e.target.value)}
              >
                <option value="pass">pass</option>
                <option value="fail">fail</option>
                <option value="insufficient_data">insufficient_data</option>
              </select>
            </div>

            <div className="flex gap-2">
              <Button
                size="sm"
                className="gap-1.5 bg-green-600 hover:bg-green-700"
                disabled={reviewMutation.isPending}
                onClick={() => reviewMutation.mutate("approved")}
              >
                <CheckCircle className="h-3.5 w-3.5" />
                Approve AI result
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="gap-1.5 border-red-300 text-red-600 hover:bg-red-50"
                disabled={reviewMutation.isPending}
                onClick={() => reviewMutation.mutate("rejected")}
              >
                <XCircle className="h-3.5 w-3.5" />
                Reject &amp; override
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ReviewQueue() {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useQuery({
    queryKey: ["review-queue", page],
    queryFn: () => apiClient.get(`/origin/review-queue?page=${page}&page_size=20`).then(r => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner className="h-6 w-6 text-brand-600" />
      </div>
    );
  }

  if (isError) {
    return <p className="text-sm text-slate-500">Failed to load review queue.</p>;
  }

  const { items, total } = data;
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">
            {total === 0
              ? "No determinations pending review."
              : `${total} determination${total !== 1 ? "s" : ""} awaiting review`}
          </p>
        </div>
        {total > 0 && (
          <div className="flex items-center gap-1.5 rounded-lg bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700">
            <AlertTriangle className="h-3.5 w-3.5" />
            Below {Math.round(0.75 * 100)}% confidence threshold
          </div>
        )}
      </div>

      {items.length === 0 ? (
        <Card>
          <CardContent className="flex h-40 items-center justify-center">
            <div className="text-center">
              <CheckCircle className="mx-auto h-8 w-8 text-green-400" />
              <p className="mt-2 text-sm font-medium text-slate-600">Queue is clear</p>
              <p className="text-xs text-slate-400">All determinations are above the confidence threshold.</p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="space-y-3">
            {items.map((det: Determination) => (
              <ReviewCard key={det.id} det={det} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-2">
              <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</Button>
              <span className="text-xs text-slate-500">Page {page} of {totalPages}</span>
              <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
