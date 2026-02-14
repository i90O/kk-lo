"""
News sentiment analysis tool using Polygon.io News API.
"""

from datetime import datetime
from langchain.tools import tool
from tools import polygon_client as _client


@tool
def analyze_news_sentiment(ticker: str, limit: int = 10) -> dict:
    """
    Fetch latest news for a ticker and provide sentiment context.

    Args:
        ticker: Stock symbol
        limit: Number of news articles (1-50)
    """
    news_items = []

    try:
        for item in _client.list_ticker_news(ticker=ticker, limit=limit):
            news_items.append({
                "title": item.title,
                "published": str(item.published_utc),
                "source": item.publisher.name if item.publisher else "Unknown",
                "url": item.article_url,
                "description": item.description[:200] if item.description else None,
            })
            if len(news_items) >= limit:
                break
    except Exception as e:
        return {"error": f"Polygon News API error: {e}", "ticker": ticker}

    return {
        "ticker": ticker,
        "source": "polygon",
        "news_count": len(news_items),
        "articles": news_items,
        "instruction": (
            "Based on these headlines and summaries, determine market sentiment "
            "(bullish/bearish/neutral) and flag key events that may impact "
            "options pricing (earnings, FDA, lawsuits, M&A, etc.)."
        ),
    }


if __name__ == "__main__":
    result = analyze_news_sentiment.invoke({"ticker": "TSLA", "limit": 5})
    print(f"Source: {result.get('source', 'unknown')}")
    print(f"News count: {result.get('news_count', 0)}")
    for a in result.get("articles", []):
        print(f"  - {a['title'][:80]}")
