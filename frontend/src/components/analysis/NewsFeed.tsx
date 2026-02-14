"use client";

import { useAppStore } from "@/lib/store";
import { timeAgo } from "@/lib/format";
import LoadingSpinner from "@/components/shared/LoadingSpinner";

export default function NewsFeed() {
  const data = useAppStore((s) => s.newsData);
  const loading = useAppStore((s) => s.loading.news);

  if (loading && !data) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm font-semibold text-gray-400 mb-3">News</div>
        <div className="flex items-center justify-center py-4"><LoadingSpinner size="sm" /></div>
      </div>
    );
  }
  if (!data || data.articles.length === 0) {
    return (
      <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
        <div className="text-sm font-semibold text-gray-400 mb-3">News</div>
        <div className="text-xs text-gray-600">No recent news</div>
      </div>
    );
  }

  return (
    <div className="bg-[#111] border border-gray-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm font-semibold text-gray-400">News</div>
        <span className="text-[10px] text-gray-600">{data.news_count} articles</span>
      </div>
      <div className="space-y-2">
        {data.articles.slice(0, 8).map((a, i) => (
          <a
            key={i}
            href={a.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block py-2 border-b border-gray-800/50 last:border-0 hover:bg-gray-800/30 -mx-2 px-2 rounded transition"
          >
            <div className="text-xs text-gray-200 leading-snug line-clamp-2">{a.title}</div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[10px] text-gray-500">{a.source}</span>
              <span className="text-[10px] text-gray-600">{timeAgo(a.published)}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
