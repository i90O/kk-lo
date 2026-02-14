"use client";

import { useAppStore } from "@/lib/store";
import { timeAgo } from "@/lib/format";
import LoadingSpinner from "@/components/shared/LoadingSpinner";
import { ExternalLink } from "lucide-react";

export default function NewsFeed() {
  const data = useAppStore((s) => s.newsData);
  const loading = useAppStore((s) => s.loading.news);

  if (loading && !data) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">News</div>
        <div className="flex items-center justify-center py-4"><LoadingSpinner size="sm" /></div>
      </div>
    );
  }
  if (!data || data.articles.length === 0) {
    return (
      <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
        <div className="text-sm font-medium text-[var(--text-secondary)] mb-3">News</div>
        <div className="text-xs text-[var(--text-muted)]">No recent news</div>
      </div>
    );
  }

  return (
    <div className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-medium text-[var(--text-secondary)]">News</div>
        <span className="text-[10px] text-[var(--text-muted)]">{data.news_count} articles</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        {data.articles.slice(0, 9).map((a, i) => (
          <a
            key={i}
            href={a.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-2.5 rounded-lg border border-[var(--border)] hover:border-[var(--border-hover)] hover:bg-[var(--bg-tertiary)]/30 transition group"
          >
            <div className="text-xs text-[var(--text-primary)] leading-snug line-clamp-2 group-hover:text-white">{a.title}</div>
            <div className="flex items-center justify-between mt-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-[var(--text-muted)]">{a.source}</span>
                <span className="text-[10px] text-[var(--text-muted)] opacity-60">{timeAgo(a.published)}</span>
              </div>
              <ExternalLink size={10} className="text-[var(--text-muted)] opacity-0 group-hover:opacity-100 transition" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
