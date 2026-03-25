"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { ShipmentForm } from "./shipment-form";
import { DeterminationResults } from "./determination-results";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

type WizardStep = "shipment" | "processing" | "results";

interface StepInfo { key: WizardStep; label: string; }
const STEPS: StepInfo[] = [
  { key: "shipment",   label: "Shipment Details" },
  { key: "processing", label: "Analysis" },
  { key: "results",    label: "Results & Certificate" },
];

export function OriginWizard() {
  const [step, setStep] = useState<WizardStep>("shipment");
  const [determinationId, setDeterminationId] = useState<string | null>(null);

  const stepIndex = STEPS.findIndex(s => s.key === step);

  return (
    <div className="space-y-6">
      {/* Step indicator */}
      <div className="flex items-center gap-0">
        {STEPS.map((s, i) => {
          const done    = i < stepIndex;
          const active  = i === stepIndex;
          const pending = i > stepIndex;
          return (
            <div key={s.key} className="flex items-center">
              <div className="flex items-center gap-2">
                <div className={cn(
                  "flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition-colors",
                  done   ? "bg-green-500 text-white" :
                  active ? "bg-brand-600 text-white" :
                           "bg-slate-200 text-slate-400"
                )}>
                  {done ? <CheckCircle2 className="h-4 w-4" /> : i + 1}
                </div>
                <span className={cn("text-sm font-medium",
                  active ? "text-slate-900" : "text-slate-400"
                )}>
                  {s.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={cn("mx-4 h-px w-12 transition-colors",
                  i < stepIndex ? "bg-green-400" : "bg-slate-200"
                )} />
              )}
            </div>
          );
        })}
      </div>

      {/* Step content */}
      {step === "shipment" && (
        <ShipmentForm
          onSubmit={(taskId) => {
            setDeterminationId(taskId);
            setStep("processing");
            // Poll until done — handled inside DeterminationResults
            setTimeout(() => setStep("results"), 500);
          }}
        />
      )}

      {step === "processing" && (
        <Card>
          <CardContent className="flex flex-col items-center gap-4 py-16">
            <Loader2 className="h-10 w-10 animate-spin text-brand-600" />
            <div className="text-center">
              <p className="font-semibold text-slate-800">Analysing Rules of Origin…</p>
              <p className="mt-1 text-sm text-slate-500">
                Evaluating CUSMA, CETA, CPTPP and other applicable agreements
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {step === "results" && determinationId && (
        <DeterminationResults determinationId={determinationId} />
      )}
    </div>
  );
}
