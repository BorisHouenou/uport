"use client";

import { useState } from "react";
import { Spinner } from "@/components/ui/spinner";
import { useSupplierDeclarations, useUploadDeclarationDoc } from "@/hooks/use-api";
import { AlertTriangle, Bell, FileText, Upload, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import toast from "react-hot-toast";

export interface Declaration {
  id: string;
  supplier_name: string;
  supplier_country: string;
  origin_country: string;
  valid_from: string;
  valid_until: string;
  is_expired: boolean;
  doc_url?: string;
}

function getDaysLeft(d: Declaration): number {
  return Math.ceil((new Date(d.valid_until).getTime() - Date.now()) / 86_400_000);
}

function completeness(d: Declaration): number {
  let score = 0;
  if (d.supplier_name) score += 25;
  if (d.supplier_country) score += 25;
  if (d.origin_country) score += 25;
  if (d.doc_url) score += 25;
  return score;
}

function SupplierCard({
  d,
  onView,
}: {
  d: Declaration;
  onView: (id: string) => void;
}) {
  const uploadDoc = useUploadDeclarationDoc();
  const [uploadingId, setUploadingId] = useState<string | null>(null);
  const daysLeft = getDaysLeft(d);
  const pct = completeness(d);

  const handleUpload = async (file: File) => {
    setUploadingId(d.id);
    try {
      await uploadDoc.mutateAsync({ declarationId: d.id, file });
      toast.success("Document uploaded");
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploadingId(null);
    }
  };

  const statusLabel = d.is_expired
    ? "Expired"
    : daysLeft <= 30
    ? `Expires in ${daysLeft}d`
    : "Active";

  const statusCls = d.is_expired
    ? "bg-red-50 text-red-600"
    : daysLeft <= 30
    ? "bg-amber-50 text-amber-700"
    : "bg-emerald-50 text-emerald-700";

  const barColor = d.is_expired
    ? "bg-red-400"
    : daysLeft <= 30
    ? "bg-amber-400"
    : "bg-emerald-500";

  return (
    <div className="rounded-xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      {/* Top row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-sm font-bold text-slate-600 uppercase">
            {d.supplier_name.slice(0, 2)}
          </div>
          <div>
            <p className="font-semibold text-slate-800">{d.supplier_name}</p>
            <p className="text-xs text-slate-500">
              {d.supplier_country} &rarr; Origin: {d.origin_country}
            </p>
          </div>
        </div>
        <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", statusCls)}>
          {statusLabel}
        </span>
      </div>

      {/* Completeness bar */}
      <div className="mt-4">
        <div className="mb-1 flex items-center justify-between">
          <span className="text-xs text-slate-500">Declaration completeness</span>
          <span className="text-xs font-semibold text-slate-700">{pct}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            className={cn("h-full rounded-full transition-all", barColor)}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Last updated */}
      <p className="mt-3 text-xs text-slate-400">
        Valid until {new Date(d.valid_until).toLocaleDateString()}
      </p>

      {/* Actions */}
      <div className="mt-4 flex items-center gap-2 border-t border-[#E2E8F0] pt-3">
        <button
          onClick={() => toast("Reminder sent")}
          className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-[#2563EB] hover:text-[#2563EB]"
        >
          <Bell className="h-3.5 w-3.5" />
          Send Reminder
        </button>
        {d.doc_url ? (
          <a
            href={d.doc_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-[#2563EB] hover:text-[#2563EB]"
          >
            <FileText className="h-3.5 w-3.5" />
            View Doc
          </a>
        ) : (
          <label className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg border border-[#E2E8F0] px-3 py-1.5 text-xs font-medium text-slate-600 transition-colors hover:border-[#2563EB] hover:text-[#2563EB]">
            <Upload className="h-3.5 w-3.5" />
            {uploadingId === d.id ? <Spinner className="h-3 w-3" /> : "Upload Doc"}
            <input
              type="file"
              className="sr-only"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleUpload(f);
              }}
            />
          </label>
        )}
        <button
          onClick={() => onView(d.id)}
          className="ml-auto inline-flex items-center gap-1 text-xs font-medium text-[#2563EB] hover:underline"
        >
          View Declarations
          <ChevronRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

export function DeclarationsTable({
  onInvite,
}: {
  onInvite: () => void;
}) {
  const { data, isLoading } = useSupplierDeclarations();

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  const declarations: Declaration[] = data?.declarations ?? [];
  const expiringSoon: number = data?.expiring_soon ?? 0;

  return (
    <div className="space-y-4">
      {/* Alert banner */}
      {expiringSoon > 0 && (
        <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>
            <strong>{expiringSoon}</strong> declaration
            {expiringSoon !== 1 ? "s" : ""} expiring within 30 days
          </span>
        </div>
      )}

      {declarations.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-[#E2E8F0] bg-white py-20 text-center shadow-sm">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
            <FileText className="h-8 w-8 text-slate-300" />
          </div>
          <p className="font-semibold text-slate-700">No supplier declarations yet</p>
          <p className="mt-1 max-w-xs text-sm text-slate-400">
            Invite a supplier to submit their origin declaration.
          </p>
          <button
            onClick={onInvite}
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-semibold text-white hover:bg-[#1D4ED8]"
          >
            Invite Supplier
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {declarations.map((d) => (
            <SupplierCard key={d.id} d={d} onView={(id) => toast(`Viewing ${id}`)} />
          ))}
        </div>
      )}
    </div>
  );
}
