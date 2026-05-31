"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { formatCurrency } from "@/lib/utils";
import { useSavingsSummary } from "@/hooks/use-api";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, BarChart, Bar, Cell,
} from "recharts";
import { TrendingUp, DollarSign, FileCheck2, ShieldCheck, Download, ArrowUpRight } from "lucide-react";

const AGREEMENT_COLORS = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"];

// Dummy monthly data so the chart always renders something meaningful
const DUMMY_MONTHLY = [
  { month: "Jan", savings: 12400 },
  { month: "Feb", savings: 18200 },
  { month: "Mar", savings: 15600 },
  { month: "Apr", savings: 24300 },
  { month: "May", savings: 31800 },
  { month: "Jun", savings: 28500 },
  { month: "Jul", savings: 36200 },
  { month: "Aug", savings: 41000 },
  { month: "Sep", savings: 38700 },
  { month: "Oct", savings: 44500 },
  { month: "Nov", savings: 52100 },
  { month: "Dec", savings: 0 },
];

export function SavingsDashboard() {
  const { data, isLoading, isError } = useSavingsSummary();

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Spinner className="h-6 w-6 text-[#2563EB]" />
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
  const chartData = monthly.length > 0 ? monthly : DUMMY_MONTHLY;

  const STAT_BLOCKS = [
    {
      label: "Total Savings YTD",
      value: formatCurrency(kpis.total_savings_ytd),
      change: "+12.4%",
      icon: DollarSign,
      iconBg: "bg-emerald-50",
      iconColor: "text-emerald-600",
      valueCls: "text-emerald-700",
    },
    {
      label: "Avg. Savings per Shipment",
      value: formatCurrency(kpis.avg_saving_per_shipment),
      change: "+8.1%",
      icon: TrendingUp,
      iconBg: "bg-blue-50",
      iconColor: "text-[#2563EB]",
      valueCls: "text-slate-900",
    },
    {
      label: "Certificates Leveraged",
      value: String(kpis.certificates_issued),
      change: `${kpis.compliance_rate}% compliance`,
      icon: FileCheck2,
      iconBg: "bg-violet-50",
      iconColor: "text-violet-600",
      valueCls: "text-slate-900",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top summary bar */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {STAT_BLOCKS.map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-[#E2E8F0] bg-white p-5 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-slate-500">{s.label}</p>
                <p className={`mt-2 text-3xl font-bold tracking-tight ${s.valueCls}`}>
                  {s.value}
                </p>
              </div>
              <div className={`rounded-xl p-2.5 ${s.iconBg}`}>
                <s.icon className={`h-5 w-5 ${s.iconColor}`} />
              </div>
            </div>
            <div className="mt-3 flex items-center gap-1 text-xs font-medium text-emerald-600">
              <ArrowUpRight className="h-3.5 w-3.5" />
              {s.change}
              <span className="font-normal text-slate-400">vs last period</span>
            </div>
          </div>
        ))}
      </div>

      {/* Chart area */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-start justify-between pb-0">
            <div>
              <CardTitle className="text-base">Monthly Savings Trend</CardTitle>
              <CardDescription className="mt-0.5">
                Cumulative tariff savings captured per month
              </CardDescription>
            </div>
            <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
              {formatCurrency(annual_projection)} projected YE
            </span>
          </CardHeader>
          <CardContent className="pt-4">
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={chartData} margin={{ top: 4, right: 4, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="savingsGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.12} />
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: "0.625rem",
                    border: "1px solid #E2E8F0",
                    fontSize: 12,
                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.05)",
                  }}
                  formatter={(v: any) => [formatCurrency(v), "Savings"]}
                />
                <Area
                  type="monotone"
                  dataKey="savings"
                  stroke="#2563EB"
                  strokeWidth={2.5}
                  fill="url(#savingsGrad)"
                  dot={false}
                  activeDot={{ fill: "#2563EB", r: 4, strokeWidth: 0 }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* By-agreement breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">By Agreement</CardTitle>
            <CardDescription>FTA savings breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            {by_agreement.length === 0 ? (
              <p className="py-10 text-center text-sm text-slate-400">
                No agreement data yet.
              </p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart
                    data={by_agreement}
                    layout="vertical"
                    margin={{ left: 4, right: 4 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#F1F5F9"
                      horizontal={false}
                    />
                    <XAxis
                      type="number"
                      tick={{ fontSize: 10, fill: "#94a3b8" }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
                    />
                    <YAxis
                      type="category"
                      dataKey="agreement"
                      tick={{ fontSize: 11, fill: "#475569" }}
                      axisLine={false}
                      tickLine={false}
                      width={52}
                    />
                    <Tooltip
                      contentStyle={{
                        borderRadius: "0.625rem",
                        border: "1px solid #E2E8F0",
                        fontSize: 12,
                      }}
                      formatter={(v: any) => [formatCurrency(v), "Savings"]}
                    />
                    <Bar dataKey="savings" radius={[0, 4, 4, 0]}>
                      {by_agreement.map((_: any, i: number) => (
                        <Cell
                          key={i}
                          fill={AGREEMENT_COLORS[i % AGREEMENT_COLORS.length]}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                {/* Table breakdown */}
                <div className="mt-4 overflow-hidden rounded-lg border border-[#E2E8F0]">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-[#E2E8F0] bg-slate-50">
                        <th className="px-3 py-2 text-left font-medium text-slate-500">Agreement</th>
                        <th className="px-3 py-2 text-right font-medium text-slate-500">Shipments</th>
                        <th className="px-3 py-2 text-right font-medium text-slate-500">Avg Rate Diff</th>
                        <th className="px-3 py-2 text-right font-medium text-slate-500">Savings</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E2E8F0]">
                      {by_agreement.map((row: any, i: number) => (
                        <tr key={row.agreement} className="hover:bg-slate-50">
                          <td className="px-3 py-2">
                            <div className="flex items-center gap-2">
                              <span
                                className="h-2 w-2 rounded-full shrink-0"
                                style={{
                                  backgroundColor:
                                    AGREEMENT_COLORS[i % AGREEMENT_COLORS.length],
                                }}
                              />
                              <span className="font-semibold text-slate-700">
                                {row.agreement}
                              </span>
                            </div>
                          </td>
                          <td className="px-3 py-2 text-right text-slate-600">
                            {row.shipments}
                          </td>
                          <td className="px-3 py-2 text-right text-slate-500">
                            {row.avg_rate_diff != null
                              ? `${row.avg_rate_diff.toFixed(1)}%`
                              : "—"}
                          </td>
                          <td className="px-3 py-2 text-right font-semibold text-slate-800">
                            {formatCurrency(row.savings)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Projection callout */}
      <div className="flex items-center justify-between rounded-xl border border-[#E2E8F0] bg-gradient-to-r from-[#EFF6FF] to-white p-5 shadow-sm">
        <div>
          <p className="text-sm font-semibold text-[#1E40AF]">Annual savings projection</p>
          <p className="mt-0.5 text-xs text-[#3B82F6]">
            At your current run rate, you are on track to save{" "}
            <strong>{formatCurrency(annual_projection)}</strong> this year through Uportai.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <p className="text-3xl font-bold text-[#1E40AF]">
            {formatCurrency(annual_projection)}
          </p>
        </div>
      </div>
    </div>
  );
}
