"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Spinner } from "@/components/ui/spinner";
import { useSubscription, useCreateCheckout, useCustomerPortal, useCertificateUsage } from "@/hooks/use-api";
import { Progress } from "@/components/ui/progress";
import { CheckCircle2, Zap, Building2, Rocket } from "lucide-react";
import toast from "react-hot-toast";

const PLANS = [
  {
    id: "starter",
    name: "Starter",
    price: "$149",
    period: "/month",
    description: "Perfect for small exporters getting started.",
    icon: Rocket,
    color: "text-slate-600",
    bg: "bg-slate-50",
    border: "border-slate-200",
    features: [
      "25 shipment determinations / month",
      "Up to 3 team members",
      "CUSMA, CETA, CPTPP coverage",
      "PDF certificate generation",
      "Email support",
    ],
  },
  {
    id: "growth",
    name: "Growth",
    price: "$499",
    period: "/month",
    description: "For growing teams with higher shipment volumes.",
    icon: Zap,
    color: "text-brand-600",
    bg: "bg-brand-50",
    border: "border-brand-300",
    popular: true,
    features: [
      "100 shipment determinations / month",
      "Up to 10 team members",
      "All FTAs + AfCFTA (beta)",
      "REST API access",
      "QuickBooks / ERP sync",
      "Priority support",
    ],
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: "$1,499",
    period: "/month",
    description: "Unlimited scale, SSO, and dedicated onboarding.",
    icon: Building2,
    color: "text-violet-600",
    bg: "bg-violet-50",
    border: "border-violet-200",
    features: [
      "Unlimited determinations",
      "Unlimited users + SSO",
      "All FTAs + custom ruleset uploads",
      "Dedicated customer success manager",
      "SLA 99.9% uptime",
      "Custom contract & invoicing",
    ],
  },
];

export function PricingPanel() {
  const { data: subscription, isLoading } = useSubscription();
  const { data: usage } = useCertificateUsage();
  const createCheckout = useCreateCheckout();
  const customerPortal = useCustomerPortal();
  const [upgrading, setUpgrading] = useState<string | null>(null);

  const currentTier = subscription?.tier ?? "free";
  const currentStatus = subscription?.status ?? "none";

  const handleUpgrade = async (planId: string) => {
    setUpgrading(planId);
    try {
      const { url } = await createCheckout.mutateAsync({
        tier: planId,
        success_url: `${window.location.origin}/settings/billing?success=1`,
        cancel_url: `${window.location.origin}/settings/billing`,
      });
      window.location.href = url;
    } catch {
      toast.error("Failed to start checkout. Please try again.");
    } finally {
      setUpgrading(null);
    }
  };

  const handleManage = async () => {
    try {
      const { url } = await customerPortal.mutateAsync(
        `${window.location.origin}/settings/billing`
      );
      window.location.href = url;
    } catch {
      toast.error("Failed to open billing portal.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current plan banner */}
      {currentTier !== "free" && currentStatus === "active" && (
        <Card className="border-brand-200 bg-gradient-to-r from-brand-50 to-white">
          <CardContent className="flex items-center justify-between p-5">
            <div>
              <p className="text-sm font-semibold text-brand-800">
                Current plan:{" "}
                <span className="capitalize">{currentTier}</span>
              </p>
              <p className="mt-0.5 text-xs text-brand-600">
                Your subscription is active.
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={handleManage} loading={customerPortal.isPending}>
              Manage billing
            </Button>
          </CardContent>
        </Card>
      )}

      {currentStatus === "past_due" && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="flex items-center justify-between p-5">
            <p className="text-sm font-semibold text-red-700">
              Payment past due — please update your payment method to avoid service interruption.
            </p>
            <Button variant="outline" size="sm" onClick={handleManage}>
              Update payment
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Certificate usage meter */}
      {usage && !usage.unlimited && (
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-slate-700">Certificates this month</p>
              <span className="text-sm font-semibold text-slate-900">
                {usage.used} / {usage.included}
              </span>
            </div>
            <Progress
              value={usage.included > 0 ? Math.min(100, (usage.used / usage.included) * 100) : 0}
              color={usage.used >= usage.included ? "red" : usage.used >= usage.included * 0.8 ? "yellow" : "green"}
            />
            {usage.overage > 0 && (
              <p className="mt-1.5 text-xs text-red-600">
                {usage.overage} certificate{usage.overage !== 1 ? "s" : ""} over limit — billed at $2/each
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Plan cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {PLANS.map((plan) => {
          const Icon = plan.icon;
          const isCurrent = currentTier === plan.id;
          return (
            <Card
              key={plan.id}
              className={`relative flex flex-col border-2 ${isCurrent ? "border-brand-500" : plan.border}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-brand-600 text-white shadow-sm">Most popular</Badge>
                </div>
              )}
              <CardHeader className="pb-3">
                <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${plan.bg}`}>
                  <Icon className={`h-5 w-5 ${plan.color}`} />
                </div>
                <CardTitle className="text-lg">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col justify-between gap-5">
                <div>
                  <p className="mb-4">
                    <span className="text-3xl font-bold text-slate-900">{plan.price}</span>
                    <span className="text-sm text-slate-500">{plan.period}</span>
                  </p>
                  <ul className="space-y-2">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2 text-xs text-slate-600">
                        <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-green-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>

                {isCurrent ? (
                  <Button variant="outline" disabled className="w-full">
                    Current plan
                  </Button>
                ) : (
                  <Button
                    className="w-full"
                    onClick={() => handleUpgrade(plan.id)}
                    loading={upgrading === plan.id}
                  >
                    {currentTier === "free" ? "Get started" : "Switch plan"}
                  </Button>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <p className="text-center text-xs text-slate-400">
        All plans include a 14-day free trial. Cancel any time. Prices in USD.
      </p>
    </div>
  );
}
