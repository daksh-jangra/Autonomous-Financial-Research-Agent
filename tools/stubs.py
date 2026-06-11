import json

def sec_filing_search(ticker: str, filing_type: str, year: int = None) -> str:
    return f"[MOCK] Returning {filing_type} filing for {ticker} from year {year or 'most recent'}."

def web_search(query: str, num_results: int = 10, date_range: str = None) -> list:
    return [{"url": f"http://example.com/mock_search_{i}", "title": f"Mock result {i} for {query}", "snippet": f"Mock snippet {i}"} for i in range(num_results)]

def earnings_transcript(ticker: str, quarter: str, year: int) -> str:
    return f"[MOCK] Transcript for {ticker} {quarter} {year}. Operator: Welcome to the earnings call. CEO: We had a great quarter."

def financial_data_api(ticker: str, statement_type: str, period: str, years: int) -> str:
    return json.dumps({
        "ticker": ticker,
        "statement_type": statement_type,
        "period": period,
        "data": {f"Year_{i}": {"revenue": 1000000 + i*10000} for i in range(years)}
    })

def news_sentiment(query: str, num_articles: int, lookback_days: int) -> dict:
    return {"sentiment_score": 0.8, "summary": f"[MOCK] Overall positive sentiment for {query} over last {lookback_days} days."}

def vector_db_search(query: str, top_k: int, filter: dict = None) -> list:
    return [{"chunk": f"[MOCK] relevant info for {query}", "score": 0.95}]

def vector_db_store(content: str, metadata: dict) -> str:
    return f"[MOCK] Stored content in DB with metadata {metadata}."

def company_profile(ticker: str) -> str:
    return json.dumps({
        "ticker": ticker,
        "name": f"{ticker} Corporation",
        "sector": "Technology",
        "market_cap": "1 Trillion",
        "description": f"[MOCK] Description for {ticker}."
    })

def peer_comparison(ticker: str, num_peers: int, metrics: list) -> dict:
    peers = [f"PEER{i}" for i in range(num_peers)]
    return {
        "target": ticker,
        "peers": peers,
        "comparison": {metric: {ticker: 10, **{peer: 9 for peer in peers}} for metric in metrics}
    }

def report_generator(template: str, sections: dict, sources: list) -> str:
    report = f"# [MOCK] Report using template {template}\n\n"
    for title, content in sections.items():
        report += f"## {title}\n{content}\n\n"
    report += "### Sources\n" + "\n".join([f"- {s}" for s in sources])
    return report

def fact_checker(claim: str, sources: list = None) -> dict:
    return {"verified": True, "claim": claim, "confidence": 0.99, "evidence": "[MOCK] Evidence found in sources."}

def calculation_engine(calculation_type: str, inputs: dict) -> dict:
    return {"calculation": calculation_type, "result": "[MOCK] 42.0", "steps": ["Mock step 1", "Mock step 2"]}
