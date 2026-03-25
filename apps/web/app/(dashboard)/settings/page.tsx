import type { Metadata } from "next";
import { QBOConnectCard } from "@/components/settings/qbo-connect-card";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage integrations, notifications, and account preferences.
        </p>
      </div>

      <section className="space-y-4">
        <h2 className="text-base font-semibold text-slate-700">Integrations</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <QBOConnectCard />
        </div>
      </section>
    </div>
  );
}
