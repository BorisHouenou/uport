"use client";

import { useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { useCertificates } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageSpinner } from "@/components/ui/spinner";
import { formatDate, formatCurrency, cn } from "@/lib/utils";
import { Download, FileCheck2, RefreshCw, Plus } from "lucide-react";
import Link from "next/link";

const CERT_TYPE_LABELS: Record<string, string> = {
  cusma: "CUSMA",
  eur1:  "EUR.1",
  form_a: "Form A",
  generic: "Generic CO",
};

const STATUS_VARIANT: Record<string, "success" | "warning" | "destructive" | "outline"> = {
  issued:  "success",
  draft:   "warning",
  expired: "destructive",
  revoked: "destructive",
};

export function CertificatesPanel() {
  const [page, setPage] = useState(1);
  const { data, isLoading, refetch } = useCertificates(page);
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

  if (isLoading) return <PageSpinner />;

  const certificates = data?.certificates ?? [];

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          {data?.total ?? 0} certificate{data?.total !== 1 ? "s" : ""} total
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </Button>
          <Link href="/origin">
            <Button size="sm">
              <Plus className="h-3.5 w-3.5" /> New Certificate
            </Button>
          </Link>
        </div>
      </div>

      {certificates.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-16 text-center">
            <FileCheck2 className="h-12 w-12 text-slate-300" />
            <div>
              <p className="font-semibold text-slate-700">No certificates yet</p>
              <p className="mt-1 text-sm text-slate-400">
                Run an origin determination to generate your first certificate.
              </p>
            </div>
            <Link href="/origin">
              <Button>Start Origin Check</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50">
                  {["Cert Number", "Type", "Shipment", "Destination", "Issued", "Expires", "Status", ""].map(h => (
                    <th key={h} className="px-4 py-2.5 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {certificates.map((cert: any) => (
                  <tr key={cert.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-slate-700">
                      {cert.cert_number || cert.id.slice(0, 8).toUpperCase()}
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
                        {CERT_TYPE_LABELS[cert.cert_type] ?? cert.cert_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">
                      {cert.shipment_id?.slice(0, 8)}…
                    </td>
                    <td className="px-4 py-3 text-slate-600">—</td>
                    <td className="px-4 py-3 text-slate-500">
                      {cert.issued_at ? formatDate(cert.issued_at) : "—"}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {cert.valid_until ? formatDate(cert.valid_until) : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={STATUS_VARIANT[cert.status] ?? "outline"}>
                        {cert.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDownload(cert.id, cert.cert_number)}
                        disabled={cert.status === "draft"}
                      >
                        <Download className="h-3.5 w-3.5" /> PDF
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {(data?.total ?? 0) > 20 && (
            <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3">
              <Button variant="outline" size="sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                Previous
              </Button>
              <span className="text-xs text-slate-500">Page {page}</span>
              <Button variant="outline" size="sm" onClick={() => setPage(p => p + 1)}>
                Next
              </Button>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
