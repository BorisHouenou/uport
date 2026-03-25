import { ReviewQueue } from "@/components/review/review-queue";

export const metadata = { title: "Review Queue — Uportai" };

export default function ReviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Review Queue</h1>
        <p className="mt-1 text-sm text-slate-500">
          Origin determinations flagged for human review due to low AI confidence.
          Approve to confirm the result or reject to override it.
        </p>
      </div>
      <ReviewQueue />
    </div>
  );
}
