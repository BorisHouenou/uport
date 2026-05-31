import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/topbar";

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { userId } = await auth();
  if (!userId) redirect("/sign-in");

  return (
    <div className="flex h-screen overflow-hidden bg-[#F8FAFF]">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Blue accent bar */}
        <div className="h-0.5 w-full shrink-0 bg-gradient-to-r from-[#2563EB] via-[#3B82F6] to-[#60A5FA]" />
        <TopBar />
        <main className="flex-1 overflow-y-auto scrollbar-thin p-6">{children}</main>
      </div>
    </div>
  );
}
