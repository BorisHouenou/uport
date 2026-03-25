"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { MessageBubble, type ChatMessage, type Citation } from "./message-bubble";
import { Send, Bot } from "lucide-react";

const AGREEMENTS = ["cusma", "ceta", "cptpp"];

const STARTERS = [
  "What RVC threshold applies to passenger vehicles under CUSMA?",
  "How do I calculate Regional Value Content using the Build-Down method?",
  "What certificates of origin does CETA require?",
  "What is the de minimis rule under CUSMA Article 4.18?",
];

export function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [filter, setFilter] = useState<string[]>([]);
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const toggleFilter = (code: string) =>
    setFilter((prev) => (prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]));

  const send = async (text: string) => {
    if (!text.trim() || streaming) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);

    // Placeholder assistant message
    const assistantIdx = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const resp = await fetch("/api/v1/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, userMsg].map((m) => ({ role: m.role, content: m.content })),
          agreement_filter: filter.length ? filter : null,
        }),
        signal: ctrl.signal,
      });

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      if (!resp.body) throw new Error("No response body");

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = "";
      let citations: Citation[] | undefined;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const raw = decoder.decode(value, { stream: true });
        // Each SSE line: "data: <json>\n\n"
        for (const line of raw.split("\n")) {
          const trimmed = line.replace(/^data:\s*/, "").trim();
          if (!trimmed || trimmed === "[DONE]") continue;
          try {
            const chunk = JSON.parse(trimmed);
            if (chunk.type === "text") {
              accumulated += chunk.text;
              setMessages((prev) => {
                const updated = [...prev];
                updated[assistantIdx] = { role: "assistant", content: accumulated };
                return updated;
              });
            } else if (chunk.type === "citations") {
              citations = chunk.citations;
            }
          } catch {
            // partial JSON — skip
          }
        }
      }

      // Attach citations to the assistant message
      if (citations) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[assistantIdx] = { role: "assistant", content: accumulated, citations };
          return updated;
        });
      }
    } catch (err: unknown) {
      if ((err as Error).name !== "AbortError") {
        setMessages((prev) => {
          const updated = [...prev];
          updated[assistantIdx] = {
            role: "assistant",
            content: "Sorry, I encountered an error. Please try again.",
          };
          return updated;
        });
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  };

  return (
    <div className="flex h-[calc(100vh-10rem)] flex-col gap-4">
      {/* Agreement filter */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-500">Filter by:</span>
        {AGREEMENTS.map((code) => (
          <button
            key={code}
            onClick={() => toggleFilter(code)}
            className={`rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide transition-colors ${
              filter.includes(code)
                ? "border-brand-500 bg-brand-600 text-white"
                : "border-slate-200 bg-white text-slate-500 hover:border-brand-300"
            }`}
          >
            {code}
          </button>
        ))}
        {filter.length > 0 && (
          <button onClick={() => setFilter([])} className="text-xs text-slate-400 hover:text-slate-600">
            clear
          </button>
        )}
      </div>

      {/* Messages area */}
      <Card className="flex-1 overflow-hidden">
        <CardContent className="flex h-full flex-col p-0">
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.length === 0 ? (
              <EmptyState onSelect={send} />
            ) : (
              messages.map((msg, i) => <MessageBubble key={i} message={msg} />)
            )}
            {streaming && messages[messages.length - 1]?.content === "" && (
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Spinner size="sm" />
                Thinking…
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-100 p-4">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="flex gap-2"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={streaming}
                placeholder="Ask a trade compliance question…"
                className="flex-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:opacity-50"
              />
              <Button type="submit" disabled={!input.trim() || streaming} className="shrink-0">
                {streaming ? <Spinner size="sm" /> : <Send className="h-4 w-4" />}
              </Button>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 py-12">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50">
        <Bot className="h-7 w-7 text-brand-600" />
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold text-slate-800">Compliance Assistant</p>
        <p className="mt-1 text-xs text-slate-500">
          Ask anything about Rules of Origin, CUSMA, CETA, or CPTPP.
        </p>
      </div>
      <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
        {STARTERS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-xs text-slate-600 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
