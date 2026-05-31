"use client";

import { UserButton, OrganizationSwitcher } from "@clerk/nextjs";
import { usePathname } from "next/navigation";
import { Bell, Plus } from "lucide-react";
import Link from "next/link";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/origin": "Origin Check",
  "/certificates": "Certificates",
  "/bom": "Bill of Materials",
  "/supplier": "Suppliers",
  "/savings": "Savings",
  "/review": "Review Queue",
  "/assistant": "AI Assistant",
  "/settings": "Settings",
  "/settings/billing": "Billing",
};

export function TopBar() {
  const pathname = usePathname();
  const title = pageTitles[pathname] ?? pageTitles[`/${pathname.split("/")[1]}`] ?? "Uportai";

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-[#E2E8F0] bg-white px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-base font-semibold text-[#0A0F1E]">{title}</h2>
        <OrganizationSwitcher
          appearance={{
            elements: {
              organizationSwitcherTrigger:
                "rounded-lg border border-slate-200 px-2.5 py-1 text-xs text-slate-600 hover:bg-slate-50 transition-colors",
            },
          }}
        />
      </div>
      <div className="flex items-center gap-2">
        <button
          type="button"
          className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-[#2563EB]" />
        </button>
        <Link
          href="/origin"
          className="btn-primary text-xs px-3 py-2"
        >
          <Plus className="h-3.5 w-3.5" />
          New Check
        </Link>
        <div className="pl-1">
          <UserButton afterSignOutUrl="/sign-in" />
        </div>
      </div>
    </header>
  );
}
