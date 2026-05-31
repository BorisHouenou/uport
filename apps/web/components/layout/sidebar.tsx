"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUser } from "@clerk/nextjs";
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
  ClipboardCheck,
  Plus,
  Zap,
} from "lucide-react";
import { cn } from "@/lib/utils";

const complianceNav = [
  { name: "Origin Check", href: "/origin", icon: ShieldCheck },
  { name: "Bill of Materials", href: "/bom", icon: PackageSearch },
  { name: "Certificates", href: "/certificates", icon: FileCheck2 },
];

const operationsNav = [
  { name: "Suppliers", href: "/supplier", icon: Users },
  { name: "Review Queue", href: "/review", icon: ClipboardCheck },
  { name: "Savings", href: "/savings", icon: TrendingUp },
];

const intelligenceNav = [
  { name: "AI Assistant", href: "/assistant", icon: MessageSquare },
];

function NavItem({ href, icon: Icon, name }: { href: string; icon: React.ElementType; name: string }) {
  const pathname = usePathname();
  const active = pathname === href || pathname.startsWith(href + "/");
  return (
    <Link
      href={href}
      className={cn(
        "nav-pill",
        active
          ? "bg-[#2563EB] text-white"
          : "text-[#94a3b8] hover:bg-[#162947] hover:text-white"
      )}
    >
      <Icon className={cn("h-4 w-4 shrink-0", active ? "text-white" : "text-[#4a6fa5]")} />
      {name}
    </Link>
  );
}

export function Sidebar() {
  const { user } = useUser();
  const initials = user
    ? `${user.firstName?.[0] ?? ""}${user.lastName?.[0] ?? ""}`.toUpperCase() || "U"
    : "U";

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col bg-[#0F1E3C] border-r border-[#1a2f52]">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b border-[#1a2f52] px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[#2563EB] to-[#1d4ed8] shadow-lg">
          <ShieldCheck className="h-4 w-4 text-white" />
        </div>
        <div>
          <span className="text-base font-bold text-white tracking-tight">Uportai</span>
        </div>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto scrollbar-hide px-3 py-4 space-y-5">
        {/* Dashboard */}
        <div>
          <Link
            href="/dashboard"
            className={cn(
              "nav-pill mb-1",
              usePathname() === "/dashboard"
                ? "bg-[#2563EB] text-white"
                : "text-[#94a3b8] hover:bg-[#162947] hover:text-white"
            )}
          >
            <LayoutDashboard className={cn("h-4 w-4 shrink-0", usePathname() === "/dashboard" ? "text-white" : "text-[#4a6fa5]")} />
            Dashboard
          </Link>
        </div>

        {/* New Check CTA */}
        <Link
          href="/origin"
          className="flex items-center justify-center gap-2 rounded-lg bg-[#2563EB] px-3 py-2.5 text-sm font-semibold text-white transition-all duration-150 hover:bg-[#1D4ED8] hover:shadow-lg active:scale-[0.98]"
        >
          <Plus className="h-4 w-4" />
          New Origin Check
        </Link>

        {/* Compliance section */}
        <div>
          <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-widest text-[#4a6fa5]">
            Compliance
          </p>
          <div className="space-y-0.5">
            {complianceNav.map((item) => (
              <NavItem key={item.href} {...item} />
            ))}
          </div>
        </div>

        {/* Separator */}
        <div className="border-t border-[#1a2f52]" />

        {/* Operations section */}
        <div>
          <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-widest text-[#4a6fa5]">
            Operations
          </p>
          <div className="space-y-0.5">
            {operationsNav.map((item) => (
              <NavItem key={item.href} {...item} />
            ))}
          </div>
        </div>

        {/* Separator */}
        <div className="border-t border-[#1a2f52]" />

        {/* Intelligence section */}
        <div>
          <p className="mb-1.5 px-3 text-[10px] font-semibold uppercase tracking-widest text-[#4a6fa5]">
            Intelligence
          </p>
          <div className="space-y-0.5">
            {intelligenceNav.map((item) => (
              <NavItem key={item.href} {...item} />
            ))}
          </div>
        </div>
      </div>

      {/* User footer */}
      <div className="border-t border-[#1a2f52] px-3 py-3 space-y-1">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#2563EB] to-[#1D4ED8] text-xs font-bold text-white">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-white">
              {user?.fullName ?? user?.firstName ?? "User"}
            </p>
            <span className="inline-flex items-center rounded-full bg-[#1a2f52] px-1.5 py-0.5 text-[10px] font-medium text-[#60A5FA]">
              Admin
            </span>
          </div>
        </div>
        <Link
          href="/settings"
          className="nav-pill text-[#94a3b8] hover:bg-[#162947] hover:text-white"
        >
          <Settings className="h-4 w-4 shrink-0 text-[#4a6fa5]" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
