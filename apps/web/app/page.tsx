import { redirect } from "next/navigation";
import { auth } from "@clerk/nextjs/server";
import Link from "next/link";
import {
  ShieldCheck,
  Zap,
  FileText,
  Globe,
  Users,
  TrendingUp,
  MessageSquare,
  ArrowRight,
  CheckCircle2,
  ChevronRight,
} from "lucide-react";

export default async function HomePage() {
  const { userId } = await auth();
  if (userId) redirect("/dashboard");

  return (
    <div className="min-h-screen bg-[#060E1D] text-white overflow-x-hidden">
      {/* Nav */}
      <nav className="fixed top-0 z-50 w-full border-b border-white/5 backdrop-blur-md bg-[#060E1D]/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563EB] to-[#1D4ED8]">
              <ShieldCheck className="h-4 w-4 text-white" />
            </div>
            <span className="text-base font-bold tracking-tight">Uportai</span>
          </div>
          <div className="hidden items-center gap-8 md:flex">
            <a href="#problem" className="text-sm text-white/60 hover:text-white transition-colors">Problem</a>
            <a href="#solution" className="text-sm text-white/60 hover:text-white transition-colors">Solution</a>
            <a href="#features" className="text-sm text-white/60 hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-sm text-white/60 hover:text-white transition-colors">Pricing</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/sign-in" className="text-sm text-white/70 hover:text-white transition-colors">Sign in</Link>
            <Link href="/sign-up" className="rounded-lg bg-[#2563EB] px-4 py-2 text-sm font-semibold text-white hover:bg-[#1D4ED8] transition-colors">
              Get Early Access
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex min-h-screen items-center justify-center pt-16 hero-grid">
        {/* Radial glow */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-1/2 top-1/3 h-[600px] w-[800px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[#2563EB] opacity-[0.07] blur-[120px]" />
          <div className="absolute right-0 top-0 h-[400px] w-[400px] rounded-full bg-[#1E40AF] opacity-[0.05] blur-[100px]" />
        </div>

        <div className="relative mx-auto max-w-5xl px-6 text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#2563EB]/30 bg-[#2563EB]/10 px-4 py-1.5 text-sm text-[#60A5FA]">
            <Zap className="h-3.5 w-3.5" />
            AI-Powered Trade Compliance · Now in Canada
          </div>

          <h1 className="mb-6 font-display text-5xl font-bold leading-[1.1] tracking-tight md:text-6xl lg:text-7xl">
            Stop Leaving{" "}
            <span className="gradient-text">Tariff Savings</span>
            <br />on the Table.
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg text-white/60 leading-relaxed">
            Uportai automates Rules of Origin compliance across 170+ trade agreements.
            Determine origin, generate certificates, and reclaim preferential tariffs —
            with AI-grade certainty and a full audit trail.
          </p>

          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/sign-up"
              className="group inline-flex items-center gap-2 rounded-xl bg-[#2563EB] px-8 py-4 text-base font-semibold text-white shadow-lg shadow-[#2563EB]/25 hover:bg-[#1D4ED8] transition-all duration-150"
            >
              Request Early Access
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <a
              href="#solution"
              className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-8 py-4 text-base font-semibold text-white/70 hover:border-white/20 hover:text-white transition-all duration-150"
            >
              See How It Works
            </a>
          </div>

          {/* Agreement coverage */}
          <div className="mt-14 flex flex-wrap items-center justify-center gap-3">
            {["🇨🇦 CUSMA/USMCA", "🇪🇺 CETA", "🌏 CPTPP", "🌍 AfCFTA", "🌐 EU REX", "📋 Form A"].map((a) => (
              <span key={a} className="rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-xs font-medium text-white/50">
                {a}
              </span>
            ))}
          </div>

          {/* Hero illustration */}
          <div className="mt-16 mx-auto max-w-3xl">
            <div className="relative rounded-2xl border border-white/10 bg-[#0F1E3C]/80 p-6 shadow-2xl backdrop-blur-sm">
              {/* Mock dashboard header */}
              <div className="mb-4 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-red-500/60" />
                <div className="h-3 w-3 rounded-full bg-yellow-500/60" />
                <div className="h-3 w-3 rounded-full bg-green-500/60" />
                <div className="ml-4 flex-1 rounded-md bg-white/5 px-3 py-1 text-xs text-white/30">
                  app.uportai.com/origin
                </div>
              </div>
              {/* Mock determination result */}
              <div className="grid gap-3 sm:grid-cols-3">
                {[
                  { agreement: "CUSMA", status: "QUALIFIES", conf: 97, color: "#10B981" },
                  { agreement: "CETA", status: "QUALIFIES", conf: 89, color: "#10B981" },
                  { agreement: "CPTPP", status: "REVIEW", conf: 62, color: "#F59E0B" },
                ].map((r) => (
                  <div key={r.agreement} className="rounded-xl border border-white/10 bg-white/5 p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-xs font-semibold text-white/50 uppercase tracking-wider">{r.agreement}</span>
                      <span className="rounded-full px-2 py-0.5 text-[10px] font-bold" style={{ backgroundColor: `${r.color}20`, color: r.color }}>
                        {r.status}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-white">{r.conf}%</div>
                    <div className="mt-2 h-1.5 rounded-full bg-white/10">
                      <div className="h-full rounded-full transition-all" style={{ width: `${r.conf}%`, backgroundColor: r.color }} />
                    </div>
                    <p className="mt-2 text-[10px] text-white/30">AI Confidence Score</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section id="problem" className="py-24 bg-[#0A1528]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 font-display text-4xl font-bold tracking-tight">The compliance gap costs exporters millions.</h2>
            <p className="text-white/50 max-w-xl mx-auto">Manual, inconsistent, and expensive — the status quo is costing your business real money.</p>
          </div>
          <div className="grid gap-6 sm:grid-cols-3">
            {[
              { stat: "$134K", label: "Average annual loss per SME from unclaimed preferential tariffs", icon: TrendingUp },
              { stat: "170+", label: "Active Free Trade Agreements worldwide — each with unique, overlapping rules", icon: Globe },
              { stat: "40 hrs", label: "Average time to manually classify, verify, and certify a single complex shipment", icon: FileText },
            ].map((item) => (
              <div key={item.stat} className="glass-dark rounded-2xl p-8">
                <item.icon className="mb-4 h-6 w-6 text-[#3B82F6]" />
                <div className="mb-2 font-display text-5xl font-bold text-[#60A5FA]">{item.stat}</div>
                <p className="text-sm text-white/50 leading-relaxed">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution / Workflow */}
      <section id="solution" className="py-24 bg-[#060E1D]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 text-center">
            <span className="mb-3 inline-block rounded-full border border-[#2563EB]/30 bg-[#2563EB]/10 px-3 py-1 text-xs font-medium text-[#60A5FA]">
              How It Works
            </span>
            <h2 className="mb-4 font-display text-4xl font-bold tracking-tight">Five steps. Fully automated.</h2>
            <p className="text-white/50 max-w-xl mx-auto">A multi-agent AI pipeline that handles the entire compliance workflow — from raw product data to a legally valid certificate.</p>
          </div>

          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-1/2 top-8 hidden h-[calc(100%-4rem)] w-px -translate-x-1/2 bg-gradient-to-b from-[#2563EB]/50 via-[#2563EB]/20 to-transparent md:block" />

            <div className="space-y-8">
              {[
                { step: "01", title: "Upload BOM or Product Description", desc: "CSV, Excel, ERP export — or just describe your product in plain language. Uportai ingests it.", icon: FileText, side: "left" },
                { step: "02", title: "AI HS Classification", desc: "Our classifier assigns the correct HS code with a confidence score. Edge cases go to human review.", icon: Zap, side: "right" },
                { step: "03", title: "Multi-Agreement Origin Determination", desc: "The origin engine evaluates RVC, tariff shift, and wholly-obtained rules across every applicable FTA simultaneously.", icon: ShieldCheck, side: "left" },
                { step: "04", title: "Certificate Generation", desc: "One click produces a legally valid CUSMA Statement, EUR.1, Form A, or custom CO — digitally signed, audit-ready.", icon: FileText, side: "right" },
                { step: "05", title: "Audit Vault & Continuous Monitoring", desc: "Immutable audit trail. Supplier declaration expiry tracking. Alerts when rules change.", icon: CheckCircle2, side: "left" },
              ].map((item) => (
                <div key={item.step} className={`relative flex items-start gap-8 ${item.side === "right" ? "md:flex-row-reverse" : ""}`}>
                  <div className={`flex-1 ${item.side === "right" ? "md:text-right" : ""}`}>
                    <div className="glass-dark rounded-2xl p-6 md:max-w-md">
                      <div className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#2563EB]">Step {item.step}</div>
                      <h3 className="mb-2 text-lg font-semibold text-white">{item.title}</h3>
                      <p className="text-sm text-white/50 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                  <div className="relative z-10 hidden shrink-0 md:flex">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[#2563EB]/30 bg-[#2563EB]/10">
                      <item.icon className="h-6 w-6 text-[#3B82F6]" />
                    </div>
                  </div>
                  <div className="flex-1 hidden md:block" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 bg-[#0A1528]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 font-display text-4xl font-bold tracking-tight">Everything compliance requires. Nothing it doesn&apos;t.</h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[
              { icon: Zap, title: "AI HS Classifier", desc: "Assigns HS codes from product descriptions or BOM lines. Confidence scoring with human-in-loop escalation for edge cases." },
              { icon: Globe, title: "Multi-Agreement Arbitrage", desc: "Evaluates RVC, tariff shift, and wholly-obtained rules across CUSMA, CETA, CPTPP, AfCFTA simultaneously. Finds the best available preferential rate." },
              { icon: FileText, title: "Certificate Generator", desc: "Produces CUSMA Statements on Origin, EUR.1, Form A, and generic COs. PDF output with digital signature support." },
              { icon: MessageSquare, title: "RAG Compliance Assistant", desc: "LLM grounded in full trade agreement texts. Cites the exact article and annex. Never hallucinates — retrieval-first." },
              { icon: Users, title: "Supplier Declaration Portal", desc: "Self-serve portal for suppliers to submit origin declarations. Automated reminders, expiry tracking, one-click renewal." },
              { icon: TrendingUp, title: "Tariff Savings Calculator", desc: "Real-time ROI dashboard. Compares MFN vs preferential rates per shipment. Aggregates annual savings across all agreements." },
            ].map((f) => (
              <div key={f.title} className="glass-dark rounded-2xl p-6 card-hover">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-[#2563EB]/10 border border-[#2563EB]/20">
                  <f.icon className="h-5 w-5 text-[#3B82F6]" />
                </div>
                <h3 className="mb-2 text-base font-semibold text-white">{f.title}</h3>
                <p className="text-sm text-white/50 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trade Agreements */}
      <section className="py-20 bg-[#060E1D] border-y border-white/5">
        <div className="mx-auto max-w-7xl px-6 text-center">
          <h2 className="mb-3 font-display text-3xl font-bold">One platform. Every major trade bloc.</h2>
          <p className="mb-10 text-white/50">Starting with Canada&apos;s key agreements. Built to expand to any FTA in the world.</p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            {[
              { flag: "🇨🇦🇺🇸🇲🇽", name: "CUSMA / USMCA", desc: "Canada · US · Mexico" },
              { flag: "🇨🇦🇪🇺", name: "CETA", desc: "Canada · European Union" },
              { flag: "🌏", name: "CPTPP", desc: "11-nation Asia-Pacific" },
              { flag: "🌍", name: "AfCFTA", desc: "55 African nations" },
              { flag: "🌐", name: "EU REX", desc: "Registered Exporter" },
              { flag: "📋", name: "GSP / Form A", desc: "Generalized Preferences" },
            ].map((t) => (
              <div key={t.name} className="glass-dark rounded-2xl px-6 py-4 text-center min-w-[140px]">
                <div className="text-2xl mb-1">{t.flag}</div>
                <div className="text-sm font-semibold text-white">{t.name}</div>
                <div className="text-xs text-white/40">{t.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 bg-[#0A1528]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 font-display text-4xl font-bold tracking-tight">Simple, transparent pricing.</h2>
            <p className="text-white/50">Start free. Scale as your export volume grows.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              {
                tier: "Starter",
                price: "$299",
                period: "/mo",
                desc: "For SMEs just getting started with preferential trade.",
                features: ["5 origin determinations/mo", "CUSMA + CETA coverage", "Certificate generation", "Basic audit trail", "Email support"],
                cta: "Get Started",
                highlight: false,
              },
              {
                tier: "Growth",
                price: "$999",
                period: "/mo",
                desc: "For exporters with regular multi-agreement shipments.",
                features: ["50 determinations/mo", "All agreements (CUSMA, CETA, CPTPP)", "Supplier portal", "AI compliance assistant", "QuickBooks + ERP integrations", "Priority support"],
                cta: "Start Free Trial",
                highlight: true,
              },
              {
                tier: "Enterprise",
                price: "Custom",
                period: "",
                desc: "For brokers, manufacturers, and freight forwarders at scale.",
                features: ["Unlimited determinations", "All agreements + AfCFTA (Phase 2)", "API access + webhooks", "White-label portal", "SOC 2 reports", "Dedicated CSM"],
                cta: "Contact Sales",
                highlight: false,
              },
            ].map((p) => (
              <div
                key={p.tier}
                className={`relative rounded-2xl p-8 ${
                  p.highlight
                    ? "border border-[#2563EB]/50 bg-gradient-to-b from-[#2563EB]/10 to-[#1E3A8A]/5"
                    : "glass-dark"
                }`}
              >
                {p.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <span className="rounded-full bg-[#2563EB] px-3 py-0.5 text-xs font-bold text-white">Most Popular</span>
                  </div>
                )}
                <div className="mb-2 text-sm font-semibold text-white/50 uppercase tracking-wider">{p.tier}</div>
                <div className="mb-1 font-display text-4xl font-bold text-white">
                  {p.price}<span className="text-lg text-white/40">{p.period}</span>
                </div>
                <p className="mb-6 text-sm text-white/40">{p.desc}</p>
                <ul className="mb-8 space-y-3">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-2.5 text-sm text-white/70">
                      <CheckCircle2 className="h-4 w-4 shrink-0 text-[#10B981]" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/sign-up"
                  className={`block w-full rounded-xl py-3 text-center text-sm font-semibold transition-all duration-150 ${
                    p.highlight
                      ? "bg-[#2563EB] text-white hover:bg-[#1D4ED8] shadow-lg shadow-[#2563EB]/20"
                      : "border border-white/10 text-white/70 hover:border-white/20 hover:text-white"
                  }`}
                >
                  {p.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 bg-gradient-to-b from-[#060E1D] to-[#0F1E3C]">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] shadow-lg shadow-[#2563EB]/30">
            <ShieldCheck className="h-7 w-7 text-white" />
          </div>
          <h2 className="mb-4 font-display text-4xl font-bold tracking-tight">Join 50 founding exporters.</h2>
          <p className="mb-10 text-white/50 text-lg">
            Be among the first Canadian SMEs to automate Rules of Origin.
            Design partners get 6 months free, hands-on onboarding, and influence over the roadmap.
          </p>
          <div className="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <Link
              href="/sign-up"
              className="group inline-flex items-center gap-2 rounded-xl bg-[#2563EB] px-8 py-4 text-base font-semibold text-white shadow-lg shadow-[#2563EB]/25 hover:bg-[#1D4ED8] transition-all"
            >
              Apply as a Design Partner
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
          <p className="mt-4 text-xs text-white/30">No credit card required. Available to Canadian exporters in Phase 1.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-[#060E1D] py-10">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-2.5">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#2563EB]/20">
                <ShieldCheck className="h-4 w-4 text-[#3B82F6]" />
              </div>
              <span className="text-sm font-bold text-white/80">Uportai</span>
              <span className="text-white/20">·</span>
              <span className="text-xs text-white/30">AI Trade Compliance Engine</span>
            </div>
            <div className="flex items-center gap-6 text-xs text-white/30">
              <a href="#" className="hover:text-white/60 transition-colors">Privacy</a>
              <a href="#" className="hover:text-white/60 transition-colors">Terms</a>
              <a href="mailto:hello@uportai.com" className="hover:text-white/60 transition-colors">Contact</a>
            </div>
            <p className="text-xs text-white/20">© 2025 Uportai. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
