"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useCertificates } from "@/hooks/use-api";
import { Button } from "@/components/ui/button";
import { PageSpinner } from "@/components/ui/spinner";
import { formatDate, cn } from "@/lib/utils";
import {
  Download,
  FileCheck2,
  Plus,
  Search,
  ChevronDown,
  MoreHorizontal,
} from "lucide-react";
import Link from "next/link";

const CERT_TYPE_LABELS: Record<string, string> = {
  cusma: "CUSMA",
  eur1: "EUR.1",
  form_a: "Form A",
  generic: "Generic CO",
  ceta: "CETA",
  cptpp: "CPTPP",
};

const CERT_TYPE_COLORS: Record<string, string> = {
  cusma: "bg-blue-50 text-blue-700 border-blue-200",
  eur1: "bg-violet-50 text-violet-700 border-violet-200",
  form_a: "bg-amber-50 text-amber-700 border-amber-200",
  generic: "bg-slate-100 text-slate-600 border-slate-200",
  ceta: "bg-emerald-50 text-emerald-700 border-emerald-200",
  cptpp: "bg-indigo-50 text-indigo-700 border-indigo-200",
};

const STATUS_STYLES: Record<string, string> = {
  issued: "bg-emerald-50 text-emerald-700",
  draft: "bg-amber-50 text-amber-700",
  expired: "bg-red-50 text-red-600",
  revoked: "bg-red-50 text-red-600",
};

export function CertificatesPanel() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [agreementFilter, setAgreementFilter] = useState("all");
  const { data, isLoading } = useCertificates(page);
  const { getToken } = useAuth();

  const handleDownload = async (certId: string, certNumber?: string) => {
    const token = await getToken();
    const res = await fetch(`/api/v1/certificates/${certId}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
      alert("Download failed — please try again");
      return;
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `certificate_${certNumber ?? certId}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadAll = async () => {
    const certs = data?.certificates ?? [];
    for (const cert of certs) {
      if (cert.status !== "draft") {
        await handleDownload(cert.id, cert.cert_number);
      }
    }
  };

  if (isLoading) return <PageSpinner />;

  const allCerts = data?.certificates ?? [];

  const certificates = allCerts.filter((cert: any) => {
    const matchesSearch =
      !search ||
      cert.cert_number?.toLowerCase().includes(search.toLowerCase()) ||
      cert.shipment_id?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "all" || cert.status === statusFilter;
    const matchesAgreement =
      agreementFilter === "all" || cert.cert_type === agreementFilter;
    return matchesSearch && matchesStatus && matchesAgreement;
  });

  return (
    <div className="space-y-5">
      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative">
          <select
            value={agreementFilter}
            onChange={(e) => setAgreementFilter(e.target.value)}
            className="h-9 appearance-none rounded-lg border border-[#E2E8F0] bg-white pl-3 pr-8 text-sm text-slate-700 focus:border-[#2563EB] focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
          >
            <option value="all">All Agreements</option>
            <option value="cusma">CUSMA</option>
            <option value="ceta">CETA</option>
            <option value="cptpp">CPTPP</option>
            <option value="eur1">EUR.1</option>
            <option value="form_a">Form A</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-2 top-2.5 h-4 w-4 text-slate-400" />
        </div>

        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="h-9 appearance-none rounded-lg border border-[#E2E8F0] bg-white pl-3 pr-8 text-sm text-slate-700 focus:border-[#2563EB] focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
          >
            <option value="all">All Statuses</option>
            <option value="issued">Issued</option>
            <option value="draft">Draft</option>
            <option value="expired">Expired</option>
            <option value="revoked">Revoked</option>
          </select>
          <ChevronDown className="pointer-events-none absolute right-2 top-2.5 h-4 w-4 text-slate-400" />
        </div>

        <div className="relative flex-1 min-w-[200px]">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search cert number or shipment…"
            className="h-9 w-full rounded-lg border border-[#E2E8F0] bg-white pl-9 pr-3 text-sm text-slate-700 placeholder:text-slate-400 focus:border-[#2563EB] focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-slate-500">
            {data?.total ?? 0} certificate{data?.total !== 1 ? "s" : ""}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadAll}
            className="gap-1.5"
          >
            <Download className="h-3.5 w-3.5" />
            Download All
          </Button>
          <Link href="/origin">
            <Button size="sm" className="gap-1.5 bg-[#2563EB] hover:bg-[#1D4ED8]">
              <Plus className="h-3.5 w-3.5" />
              New Certificate
            </Button>
          </Link>
        </div>
      </div>

      {/* Content */}
      {certificates.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-[#E2E8F0] bg-white py-24 text-center shadow-sm">
          <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-2xl bg-blue-50">
            <svg
              width="40"
              height="40"
              viewBox="0 0 40 40"
              fill="none"
            >
              <rect x="8" y="4" width="24" height="32" rx="3" fill="#DBEAFE" />
              <rect x="12" y="10" width="16" height="2" rx="1" fill="#2563EB" />
              <rect x="12" y="15" width="16" height="2" rx="1" fill="#93C5FD" />
              <rect x="12" y="20" width="10" height="2" rx="1" fill="#93C5FD" />
              <circle cx="28" cy="28" r="8" fill="#2563EB" />
              <path
                d="M24.5 28L27 30.5L31.5 26"
                stroke="white"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <p className="text-base font-semibold text-slate-800">No certificates yet</p>
          <p className="mt-1.5 max-w-xs text-sm text-slate-500">
            Run an origin determination to generate your first certificate of origin.
          </p>
          <Link href="/origin" className="mt-6">
            <Button className="bg-[#2563EB] hover:bg-[#1D4ED8]">
              <Plus className="mr-1.5 h-4 w-4" />
              Start Origin Check
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {certificates.map((cert: any) => {
            const typeKey = cert.cert_type ?? "generic";
            const typeLabel = CERT_TYPE_LABELS[typeKey] ?? typeKey.toUpperCase();
            const typeCls =
              CERT_TYPE_COLORS[typeKey] ?? "bg-slate-100 text-slate-600 border-slate-200";
            const statusCls =
              STATUS_STYLES[cert.status] ?? "bg-slate-100 text-slate-600";

            return (
              <div
                key={cert.id}
                className="flex flex-col gap-3 rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50">
                      <FileCheck2 className="h-5 w-5 text-[#2563EB]" />
                    </div>
                    <div>
                      <span
                        className={cn(
                          "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold",
                          typeCls
                        )}
                      >
                        {typeLabel}
                      </span>
                      <p className="mt-1 font-mono text-xs text-slate-500">
                        {cert.cert_number || cert.id.slice(0, 8).toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <button className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>

                <div className="space-y-1 text-xs text-slate-500">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-600">Shipment</span>
                    <span className="font-mono">
                      {cert.shipment_id ? cert.shipment_id.slice(0, 8) + "…" : "—"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-600">Issued</span>
                    <span>{cert.issued_at ? formatDate(cert.issued_at) : "—"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-slate-600">Expires</span>
                    <span>{cert.valid_until ? formatDate(cert.valid_until) : "—"}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between border-t border-[#E2E8F0] pt-3">
                  <span
                    className={cn(
                      "rounded-full px-2 py-0.5 text-xs font-medium capitalize",
                      statusCls
                    )}
                  >
                    {cert.status}
                  </span>
                  <button
                    onClick={() => handleDownload(cert.id, cert.cert_number)}
                    disabled={cert.status === "draft"}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors hover:border-[#2563EB] hover:text-[#2563EB] disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <Download className="h-3.5 w-3.5" />
                    Download PDF
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {(data?.total ?? 0) > 20 && (
        <div className="flex items-center justify-between border-t border-[#E2E8F0] pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>
          <span className="text-xs text-slate-500">Page {page}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
