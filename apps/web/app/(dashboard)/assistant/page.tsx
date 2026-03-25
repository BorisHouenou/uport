import type { Metadata } from "next";
import { ChatPanel } from "@/components/assistant/chat-panel";

export const metadata: Metadata = { title: "Compliance Assistant" };

export default function AssistantPage() {
  return (
    <div className="flex h-full flex-col space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Compliance Assistant</h1>
        <p className="mt-1 text-sm text-slate-500">
          AI-powered Q&amp;A grounded in CUSMA, CETA, CPTPP, and CPTPP agreement texts.
          Every answer cites the source article or annex.
        </p>
      </div>
      <ChatPanel />
    </div>
  );
}
