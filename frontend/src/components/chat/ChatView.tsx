"use client";

import { useEffect, useRef } from "react";
import { useAppStore } from "@/lib/store";
import ChatMessageBubble from "./ChatMessage";
import ChatInput from "./ChatInput";

const SUGGESTIONS = [
  "Analyze TSLA options opportunities",
  "What's the best strategy for NVDA right now?",
  "Scan for unusual activity in SPY",
  "Compare bull put spread vs iron condor for AAPL",
  "What does high IV percentile mean for my strategy?",
  "Give me a low-risk options play for $5,000",
];

export default function ChatView() {
  const messages = useAppStore((s) => s.chatMessages);
  const chatLoading = useAppStore((s) => s.chatLoading);
  const sendChat = useAppStore((s) => s.sendChat);
  const clearChat = useAppStore((s) => s.clearChat);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[var(--bullish)] animate-pulse" />
            AI Assistant
          </h2>
          <p className="text-[11px] text-[var(--text-muted)]">
            Powered by Claude
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="px-3 py-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] border border-[var(--border)] rounded-lg hover:border-[var(--border-hover)] transition"
          >
            Clear
          </button>
        )}
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-1 pr-2">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full">
            <div className="text-center mb-8">
              <h3 className="text-xl font-semibold text-[var(--text-secondary)] mb-2">OptionsAgent AI</h3>
              <p className="text-sm text-[var(--text-muted)] max-w-md">
                Analyze stocks, recommend strategies, scan for unusual activity.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-2xl w-full">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  onClick={() => sendChat(s)}
                  className="text-left px-4 py-3 text-xs text-[var(--text-muted)] bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg hover:border-[var(--accent)]/50 hover:text-[var(--text-secondary)] transition group"
                >
                  <span className="text-[var(--accent)]/50 group-hover:text-[var(--accent)] mr-1">&rarr;</span>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessageBubble key={msg.id} message={msg} />
          ))
        )}
      </div>

      <div className="mt-3">
        <ChatInput onSend={sendChat} disabled={chatLoading} />
      </div>
    </div>
  );
}
