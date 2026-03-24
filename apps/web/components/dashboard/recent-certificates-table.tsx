"use client";

import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

// TODO Sprint 5–6: fetch from /api/v1/certificates
const mockCertificates = [
  { id: "1", cert_type: "CUSMA", shipment_ref: "SH-2026-001", destination: "US", issued_at: "2026-03-20", status: "issued" },
  { id: "2", cert_type: "CETA",  shipment_ref: "SH-2026-002", destination: "DE", issued_at: "2026-03-18", status: "issued" },
  { id: "3", cert_type: "CUSMA", shipment_ref: "SH-2026-003", destination: "MX", issued_at: "2026-03-15", status: "draft" },
];

const STATUS_STYLES: Record<string, string> = {
  issued: "bg-green-100 text-green-700",
  draft:  "bg-yellow-100 text-yellow-700",
  expired: "bg-red-100 text-red-700",
};

export function RecentCertificatesTable() {
  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
          Recent Certificates
        </h2>
        <a href="/certificates" className="text-xs text-brand-600 hover:underline">
          View all
        </a>
      </div>
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50">
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Reference</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Destination</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Issued</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {mockCertificates.map((cert) => (
              <tr key={cert.id} className="hover:bg-slate-50 transition-colors">
                <td className="px-4 py-3 font-mono text-xs text-slate-700">{cert.shipment_ref}</td>
                <td className="px-4 py-3">
                  <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
                    {cert.cert_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-600">{cert.destination}</td>
                <td className="px-4 py-3 text-slate-500">{formatDate(cert.issued_at)}</td>
                <td className="px-4 py-3">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium capitalize", STATUS_STYLES[cert.status] ?? "bg-slate-100 text-slate-600")}>
                    {cert.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
