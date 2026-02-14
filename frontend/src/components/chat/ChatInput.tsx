"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

export default function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (message: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, [disabled]);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative">
      <div className="flex items-end gap-2 bg-[var(--bg-secondary)] border border-[var(--border)] rounded-xl p-2 focus-within:border-[var(--accent)]/50 transition">
        <textarea
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "Waiting for response..." : "Ask about options, strategies, or market analysis..."}
          disabled={disabled}
          rows={1}
          className="flex-1 bg-transparent text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] outline-none resize-none max-h-32 py-2 px-2"
          style={{ minHeight: "36px" }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="p-2 rounded-lg bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] disabled:bg-[var(--bg-tertiary)] disabled:text-[var(--text-muted)] transition flex-shrink-0"
        >
          <Send size={16} />
        </button>
      </div>
      <div className="text-[10px] text-[var(--text-muted)] mt-1.5 px-2 opacity-60">
        Enter to send &bull; Shift+Enter for new line
      </div>
    </div>
  );
}
