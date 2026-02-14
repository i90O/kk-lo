"use client";

import type { ChatMessage } from "@/lib/types";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

function formatMarkdown(text: string): string {
  // NOTE: Content comes from our own AI backend, not user input.
  // In production, consider adding DOMPurify for defense-in-depth.
  let html = text
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="chat-code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="chat-inline-code">$1</code>')
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^### (.+)$/gm, '<h4 class="text-sm font-semibold text-[var(--text-primary)] mt-3 mb-1">$1</h4>')
    .replace(/^## (.+)$/gm, '<h3 class="text-sm font-bold text-[var(--text-primary)] mt-3 mb-1">$1</h3>')
    .replace(/^# (.+)$/gm, '<h2 class="text-base font-bold text-white mt-4 mb-2">$1</h2>')
    .replace(/^[-\u2022] (.+)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li class="ml-4 list-decimal">$1</li>')
    .replace(/^---$/gm, '<hr class="border-[var(--border)] my-3" />')
    .replace(/\n/g, "<br />");
  return html;
}

export default function ChatMessageBubble({ message }: { message: ChatMessage }) {
  if (message.loading) {
    return (
      <div className="flex gap-3 py-4 px-4 animate-fade-in">
        <div className="w-7 h-7 rounded-full bg-[var(--accent)]/20 border border-[var(--accent)]/30 flex items-center justify-center flex-shrink-0">
          <span className="text-[10px] font-bold text-[var(--accent)]">AI</span>
        </div>
        <div className="flex items-center gap-2">
          <LoadingSpinner size="sm" />
          <span className="text-sm text-[var(--text-muted)] animate-pulse">Thinking...</span>
        </div>
      </div>
    );
  }

  if (message.role === "user") {
    return (
      <div className="flex gap-3 py-3 px-4 animate-fade-in">
        <div className="w-7 h-7 rounded-full bg-[var(--bg-tertiary)] border border-[var(--border)] flex items-center justify-center flex-shrink-0">
          <span className="text-[10px] font-bold text-[var(--text-secondary)]">U</span>
        </div>
        <div className="flex-1">
          <div className="text-[10px] text-[var(--text-muted)] mb-1">You</div>
          <div className="text-sm text-[var(--text-primary)]">{message.content}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3 py-3 px-4 bg-[var(--bg-secondary)] rounded-lg animate-fade-in">
      <div className="w-7 h-7 rounded-full bg-[var(--accent)]/20 border border-[var(--accent)]/30 flex items-center justify-center flex-shrink-0">
        <span className="text-[10px] font-bold text-[var(--accent)]">AI</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] text-[var(--text-muted)] mb-1">OptionsAgent</div>
        <div
          className="text-sm text-[var(--text-secondary)] leading-relaxed chat-content"
          dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
        />
      </div>
    </div>
  );
}
