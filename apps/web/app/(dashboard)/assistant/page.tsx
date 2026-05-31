import type { Metadata } from "next";
import { ChatPanel } from "@/components/assistant/chat-panel";

export const metadata: Metadata = { title: "Compliance Assistant" };

export default function AssistantPage() {
  return (
    <div className="-m-6 flex h-[calc(100vh-4.5rem)] flex-col">
      <ChatPanel />
    </div>
  );
}
