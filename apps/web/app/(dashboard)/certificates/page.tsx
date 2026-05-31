import type { Metadata } from "next";
import { CertificatesPanel } from "@/components/certificates/certificates-panel";

export const metadata: Metadata = { title: "Certificates" };

export default function CertificatesPage() {
  return (
    <div className="min-h-screen bg-[#F8FAFF] px-0 py-0">
      <div className="space-y-6 p-6">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Certificates</h1>
            <p className="mt-1 text-sm text-slate-500">
              All generated certificates of origin — download, view, or reissue.
            </p>
          </div>
        </div>
        <CertificatesPanel />
      </div>
    </div>
  );
}
