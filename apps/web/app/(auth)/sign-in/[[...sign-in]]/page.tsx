import { SignIn } from "@clerk/nextjs";
import { ShieldCheck, CheckCircle2 } from "lucide-react";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen">
      {/* Left — brand panel */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-[#0F1E3C] px-12 py-10">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] shadow-lg">
            <ShieldCheck className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">Uportai</span>
        </div>

        <div>
          <h2 className="text-4xl font-bold text-white leading-tight tracking-tight">
            AI-powered trade<br />compliance.
          </h2>
          <p className="mt-4 text-[#94a3b8] text-base leading-relaxed max-w-sm">
            Automate Rules of Origin across CUSMA, CETA, CPTPP, and 170+ trade agreements. Reclaim every preferential tariff you've earned.
          </p>
          <ul className="mt-8 space-y-3">
            {[
              "HS code classification in seconds, not hours",
              "Multi-agreement arbitrage — best rate, automatically",
              "Legally valid certificates with full audit trail",
            ].map((item) => (
              <li key={item} className="flex items-start gap-3 text-sm text-[#94a3b8]">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#3B82F6]" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-[#4a6fa5]">© 2025 Uportai · SOC 2 · PIPEDA · GDPR</p>
      </div>

      {/* Right — Clerk form */}
      <div className="flex flex-1 items-center justify-center bg-[#F8FAFF] px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-6 lg:hidden flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563EB] to-[#1D4ED8]">
              <ShieldCheck className="h-4 w-4 text-white" />
            </div>
            <span className="text-base font-bold text-[#0A0F1E]">Uportai</span>
          </div>
          <SignIn
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "rounded-2xl shadow-card border border-[#E2E8F0] bg-white",
                headerTitle: "text-[#0A0F1E] font-bold",
                formButtonPrimary: "bg-[#2563EB] hover:bg-[#1D4ED8] rounded-xl font-semibold",
                footerActionLink: "text-[#2563EB] hover:text-[#1D4ED8]",
              },
            }}
          />
        </div>
      </div>
    </div>
  );
}
