"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { CheckCircle, XCircle, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import { cn } from "@/lib/utils";

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

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const barColor =
    pct >= 85
      ? "bg-emerald-500"
      : pct >= 60
      ? "bg-amber-400"
      : "bg-red-500";
  const labelColor =
    pct >= 85
      ? "text-emerald-700"
      : pct >= 60
      ? "text-amber-700"
      : "text-red-600";
  const bgColor =
    pct >= 85
      ? "bg-emerald-50"
      : pct >= 60
      ? "bg-amber-50"
      : "bg-red-50";

  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 overflow-hidden rounded-full bg-slate-100 h-1.5">
        <div
          className={cn("h-full rounded-full transition-all", barColor)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span
        className={cn(
          "shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold",
          bgColor,
          labelColor
        )}
      >
        {pct}% confidence
      </span>
    </div>
  );
}

function ReviewCard({ det }: { det: Determination }) {
  const qc = useQueryClient();
  const [expanded, setExpanded] = useState(false);
  const [notes, setNotes] = useState("");
  const [correctedResult, setCorrectedResult] = useState(det.result);
  const pct = Math.round(det.confidence * 100);
  const isFlagged = pct < 85;

  const reviewMutation = useMutation({
    mutationFn: (decision: "approved" | "rejected") =>
      apiClient
        .post(`/origin/${det.id}/review`, {
          decision,
          reviewer_notes: notes || undefined,
          corrected_result: decision === "rejected" ? correctedResult : undefined,
        })
        .then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["review-queue"] }),
  });

  return (
    <div
      className={cn(
        "rounded-xl border bg-white shadow-sm transition-shadow hover:shadow-md",
        isFlagged ? "border-l-4 border-red-300 border-t-[#E2E8F0] border-r-[#E2E8F0] border-b-[#E2E8F0]" : "border-[#E2E8F0]"
      )}
    >
      <div className="p-5">
        {/* Top row */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0 space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-bold text-slate-700 uppercase tracking-wide">
                {det.agreement_code}
              </span>
              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-xs font-medium",
                  det.result === "pass"
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-red-50 text-red-600"
                )}
              >
                {det.result}
              </span>
              {isFlagged && (
                <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-[10px] font-semibold text-red-600">
                  <AlertTriangle className="h-3 w-3" />
                  Below threshold
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">
              Shipment{" "}
              <span className="font-mono">{det.shipment_id.slice(0, 8)}…</span>
              {" · "}Rule: {det.rule_applied}
              {det.created_at && ` · ${det.created_at.slice(0, 10)}`}
            </p>
            {/* Confidence bar */}
            <ConfidenceBar value={det.confidence} />
          </div>

          {/* Primary actions visible by default */}
          <div className="flex shrink-0 items-center gap-2">
            <button
              onClick={() => reviewMutation.mutate("approved")}
              disabled={reviewMutation.isPending}
              className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-emerald-700 disabled:opacity-50"
            >
              <CheckCircle className="h-3.5 w-3.5" />
              Approve
            </button>
            <button
              onClick={() => setExpanded((e) => !e)}
              className="rounded-lg border border-[#E2E8F0] p-2 text-slate-400 hover:bg-slate-50 hover:text-slate-600"
            >
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>

        {/* Expanded detail */}
        {expanded && (
          <div className="mt-4 space-y-4 border-t border-[#E2E8F0] pt-4">
            {det.reasoning && (
              <div>
                <p className="mb-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wide">
                  AI Reasoning
                </p>
                <p className="whitespace-pre-wrap rounded-xl bg-[#F8FAFF] p-4 text-sm leading-relaxed text-slate-700">
                  {det.reasoning}
                </p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3 rounded-xl bg-slate-50 px-4 py-3 text-xs text-slate-600">
              <div>
                <span className="font-medium text-slate-500">MFN Rate</span>
                <p className="mt-0.5 font-semibold text-slate-800">
                  {det.mfn_rate ?? "—"}
                </p>
              </div>
              <div>
                <span className="font-medium text-slate-500">Preferential Rate</span>
                <p className="mt-0.5 font-semibold text-slate-800">
                  {det.preferential_rate ?? "—"}
                </p>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500">
                Review notes (optional)
              </label>
              <textarea
                className="mt-1.5 w-full rounded-lg border border-[#E2E8F0] p-3 text-sm text-slate-700 focus:border-[#2563EB] focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                rows={2}
                placeholder="Add context for the record…"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-500">
                Override result (if rejecting)
              </label>
              <select
                className="mt-1.5 w-full rounded-lg border border-[#E2E8F0] p-2 text-sm text-slate-700 focus:border-[#2563EB] focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                value={correctedResult}
                onChange={(e) => setCorrectedResult(e.target.value)}
              >
                <option value="pass">pass</option>
                <option value="fail">fail</option>
                <option value="insufficient_data">insufficient_data</option>
              </select>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => reviewMutation.mutate("approved")}
                disabled={reviewMutation.isPending}
                className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                <CheckCircle className="h-4 w-4" />
                Approve AI result
              </button>
              <button
                onClick={() => reviewMutation.mutate("rejected")}
                disabled={reviewMutation.isPending}
                className="inline-flex items-center gap-1.5 rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                <XCircle className="h-4 w-4" />
                Override
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

type Tab = "needs_review" | "all";

export function ReviewQueue() {
  const [page, setPage] = useState(1);
  const [tab, setTab] = useState<Tab>("needs_review");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["review-queue", page],
    queryFn: () =>
      apiClient
        .get(`/origin/review-queue?page=${page}&page_size=20`)
        .then((r) => r.data),
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner className="h-6 w-6 text-[#2563EB]" />
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-slate-500">Failed to load review queue.</p>
    );
  }

  const { items, total } = data;
  const totalPages = Math.ceil(total / 20);

  const needsReview = items.filter(
    (d: Determination) => Math.round(d.confidence * 100) < 85
  );
  const displayItems = tab === "needs_review" ? needsReview : items;

  return (
    <div className="space-y-4">
      {/* Tabs + count */}
      <div className="flex items-center justify-between">
        <div className="flex rounded-xl border border-[#E2E8F0] bg-white p-1">
          {(
            [
              { key: "needs_review", label: "Needs Review", count: needsReview.length },
              { key: "all", label: "All Determinations", count: items.length },
            ] as { key: Tab; label: string; count: number }[]
          ).map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={cn(
                "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                tab === t.key
                  ? "bg-[#2563EB] text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              )}
            >
              {t.label}
              <span
                className={cn(
                  "rounded-full px-1.5 py-0.5 text-[10px] font-semibold",
                  tab === t.key
                    ? "bg-white/20 text-white"
                    : "bg-slate-100 text-slate-600"
                )}
              >
                {t.count}
              </span>
            </button>
          ))}
        </div>

        {needsReview.length > 0 && (
          <div className="flex items-center gap-1.5 rounded-xl bg-red-50 px-3 py-2 text-xs font-medium text-red-600">
            <AlertTriangle className="h-3.5 w-3.5" />
            {needsReview.length} below 85% threshold
          </div>
        )}
      </div>

      {/* Items */}
      {displayItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-[#E2E8F0] bg-white py-20 text-center shadow-sm">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50">
            <CheckCircle className="h-8 w-8 text-emerald-500" />
          </div>
          <p className="font-semibold text-slate-700">Queue is clear</p>
          <p className="mt-1 text-sm text-slate-400">
            All determinations are above the 85% confidence threshold.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayItems.map((det: Determination) => (
            <ReviewCard key={det.id} det={det} />
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className="text-xs text-slate-500">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
