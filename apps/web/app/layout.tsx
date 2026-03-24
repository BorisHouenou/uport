import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "Uportai — Rules of Origin Compliance",
    template: "%s | Uportai",
  },
  description:
    "Automated Rules of Origin certification. Recapture $134K average savings per SME exporter. CUSMA, CETA, CPTPP, AfCFTA and more.",
  keywords: ["rules of origin", "RoO compliance", "CUSMA", "CETA", "trade compliance", "certificate of origin"],
  robots: { index: false, follow: false }, // private SaaS app
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en" className={inter.variable}>
        <body className="min-h-screen bg-slate-50 font-sans antialiased">
          <QueryProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: { borderRadius: "0.5rem", fontSize: "0.875rem" },
              }}
            />
          </QueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
