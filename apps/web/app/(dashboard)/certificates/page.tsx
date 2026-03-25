import type { Metadata } from "next";
import { CertificatesPanel } from "@/components/certificates/certificates-panel";

export const metadata: Metadata = { title: "Certificates" };

export default function CertificatesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Certificates of Origin</h1>
        <p className="mt-1 text-sm text-slate-500">
          All generated certificates — download, view, or reissue.
        </p>
      </div>
      <CertificatesPanel />
    </div>
  );
}
