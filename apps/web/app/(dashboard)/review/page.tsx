import { ReviewQueue } from "@/components/review/review-queue";

export const metadata = { title: "Review Queue — Uportai" };

export default function ReviewPage() {
  return (
    <div className="min-h-screen bg-[#F8FAFF]">
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Review Queue</h1>
          <p className="mt-1 text-sm text-slate-500">
            Origin determinations flagged for human review. Approve to confirm or override with your decision.
          </p>
        </div>
        <ReviewQueue />
      </div>
    </div>
  );
}
