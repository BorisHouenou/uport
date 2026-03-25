import type { Metadata } from "next";
import { DeclarationForm } from "@/components/supplier/declaration-form";
import { DeclarationsTable } from "@/components/supplier/declarations-table";

export const metadata: Metadata = { title: "Suppliers" };

export default function SupplierPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Supplier Declarations</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage supplier origin declarations. Track expiry and attach supporting documents.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <DeclarationForm />
        </div>
        <div className="lg:col-span-3">
          <DeclarationsTable />
        </div>
      </div>
    </div>
  );
}
