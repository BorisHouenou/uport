import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { QueryProvider } from "@/components/providers/query-provider";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: {
    default: "Uportai — AI Trade Compliance Engine",
    template: "%s | Uportai",
  },
  description:
    "Automate Rules of Origin compliance with AI. Reclaim $134K average annual savings per SME exporter across CUSMA, CETA, CPTPP, AfCFTA and 170+ trade agreements.",
  keywords: ["rules of origin", "RoO compliance", "CUSMA", "CETA", "AfCFTA", "trade compliance", "certificate of origin", "AI compliance"],
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <html lang="en" className={`${inter.variable} ${jakarta.variable}`}>
        <body className="min-h-screen bg-background font-sans antialiased">
          <QueryProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  borderRadius: "0.625rem",
                  fontSize: "0.875rem",
                  fontWeight: "500",
                  boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                },
              }}
            />
          </QueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
