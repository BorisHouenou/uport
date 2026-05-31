"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { ShipmentForm } from "./shipment-form";
import { DeterminationResults } from "./determination-results";
import { CheckCircle2, Loader2, ShieldCheck, FileText, Zap } from "lucide-react";

type WizardStep = "shipment" | "processing" | "results";

interface StepInfo { key: WizardStep; label: string; desc: string; icon: React.ElementType; }
const STEPS: StepInfo[] = [
  { key: "shipment",   label: "Shipment Details", desc: "Product & destination", icon: FileText },
  { key: "processing", label: "AI Analysis",       desc: "Running determination", icon: Zap },
  { key: "results",    label: "Results",           desc: "Origin & certificate",  icon: ShieldCheck },
];

export function OriginWizard() {
  const [step, setStep] = useState<WizardStep>("shipment");
  const [determinationId, setDeterminationId] = useState<string | null>(null);

  const stepIndex = STEPS.findIndex(s => s.key === step);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Step indicator */}
      <div className="rounded-2xl border border-[#E2E8F0] bg-white p-4 shadow-card">
        <div className="flex items-center">
          {STEPS.map((s, i) => {
            const done    = i < stepIndex;
            const active  = i === stepIndex;
            return (
              <div key={s.key} className="flex flex-1 items-center">
                <div className="flex items-center gap-3">
                  <div className={cn(
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-semibold transition-all duration-200",
                    done   ? "bg-emerald-500 text-white shadow-sm" :
                    active ? "bg-[#2563EB] text-white shadow-sm shadow-blue-200" :
                             "bg-slate-100 text-slate-400"
                  )}>
                    {done ? <CheckCircle2 className="h-4 w-4" /> : <s.icon className="h-4 w-4" />}
                  </div>
                  <div className="hidden sm:block">
                    <p className={cn("text-sm font-semibold", active ? "text-[#0A0F1E]" : done ? "text-slate-600" : "text-slate-400")}>
                      {s.label}
                    </p>
                    <p className={cn("text-xs", active ? "text-slate-500" : "text-slate-300")}>
                      {s.desc}
                    </p>
                  </div>
                </div>
                {i < STEPS.length - 1 && (
                  <div className="mx-4 flex-1">
                    <div className={cn("h-0.5 rounded-full transition-all duration-300", i < stepIndex ? "bg-emerald-400" : "bg-slate-100")} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step content */}
      {step === "shipment" && (
        <ShipmentForm
          onSubmit={(taskId) => {
            setDeterminationId(taskId);
            setStep("processing");
            setTimeout(() => setStep("results"), 500);
          }}
        />
      )}

      {step === "processing" && (
        <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-card">
          <div className="flex flex-col items-center gap-5 py-20 text-center">
            <div className="relative">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50">
                <Zap className="h-8 w-8 text-[#2563EB]" />
              </div>
              <div className="absolute -right-1 -top-1">
                <Loader2 className="h-5 w-5 animate-spin text-[#2563EB]" />
              </div>
            </div>
            <div>
              <p className="text-base font-semibold text-[#0A0F1E]">Analysing Rules of Origin…</p>
              <p className="mt-1 text-sm text-slate-500">
                Evaluating CUSMA · CETA · CPTPP and all applicable agreements
              </p>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-[#E2E8F0] bg-[#F8FAFF] px-4 py-2">
              <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#2563EB] [animation-delay:0ms]" />
              <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#2563EB] [animation-delay:150ms]" />
              <div className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#2563EB] [animation-delay:300ms]" />
              <span className="ml-1 text-xs text-slate-400">Running multi-agent pipeline</span>
            </div>
          </div>
        </div>
      )}

      {step === "results" && determinationId && (
        <DeterminationResults determinationId={determinationId} />
      )}
    </div>
  );
}
