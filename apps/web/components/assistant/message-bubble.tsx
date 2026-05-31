"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { Bot, User, ChevronDown, ChevronUp, BookOpen } from "lucide-react";

export interface Citation {
  index: number;
  source: string;
  agreement: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
}

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div className={cn("flex gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
      {/* Avatar */}
      <div
        className={cn(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-[#2563EB]" : "bg-[#2563EB]"
        )}
      >
        {isUser ? (
          <User className="h-3.5 w-3.5 text-white" />
        ) : (
          <Bot className="h-3.5 w-3.5 text-white" />
        )}
      </div>

      <div className={cn("flex max-w-[78%] flex-col gap-1.5", isUser && "items-end")}>
        {/* Bubble */}
        <div
          className={cn(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "rounded-tr-sm bg-[#2563EB] text-white shadow-sm shadow-blue-200"
              : "rounded-tl-sm border border-[#E2E8F0] bg-white text-slate-800 shadow-sm"
          )}
        >
          {message.content.split("\n").map((line, i) => (
            <p key={i} className={i > 0 ? "mt-1.5" : ""}>
              {renderLine(line)}
            </p>
          ))}
        </div>

        {/* Sources collapsible — assistant only */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="w-full rounded-xl border border-[#E2E8F0] bg-white shadow-sm">
            <button
              onClick={() => setSourcesOpen((v) => !v)}
              className="flex w-full items-center gap-2 px-3 py-2 text-left"
            >
              <BookOpen className="h-3.5 w-3.5 text-[#2563EB]" />
              <span className="flex-1 text-xs font-medium text-slate-600">
                Sources ({message.citations.length})
              </span>
              {sourcesOpen ? (
                <ChevronUp className="h-3.5 w-3.5 text-slate-400" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
              )}
            </button>
            {sourcesOpen && (
              <div className="border-t border-[#E2E8F0] px-3 pb-3 pt-2">
                <div className="flex flex-wrap gap-1.5">
                  {message.citations.map((c) => (
                    <span
                      key={c.index}
                      title={c.source}
                      className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[10px] font-medium text-[#2563EB]"
                    >
                      [{c.index}] {c.agreement.toUpperCase()} · {c.source.split("—")[0].trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/** Render **bold** markdown inline. */
function renderLine(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}
