"use client";

import { useState } from "react";
import { DeclarationsTable } from "@/components/supplier/declarations-table";
import { DeclarationForm } from "@/components/supplier/declaration-form";
import { UserPlus, X } from "lucide-react";

export default function SupplierPage() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#F8FAFF]">
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Supplier Portal</h1>
            <p className="mt-1 text-sm text-slate-500">
              Manage supplier origin declarations, track expiry, and attach supporting documents.
            </p>
          </div>
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-[#2563EB] px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#1D4ED8]"
          >
            <UserPlus className="h-4 w-4" />
            Invite Supplier
          </button>
        </div>

        {/* Declarations grid */}
        <DeclarationsTable onInvite={() => setModalOpen(true)} />

        {/* Modal */}
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
              className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
              onClick={() => setModalOpen(false)}
            />
            <div className="relative z-10 w-full max-w-lg rounded-2xl bg-white shadow-2xl">
              <div className="flex items-center justify-between border-b border-[#E2E8F0] px-6 py-4">
                <div>
                  <p className="font-semibold text-slate-800">New Supplier Declaration</p>
                  <p className="text-xs text-slate-500">
                    Record a supplier&apos;s declaration of origin for a product in your BOM.
                  </p>
                </div>
                <button
                  onClick={() => setModalOpen(false)}
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="p-6">
                <DeclarationForm />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
