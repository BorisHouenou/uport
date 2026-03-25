import { cn } from "@/lib/utils";
import { type VariantProps, cva } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default:     "bg-brand-100 text-brand-700",
        success:     "bg-green-100 text-green-700",
        warning:     "bg-yellow-100 text-yellow-700",
        destructive: "bg-red-100 text-red-700",
        outline:     "border border-slate-200 text-slate-600",
        secondary:   "bg-slate-100 text-slate-700",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
