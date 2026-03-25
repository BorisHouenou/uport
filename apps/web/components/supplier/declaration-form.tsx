"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useSubmitDeclaration } from "@/hooks/use-api";
import { CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";

const COUNTRIES = [
  { code: "CA", name: "Canada" }, { code: "US", name: "United States" }, { code: "MX", name: "Mexico" },
  { code: "DE", name: "Germany" }, { code: "FR", name: "France" }, { code: "GB", name: "United Kingdom" },
  { code: "JP", name: "Japan" }, { code: "KR", name: "South Korea" }, { code: "AU", name: "Australia" },
  { code: "CN", name: "China" }, { code: "IN", name: "India" },
];

interface DeclarationFormProps {
  defaultProductId?: string;
}

export function DeclarationForm({ defaultProductId = "" }: DeclarationFormProps) {
  const submit = useSubmitDeclaration();
  const [done, setDone] = useState(false);
  const [form, setForm] = useState({
    product_id: defaultProductId,
    supplier_name: "",
    supplier_country: "CA",
    origin_country: "CA",
    valid_from: "",
    valid_until: "",
    declaration_text: "",
  });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.product_id || !form.supplier_name || !form.valid_from || !form.valid_until) {
      toast.error("Fill in all required fields");
      return;
    }
    try {
      await submit.mutateAsync(form);
      setDone(true);
      toast.success("Declaration saved");
    } catch {
      toast.error("Failed to save declaration");
    }
  };

  if (done) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center gap-3 py-10">
          <CheckCircle2 className="h-10 w-10 text-green-500" />
          <p className="font-semibold text-slate-800">Declaration saved</p>
          <Button variant="outline" size="sm" onClick={() => setDone(false)}>
            Add another
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>New Supplier Declaration</CardTitle>
        <CardDescription>
          Record a supplier's declaration of origin for a product in your BOM.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Product ID *">
              <input
                value={form.product_id}
                onChange={(e) => set("product_id", e.target.value)}
                placeholder="UUID from your product catalog"
                className={inputCls}
              />
            </Field>
            <Field label="Supplier Name *">
              <input
                value={form.supplier_name}
                onChange={(e) => set("supplier_name", e.target.value)}
                placeholder="e.g. Acme Steel Inc."
                className={inputCls}
              />
            </Field>
            <Field label="Supplier Country *">
              <CountrySelect value={form.supplier_country} onChange={(v) => set("supplier_country", v)} />
            </Field>
            <Field label="Origin Country *">
              <CountrySelect value={form.origin_country} onChange={(v) => set("origin_country", v)} />
            </Field>
            <Field label="Valid From *">
              <input type="date" value={form.valid_from} onChange={(e) => set("valid_from", e.target.value)} className={inputCls} />
            </Field>
            <Field label="Valid Until *">
              <input type="date" value={form.valid_until} onChange={(e) => set("valid_until", e.target.value)} className={inputCls} />
            </Field>
          </div>

          <Field label="Declaration Text (optional)">
            <textarea
              value={form.declaration_text}
              onChange={(e) => set("declaration_text", e.target.value)}
              rows={3}
              placeholder="Free-form declaration text or certificate reference…"
              className={`${inputCls} resize-none`}
            />
          </Field>

          <Button type="submit" loading={submit.isPending} className="w-full">
            Save Declaration
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

const inputCls =
  "w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500";

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-slate-700">{label}</label>
      {children}
    </div>
  );
}

function CountrySelect({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} className={inputCls}>
      {COUNTRIES.map((c) => (
        <option key={c.code} value={c.code}>{c.name} ({c.code})</option>
      ))}
    </select>
  );
}
