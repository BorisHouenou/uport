"use client";

import Link from "next/link";
import { FileCheck2, PackageSearch, ShieldCheck, MessageSquare } from "lucide-react";

const actions = [
  {
    title: "New Origin Check",
    description: "Determine RoO for a shipment",
    href: "/origin",
    icon: ShieldCheck,
    color: "bg-brand-50 text-brand-700",
  },
  {
    title: "Upload BOM",
    description: "Import a Bill of Materials",
    href: "/bom",
    icon: PackageSearch,
    color: "bg-violet-50 text-violet-700",
  },
  {
    title: "Generate Certificate",
    description: "Create a Certificate of Origin",
    href: "/certificates",
    icon: FileCheck2,
    color: "bg-green-50 text-green-700",
  },
  {
    title: "Ask Assistant",
    description: "Get compliance guidance",
    href: "/assistant",
    icon: MessageSquare,
    color: "bg-amber-50 text-amber-700",
  },
];

export function QuickActions() {
  return (
    <div>
      <h2 className="mb-3 text-sm font-semibold text-slate-700 uppercase tracking-wide">
        Quick Actions
      </h2>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {actions.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="group flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-brand-200 hover:shadow-md transition-all"
          >
            <div className={`w-fit rounded-lg p-2.5 ${action.color}`}>
              <action.icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 group-hover:text-brand-700 transition-colors">
                {action.title}
              </p>
              <p className="text-xs text-slate-500 mt-0.5">{action.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
