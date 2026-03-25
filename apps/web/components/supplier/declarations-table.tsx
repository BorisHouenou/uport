"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useSupplierDeclarations, useUploadDeclarationDoc } from "@/hooks/use-api";
import { AlertTriangle, CheckCircle2, Upload, FileText } from "lucide-react";
import toast from "react-hot-toast";

interface Declaration {
  id: string;
  supplier_name: string;
  supplier_country: string;
  origin_country: string;
  valid_from: string;
  valid_until: string;
  is_expired: boolean;
  doc_url?: string;
}

function expiryBadge(d: Declaration) {
  if (d.is_expired) return <Badge variant="destructive">Expired</Badge>;
  const daysLeft = Math.ceil(
    (new Date(d.valid_until).getTime() - Date.now()) / 86_400_000
  );
  if (daysLeft <= 30)
    return (
      <Badge className="bg-yellow-100 text-yellow-800">
        Expires in {daysLeft}d
      </Badge>
    );
  return <Badge variant="secondary">Active</Badge>;
}

export function DeclarationsTable() {
  const { data, isLoading } = useSupplierDeclarations();
  const uploadDoc = useUploadDeclarationDoc();
  const [uploadingId, setUploadingId] = useState<string | null>(null);

  const handleUpload = async (declarationId: string, file: File) => {
    setUploadingId(declarationId);
    try {
      await uploadDoc.mutateAsync({ declarationId, file });
      toast.success("Document uploaded");
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploadingId(null);
    }
  };

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
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Supplier Declarations</CardTitle>
          <CardDescription>
            {declarations.length} declaration{declarations.length !== 1 ? "s" : ""}
            {expiringSoon > 0 && (
              <span className="ml-2 inline-flex items-center gap-1 text-yellow-600">
                <AlertTriangle className="h-3.5 w-3.5" />
                {expiringSoon} expiring within 30 days
              </span>
            )}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        {declarations.length === 0 ? (
          <p className="py-8 text-center text-sm text-slate-400">
            No declarations yet. Use the form to add one.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-100 text-left text-xs text-slate-500">
                  <th className="pb-2 pr-4 font-medium">Supplier</th>
                  <th className="pb-2 pr-4 font-medium">Origin</th>
                  <th className="pb-2 pr-4 font-medium">Valid Until</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium">Document</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {declarations.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-50">
                    <td className="py-3 pr-4 font-medium text-slate-800">
                      {d.supplier_name}
                      <span className="ml-1 text-xs text-slate-400">({d.supplier_country})</span>
                    </td>
                    <td className="py-3 pr-4 text-slate-600">{d.origin_country}</td>
                    <td className="py-3 pr-4 text-slate-600">
                      {new Date(d.valid_until).toLocaleDateString()}
                    </td>
                    <td className="py-3 pr-4">{expiryBadge(d)}</td>
                    <td className="py-3">
                      {d.doc_url ? (
                        <a
                          href={d.doc_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-brand-600 hover:underline"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          View
                        </a>
                      ) : (
                        <label className="inline-flex cursor-pointer items-center gap-1 text-xs text-slate-400 hover:text-brand-600">
                          <Upload className="h-3.5 w-3.5" />
                          {uploadingId === d.id ? <Spinner size="sm" /> : "Upload"}
                          <input
                            type="file"
                            className="sr-only"
                            onChange={(e) => {
                              const f = e.target.files?.[0];
                              if (f) handleUpload(d.id, f);
                            }}
                          />
                        </label>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
