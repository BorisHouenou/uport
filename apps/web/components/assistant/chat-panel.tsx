"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { Spinner } from "@/components/ui/spinner";
import { MessageBubble, type ChatMessage, type Citation } from "./message-bubble";
import { Send, Bot, BookOpen, X } from "lucide-react";
import { cn } from "@/lib/utils";

const AGREEMENTS = ["cusma", "ceta", "cptpp"];

const STARTERS = [
  "What is the RVC threshold for automotive parts under CUSMA?",
  "Can I use cumulation for components from Mexico?",
  "What documents do I need for a EUR.1 certificate?",
  "How do I calculate Regional Value Content using the Build-Down method?",
];

export function ChatPanel() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [filter, setFilter] = useState<string[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [contextSources, setContextSources] = useState<Citation[]>([]);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Collect all citations from assistant messages for the context panel
  useEffect(() => {
    const all: Citation[] = [];
    messages.forEach((m) => {
      if (m.citations) {
        m.citations.forEach((c) => {
          if (!all.find((x) => x.index === c.index && x.source === c.source)) {
            all.push(c);
          }
        });
      }
    });
    setContextSources(all);
  }, [messages]);

  const toggleFilter = (code: string) =>
    setFilter((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
    );

  const send = async (text: string) => {
    if (!text.trim() || streaming) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setStreaming(true);

    const assistantIdx = messages.length + 1;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    const ctrl = new AbortController();
    abortRef.current = ctrl;

    try {
      const token = await getToken();
      const resp = await fetch("/api/v1/assistant/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          messages: [...messages, userMsg].map((m) => ({
            role: m.role,
            content: m.content,
          })),
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

      if (citations) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[assistantIdx] = {
            role: "assistant",
            content: accumulated,
            citations,
          };
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
    <div className="flex h-full overflow-hidden">
      {/* Main chat column */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-[#E2E8F0] bg-white px-5 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#2563EB]">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">Compliance Assistant</p>
              <p className="text-xs text-slate-500">
                Grounded in CUSMA · CETA · CPTPP agreement texts
              </p>
            </div>
          </div>
          {/* Agreement filters */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Filter:</span>
            {AGREEMENTS.map((code) => (
              <button
                key={code}
                onClick={() => toggleFilter(code)}
                className={cn(
                  "rounded-full border px-3 py-0.5 text-xs font-semibold uppercase tracking-wide transition-colors",
                  filter.includes(code)
                    ? "border-[#2563EB] bg-[#2563EB] text-white"
                    : "border-[#E2E8F0] bg-white text-slate-500 hover:border-[#2563EB] hover:text-[#2563EB]"
                )}
              >
                {code}
              </button>
            ))}
            {filter.length > 0 && (
              <button
                onClick={() => setFilter([])}
                className="text-xs text-slate-400 hover:text-slate-600"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto bg-[#F8FAFF] px-5 py-6 space-y-4">
          {messages.length === 0 ? (
            <EmptyState onSelect={(q) => { send(q); }} />
          ) : (
            messages.map((msg, i) => <MessageBubble key={i} message={msg} />)
          )}
          {streaming && messages[messages.length - 1]?.content === "" && (
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#2563EB]">
                <Bot className="h-3.5 w-3.5 text-white" />
              </div>
              <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-sm bg-white px-4 py-2.5 shadow-sm border border-[#E2E8F0]">
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:0ms]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:150ms]" />
                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400 [animation-delay:300ms]" />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-[#E2E8F0] bg-white px-5 py-4">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex items-center gap-3"
          >
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={streaming}
              placeholder="Ask about CUSMA Article 4.2, RVC thresholds, EUR.1 requirements…"
              className="flex-1 rounded-full border border-[#E2E8F0] bg-[#F8FAFF] px-5 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#2563EB] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || streaming}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#2563EB] text-white shadow-sm transition-all hover:bg-[#1D4ED8] disabled:cursor-not-allowed disabled:opacity-40"
            >
              {streaming ? (
                <Spinner className="h-4 w-4 text-white" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </form>
          <p className="mt-2.5 text-center text-[10px] text-slate-400">
            Powered by Claude · Sources cite agreement articles and annexes
          </p>
        </div>
      </div>

      {/* Context sources panel — desktop only */}
      <aside className="hidden w-72 shrink-0 flex-col border-l border-[#E2E8F0] bg-white lg:flex">
        <div className="flex items-center gap-2 border-b border-[#E2E8F0] px-4 py-3">
          <BookOpen className="h-4 w-4 text-[#2563EB]" />
          <p className="text-xs font-semibold text-slate-700">Context Sources</p>
          {contextSources.length > 0 && (
            <span className="ml-auto rounded-full bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-[#2563EB]">
              {contextSources.length}
            </span>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {contextSources.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-10 text-center">
              <BookOpen className="h-8 w-8 text-slate-200" />
              <p className="text-xs text-slate-400">
                Retrieved agreement chunks will appear here as you chat.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {contextSources.map((c, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-[#E2E8F0] bg-[#F8FAFF] p-3"
                >
                  <div className="flex items-center gap-1.5">
                    <span className="rounded-full bg-[#2563EB] px-1.5 py-0.5 text-[9px] font-bold text-white">
                      [{c.index}]
                    </span>
                    <span className="text-[10px] font-semibold uppercase tracking-wide text-[#2563EB]">
                      {c.agreement}
                    </span>
                  </div>
                  <p className="mt-1.5 text-[11px] leading-relaxed text-slate-600">
                    {c.source}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
}

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-6 py-16">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#2563EB] shadow-lg shadow-blue-200">
        <Bot className="h-8 w-8 text-white" />
      </div>
      <div className="text-center">
        <p className="text-base font-semibold text-slate-800">Compliance Assistant</p>
        <p className="mt-1 max-w-xs text-sm text-slate-500">
          Ask anything about Rules of Origin, CUSMA, CETA, or CPTPP. Every answer cites the source article.
        </p>
      </div>
      <div className="grid w-full max-w-xl grid-cols-1 gap-2 sm:grid-cols-2">
        {STARTERS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="rounded-xl border border-[#E2E8F0] bg-white px-4 py-3 text-left text-xs text-slate-600 shadow-sm transition-all hover:border-[#2563EB] hover:shadow-md hover:text-[#2563EB]"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
