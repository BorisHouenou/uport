"use client";

import Link from "next/link";
import { FileCheck2, PackageSearch, ShieldCheck, MessageSquare } from "lucide-react";

const actions = [
  { title: "New Origin Check", href: "/origin", icon: ShieldCheck, primary: true },
  { title: "Upload BOM", href: "/bom", icon: PackageSearch, primary: false },
  { title: "Generate Certificate", href: "/certificates", icon: FileCheck2, primary: false },
  { title: "Ask AI Assistant", href: "/assistant", icon: MessageSquare, primary: false },
];

export function QuickActions() {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {actions.map((action) => (
        <Link
          key={action.href}
          href={action.href}
          className={
            action.primary
              ? "btn-primary"
              : "btn-outline"
          }
        >
          <action.icon className="h-4 w-4" />
          {action.title}
        </Link>
      ))}
    </div>
  );
}
