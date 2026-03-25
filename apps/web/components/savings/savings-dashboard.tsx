"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency } from "@/lib/utils";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Legend, Cell,
} from "recharts";
import { TrendingUp, DollarSign, FileCheck2, ShieldCheck } from "lucide-react";

// TODO Sprint 7-8: fetch from /api/v1/savings/summary
const MOCK_MONTHLY = [
  { month: "Oct",  savings: 8200,  shipments: 3 },
  { month: "Nov",  savings: 14500, shipments: 5 },
  { month: "Dec",  savings: 11000, shipments: 4 },
  { month: "Jan",  savings: 19800, shipments: 7 },
  { month: "Feb",  savings: 22400, shipments: 8 },
  { month: "Mar",  savings: 31200, shipments: 11 },
];

const MOCK_BY_AGREEMENT = [
  { agreement: "CUSMA", savings: 68400, shipments: 24, avg_rate_saved: "6.5%" },
  { agreement: "CETA",  savings: 29800, shipments: 10, avg_rate_saved: "4.2%" },
  { agreement: "CPTPP", savings: 9100,  shipments:  4, avg_rate_saved: "3.8%" },
];

const AGREEMENT_COLORS = ["#0062c9", "#22c55e", "#f59e0b"];

const KPIs = [
  { label: "Total Savings YTD",      value: formatCurrency(107300), icon: DollarSign,  color: "text-green-600",  bg: "bg-green-50" },
  { label: "Certificates Issued",    value: "38",                   icon: FileCheck2,  color: "text-brand-600",  bg: "bg-brand-50" },
  { label: "Avg Saving / Shipment",  value: formatCurrency(2824),   icon: TrendingUp,  color: "text-violet-600", bg: "bg-violet-50" },
  { label: "Compliance Rate",        value: "97%",                  icon: ShieldCheck, color: "text-emerald-600", bg: "bg-emerald-50" },
];

export function SavingsDashboard() {
  return (
    <div className="space-y-6">
      {/* KPI row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {KPIs.map((kpi) => (
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
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={MOCK_MONTHLY} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="savingsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#0062c9" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#0062c9" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false}
                  tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: 12 }}
                  formatter={(v: any) => [formatCurrency(v), "Savings"]}
                />
                <Area type="monotone" dataKey="savings" stroke="#0062c9" strokeWidth={2}
                  fill="url(#savingsGrad)" dot={{ fill: "#0062c9", r: 3 }} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* By agreement */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Savings by Agreement</CardTitle>
            <CardDescription>Which FTAs deliver the most value</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={MOCK_BY_AGREEMENT} layout="vertical" margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false}
                  tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="agreement" tick={{ fontSize: 11, fill: "#475569" }} axisLine={false} tickLine={false} width={52} />
                <Tooltip
                  contentStyle={{ borderRadius: "0.5rem", border: "1px solid #e2e8f0", fontSize: 12 }}
                  formatter={(v: any) => [formatCurrency(v), "Savings"]}
                />
                <Bar dataKey="savings" radius={[0, 4, 4, 0]}>
                  {MOCK_BY_AGREEMENT.map((_, i) => (
                    <Cell key={i} fill={AGREEMENT_COLORS[i % AGREEMENT_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            {/* Table */}
            <div className="mt-4 space-y-2">
              {MOCK_BY_AGREEMENT.map((row, i) => (
                <div key={row.agreement} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: AGREEMENT_COLORS[i] }} />
                    <span className="font-semibold text-slate-700">{row.agreement}</span>
                  </div>
                  <div className="flex gap-4 text-slate-500">
                    <span>{row.shipments} shipments</span>
                    <span className="font-medium text-slate-700">{formatCurrency(row.savings)}</span>
                  </div>
                </div>
              ))}
            </div>
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
              <strong>{formatCurrency(134000)}</strong> this year through Uportai.
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-brand-700">{formatCurrency(134000)}</p>
            <Badge variant="default" className="mt-1">Industry average benchmark</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
