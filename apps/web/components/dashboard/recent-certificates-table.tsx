"use client";

import Link from "next/link";
import { Download, FileText, ArrowRight } from "lucide-react";
import { formatDate, cn } from "@/lib/utils";

const mockCertificates = [
  { id: "1", cert_type: "CUSMA", shipment_ref: "SH-2026-001", product: "Industrial Water Pump", destination: "United States", issued_at: "2026-03-20", status: "issued" },
  { id: "2", cert_type: "CETA",  shipment_ref: "SH-2026-002", product: "Auto Parts Assembly", destination: "Germany", issued_at: "2026-03-18", status: "issued" },
  { id: "3", cert_type: "CUSMA", shipment_ref: "SH-2026-003", product: "Steel Fabrication Kit", destination: "Mexico", issued_at: "2026-03-15", status: "draft" },
];

const CERT_BADGE: Record<string, string> = {
  CUSMA: "bg-blue-50 text-blue-700",
  CETA: "bg-violet-50 text-violet-700",
  CPTPP: "bg-emerald-50 text-emerald-700",
};

const STATUS_BADGE: Record<string, string> = {
  issued: "badge-success",
  draft: "badge-warning",
  expired: "badge-error",
};

export function RecentCertificatesTable() {
  const isEmpty = mockCertificates.length === 0;

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-card overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#F1F5F9] px-6 py-4">
        <h2 className="text-sm font-semibold text-[#0A0F1E]">Recent Certificates</h2>
        <Link href="/certificates" className="flex items-center gap-1 text-xs font-medium text-[#2563EB] hover:text-[#1D4ED8] transition-colors">
          View all <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {isEmpty ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50">
            <FileText className="h-7 w-7 text-[#2563EB]" />
          </div>
          <p className="text-sm font-medium text-slate-700">No certificates yet</p>
          <p className="mt-1 text-xs text-slate-400">Run your first origin check to generate a certificate</p>
          <Link href="/origin" className="btn-primary mt-4 text-xs">
            Start Origin Check
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="bg-[#F8FAFF]">
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Reference</th>
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Product</th>
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Agreement</th>
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Destination</th>
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Issued</th>
                <th className="px-6 py-3 text-left text-[10px] font-semibold uppercase tracking-wider text-slate-400">Status</th>
                <th className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {mockCertificates.map((cert) => (
                <tr key={cert.id} className="hover:bg-[#F8FAFF] transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-slate-600">{cert.shipment_ref}</td>
                  <td className="px-6 py-4 text-sm text-slate-700 font-medium max-w-[160px] truncate">{cert.product}</td>
                  <td className="px-6 py-4">
                    <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-semibold", CERT_BADGE[cert.cert_type] ?? "bg-slate-100 text-slate-600")}>
                      {cert.cert_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500">{cert.destination}</td>
                  <td className="px-6 py-4 text-xs text-slate-400">{formatDate(cert.issued_at)}</td>
                  <td className="px-6 py-4">
                    <span className={cn(STATUS_BADGE[cert.status] ?? "badge-blue", "capitalize")}>
                      {cert.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button type="button" className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-[#2563EB] transition-colors" aria-label="Download">
                      <Download className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
