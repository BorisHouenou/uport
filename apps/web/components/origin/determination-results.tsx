"use client";

import { useAuth } from "@clerk/nextjs";
import { useDetermination, useGenerateCertificate } from "@/hooks/use-api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfidenceMeter } from "@/components/ui/progress";
import { PageSpinner } from "@/components/ui/spinner";
import { formatCurrency, cn } from "@/lib/utils";
import { CheckCircle2, XCircle, AlertCircle, FileCheck2, Download, Trophy } from "lucide-react";
import toast from "react-hot-toast";

interface DeterminationResultsProps {
  determinationId: string;
}

function ResultIcon({ result }: { result: string }) {
  if (result === "pass")             return <CheckCircle2 className="h-5 w-5 text-green-500" />;
  if (result === "fail")             return <XCircle className="h-5 w-5 text-red-400" />;
  return <AlertCircle className="h-5 w-5 text-yellow-500" />;
}

function ResultBadge({ result }: { result: string }) {
  if (result === "pass") return <Badge variant="success">QUALIFIES</Badge>;
  if (result === "fail") return <Badge variant="destructive">DOES NOT QUALIFY</Badge>;
  return <Badge variant="warning">NEEDS REVIEW</Badge>;
}

export function DeterminationResults({ determinationId }: DeterminationResultsProps) {
  const { data, isLoading } = useDetermination(determinationId);
  const generateCert = useGenerateCertificate();
  const { getToken } = useAuth();

  if (isLoading || !data) return <PageSpinner />;

  const determinations = data.results ?? [];
  const bestAgreement  = data.best_agreement;
  const totalSavings   = data.total_savings_usd;

  const handleGenerateCert = async (agreement: string) => {
    try {
      const cert = await generateCert.mutateAsync({
        shipment_id: data.shipment_id,
        determination_id: determinationId,
        cert_type: agreement === "ceta" ? "eur1" : "cusma",
      }) as any;

      toast.success("Certificate generated — downloading PDF…");

      // Download the PDF immediately
      if (cert?.certificate_id) {
        const token = await getToken();
        const res = await fetch(`/api/v1/certificates/${cert.certificate_id}/download`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        if (res.ok) {
          const blob = await res.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `certificate_${cert.certificate_id}.pdf`;
          a.click();
          URL.revokeObjectURL(url);
        }
      }
    } catch {
      toast.error("Certificate generation failed");
    }
  };

  return (
    <div className="space-y-4">
      {/* Summary banner */}
      {bestAgreement && (
        <div className="flex items-center gap-4 rounded-xl border border-green-200 bg-green-50 p-5">
          <Trophy className="h-8 w-8 shrink-0 text-green-500" />
          <div className="flex-1">
            <p className="font-semibold text-green-800">
              Best preferential rate: <span className="uppercase">{bestAgreement}</span>
            </p>
            {totalSavings != null && (
              <p className="text-sm text-green-700 mt-0.5">
                Estimated savings: <strong>{formatCurrency(totalSavings)}</strong> on this shipment
              </p>
            )}
          </div>
          <Button
            onClick={() => handleGenerateCert(bestAgreement)}
            loading={generateCert.isPending}
            className="shrink-0"
          >
            <FileCheck2 className="h-4 w-4" />
            Generate Certificate
          </Button>
        </div>
      )}

      {/* Per-agreement results */}
      <div className="grid gap-3">
        {determinations.map((det: any) => (
          <Card key={det.agreement_code} className={cn(
            det.result === "pass" ? "border-green-200" :
            det.result === "fail" ? "border-red-100"   : "border-yellow-200"
          )}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <ResultIcon result={det.result} />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900 uppercase">{det.agreement_code}</span>
                      <ResultBadge result={det.result} />
                    </div>
                    <p className="mt-0.5 text-xs text-slate-500 capitalize">
                      Rule: {det.rule_applied?.replace(/_/g, " ")}
                    </p>
                  </div>
                </div>
                {det.result === "pass" && bestAgreement !== det.agreement_code && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleGenerateCert(det.agreement_code)}
                    loading={generateCert.isPending}
                  >
                    <Download className="h-3.5 w-3.5" /> Certificate
                  </Button>
                )}
              </div>

              <div className="mt-4 space-y-3">
                <ConfidenceMeter confidence={det.confidence ?? 0} />

                <div className="rounded-lg bg-slate-50 px-3 py-2.5 text-xs text-slate-600 leading-relaxed">
                  {det.reasoning}
                </div>

                {/* RVC detail */}
                {det.rvc_result && (
                  <div className="flex flex-wrap gap-4 text-xs">
                    <span className="text-slate-500">
                      RVC: <strong className={det.rvc_result.passes ? "text-green-600" : "text-red-600"}>
                        {det.rvc_result.rvc_pct}%
                      </strong>{" "}(threshold {det.rvc_result.threshold_pct}%)
                    </span>
                    <span className="text-slate-500">
                      Non-orig value: <strong>{formatCurrency(det.rvc_result.non_originating_value_usd)}</strong>
                    </span>
                    <span className="text-slate-400 font-mono text-[11px]">{det.rvc_result.method?.replace("_", "-").toUpperCase()}</span>
                  </div>
                )}

                {/* TS detail */}
                {det.ts_result && (
                  <p className="text-xs text-slate-500">
                    Tariff shift ({det.ts_result.shift_level}): {" "}
                    <span className={det.ts_result.passes ? "text-green-600 font-medium" : "text-red-600 font-medium"}>
                      {det.ts_result.passes ? "PASS" : "FAIL"}
                    </span>
                    {" "}— {det.ts_result.detail}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        ))}

        {determinations.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center gap-3 py-12 text-center">
              <AlertCircle className="h-8 w-8 text-yellow-500" />
              <p className="font-medium text-slate-700">No determinations available yet</p>
              <p className="text-sm text-slate-400">The analysis may still be processing. This page refreshes automatically.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
