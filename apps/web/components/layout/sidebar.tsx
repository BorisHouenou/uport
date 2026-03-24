"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileCheck2,
  PackageSearch,
  ScrollText,
  Users,
  TrendingUp,
  MessageSquare,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Origin Check", href: "/origin", icon: ShieldCheck },
  { name: "Certificates", href: "/certificates", icon: FileCheck2 },
  { name: "Bill of Materials", href: "/bom", icon: PackageSearch },
  { name: "Suppliers", href: "/supplier", icon: Users },
  { name: "Savings", href: "/savings", icon: TrendingUp },
  { name: "Assistant", href: "/assistant", icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
          <ShieldCheck className="h-4 w-4 text-white" />
        </div>
        <span className="text-lg font-bold text-slate-900">Uportai</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-4">
        {navigation.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-brand-50 text-brand-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
            >
              <item.icon
                className={cn("h-4 w-4 shrink-0", active ? "text-brand-600" : "text-slate-400")}
              />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="border-t border-slate-200 px-3 py-3">
        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
        >
          <Settings className="h-4 w-4 text-slate-400" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
