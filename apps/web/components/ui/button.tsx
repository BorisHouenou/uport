"use client";
import { cn } from "@/lib/utils";
import { cva, type VariantProps } from "class-variance-authority";
import { Loader2 } from "lucide-react";
import React from "react";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:   "bg-brand-600 text-white hover:bg-brand-700",
        secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200",
        outline:   "border border-slate-200 bg-white text-slate-900 hover:bg-slate-50",
        ghost:     "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
        destructive: "bg-red-600 text-white hover:bg-red-700",
        success:   "bg-green-600 text-white hover:bg-green-700",
      },
      size: {
        sm:   "h-8  px-3 text-xs",
        md:   "h-9  px-4 text-sm",
        lg:   "h-11 px-6 text-sm",
        icon: "h-9  w-9",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
      {children}
    </button>
  )
);
Button.displayName = "Button";
