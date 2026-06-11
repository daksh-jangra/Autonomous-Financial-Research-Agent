import yfinance as yf
from textblob import TextBlob

def news_sentiment(query: str, num_articles: int, lookback_days: int) -> dict:
    """Analyzes sentiment of recent news articles about a company using yfinance and TextBlob."""
    try:
        stock = yf.Ticker(query)
        news = stock.news
        
        if not news:
            return {"sentiment_score": 0.0, "summary": f"No news found for {query}."}
            
        articles = news[:num_articles]
        total_sentiment = 0.0
        summaries = []
        
        for article in articles:
            # yfinance moved the article fields under a nested "content" object;
            # fall back to the legacy flat schema for older versions.
            content = article.get("content", article)
            title = content.get("title", "") or ""
            provider = content.get("provider") or {}
            publisher = provider.get("displayName") if isinstance(provider, dict) else ""
            publisher = publisher or content.get("publisher", "") or article.get("publisher", "")

            if not title:
                continue

            # Simple sentiment analysis on the title
            blob = TextBlob(title)
            sentiment = blob.sentiment.polarity
            total_sentiment += sentiment
            
            summaries.append(f"[{publisher}] {title} (Sentiment: {sentiment:.2f})")
            
        avg_sentiment = total_sentiment / len(summaries) if summaries else 0.0
        
        return {
            "sentiment_score": avg_sentiment,
            "summary": "\n".join(summaries),
            "overall_sentiment": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral"
        }
    except Exception as e:
        return {"sentiment_score": 0.0, "summary": f"Error analyzing news: {str(e)}"}
