"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { formatCurrency } from "@/lib/utils";
import { useSavingsSummary } from "@/hooks/use-api";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Legend, Cell,
} from "recharts";
import { TrendingUp, DollarSign, FileCheck2, ShieldCheck } from "lucide-react";

const AGREEMENT_COLORS = ["#0062c9", "#22c55e", "#f59e0b", "#8b5cf6", "#ef4444"];

export function SavingsDashboard() {
  const { data, isLoading, isError } = useSavingsSummary();

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner className="h-6 w-6 text-brand-600" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-500">
        Unable to load savings data. Please try again later.
      </div>
    );
  }

  const { kpis, monthly, by_agreement, annual_projection } = data;

  const KPI_CARDS = [
    { label: "Total Savings YTD",      value: formatCurrency(kpis.total_savings_ytd),       icon: DollarSign,  color: "text-green-600",   bg: "bg-green-50" },
    { label: "Certificates Issued",    value: String(kpis.certificates_issued),              icon: FileCheck2,  color: "text-brand-600",   bg: "bg-brand-50" },
    { label: "Avg Saving / Shipment",  value: formatCurrency(kpis.avg_saving_per_shipment),  icon: TrendingUp,  color: "text-violet-600",  bg: "bg-violet-50" },
    { label: "Compliance Rate",        value: `${kpis.compliance_rate}%`,                   icon: ShieldCheck, color: "text-emerald-600", bg: "bg-emerald-50" },
  ];

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {KPI_CARDS.map((kpi) => (
          <Card key={kpi.label}>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium text-slate-500">{kpi.label}</p>
                <div className={`rounded-lg p-2 ${kpi.bg}`}>
                  <kpi.icon className={`h-4 w-4 ${kpi.color}`} />
                </div>
              </div>
              <p className="mt-3 text-2xl font-bold text-slate-900">{kpi.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        {/* Monthly savings trend */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Monthly Savings</CardTitle>
            <CardDescription>Cumulative tariff savings captured per month</CardDescription>
          </CardHeader>
          <CardContent>
            {monthly.length === 0 ? (
              <p className="py-16 text-center text-sm text-slate-400">No savings data yet for this period.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={monthly} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="savingsGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#0062c9" stopOpacity={0.15} />
                      <stop offset="95%" stopColor="#0062c9" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false}
                    tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: 12 }}
                    formatter={(v: any) => [formatCurrency(v), "Savings"]}
                  />
                  <Area type="monotone" dataKey="savings" stroke="#0062c9" strokeWidth={2}
                    fill="url(#savingsGrad)" dot={{ fill: "#0062c9", r: 3 }} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* By agreement */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Savings by Agreement</CardTitle>
            <CardDescription>Which FTAs deliver the most value</CardDescription>
          </CardHeader>
          <CardContent>
            {by_agreement.length === 0 ? (
              <p className="py-16 text-center text-sm text-slate-400">No agreement data yet.</p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={by_agreement} layout="vertical" margin={{ left: 8, right: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false}
                      tickFormatter={v => `$${(v / 1000).toFixed(0)}k`} />
                    <YAxis type="category" dataKey="agreement" tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} width={52} />
                    <Tooltip
                      contentStyle={{ borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: 12 }}
                      formatter={(v: any) => [formatCurrency(v), "Savings"]}
                    />
                    <Bar dataKey="savings" radius={[0, 4, 4, 0]}>
                      {by_agreement.map((_: any, i: number) => (
                        <Cell key={i} fill={AGREEMENT_COLORS[i % AGREEMENT_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                <div className="mt-4 space-y-2">
                  {by_agreement.map((row: any, i: number) => (
                    <div key={row.agreement} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full" style={{ backgroundColor: AGREEMENT_COLORS[i % AGREEMENT_COLORS.length] }} />
                        <span className="font-semibold text-slate-700">{row.agreement}</span>
                      </div>
                      <div className="flex gap-4 text-slate-500">
                        <span>{row.shipments} shipments</span>
                        <span className="font-medium text-slate-700">{formatCurrency(row.savings)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ROI callout */}
      <Card className="border-brand-200 bg-gradient-to-r from-brand-50 to-white">
        <CardContent className="flex items-center justify-between p-5">
          <div>
            <p className="text-sm font-semibold text-brand-800">Annual savings projection</p>
            <p className="mt-0.5 text-xs text-brand-600">
              At your current run rate, you are on track to save{" "}
              <strong>{formatCurrency(annual_projection)}</strong> this year through Uportai.
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-brand-700">{formatCurrency(annual_projection)}</p>
            <Badge variant="default" className="mt-1">Based on your YTD data</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
