import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number;  // 0-100
  className?: string;
  color?: "blue" | "green" | "yellow" | "red";
}

const COLORS = {
  blue:   "bg-brand-500",
  green:  "bg-green-500",
  yellow: "bg-yellow-400",
  red:    "bg-red-500",
};

export function Progress({ value, className, color = "blue" }: ProgressProps) {
  return (
    <div className={cn("h-2 w-full rounded-full bg-slate-100", className)}>
      <div
        className={cn("h-full rounded-full transition-all", COLORS[color])}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}

export function ConfidenceMeter({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  const color = pct >= 90 ? "green" : pct >= 70 ? "yellow" : "red";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-500">Confidence</span>
        <span className={cn("font-medium", pct >= 90 ? "text-green-600" : pct >= 70 ? "text-yellow-600" : "text-red-600")}>
          {pct}%
        </span>
      </div>
      <Progress value={pct} color={color} />
    </div>
  );
}
