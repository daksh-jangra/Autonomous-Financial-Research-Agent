"""Resolves company names to tickers and classifies query intent.

Without an LLM the agent still needs to turn a natural-language query into
concrete tool calls. This module provides the deterministic mapping layer:
company-name -> ticker, plus a coarse intent classifier that drives planning.
"""
import re

# Common company-name -> ticker map. Extend as needed; unknown names fall back
# to any explicit uppercase ticker found in the query.
COMPANY_TICKERS = {
    "microsoft": "MSFT",
    "apple": "AAPL",
    "tesla": "TSLA",
    "nvidia": "NVDA",
    "palantir": "PLTR",
    "amazon": "AMZN",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "meta": "META",
    "facebook": "META",
    "netflix": "NFLX",
    "u.s. bancorp": "USB",
    "us bancorp": "USB",
    "pnc": "PNC",
    "truist": "TFC",
    "jpmorgan": "JPM",
    "jp morgan": "JPM",
    "bank of america": "BAC",
    "wells fargo": "WFC",
}

# Words that look like tickers (all-caps) but are product/segment names, not equities.
_NOT_TICKERS = {"AWS", "GCP", "SEC", "API", "CEO", "CFO", "EPS", "DCF", "USD", "KRE", "GDP", "US"}

# Representative constituents used when a query references a sector with no
# specific company (e.g. "what's happening with the banks?").
SECTOR_PROXIES = {
    "bank": ["JPM", "BAC", "USB"],
    "regional bank": ["USB", "PNC", "TFC"],
}


def resolve_tickers(query: str) -> list:
    """Extracts a de-duplicated, order-preserving list of tickers from a query."""
    found = []
    lowered = query.lower()

    # 1. Match known company names (longest names first to avoid partial hits).
    for name in sorted(COMPANY_TICKERS, key=len, reverse=True):
        if name in lowered:
            t = COMPANY_TICKERS[name]
            if t not in found:
                found.append(t)

    # 2. Match explicit uppercase tickers like "USB", "PNC", "TFC" (1-5 chars).
    for m in re.findall(r"\b[A-Z]{1,5}\b", query):
        if m in _NOT_TICKERS or m in found:
            continue
        # Only accept as a ticker if it isn't an ordinary capitalised word.
        if m.isupper() and len(m) >= 2:
            found.append(m)

    return found


def classify_intent(query: str) -> str:
    """Maps a query to one of the agent's research intents.

    Returns one of: profile, earnings, risk, comparison, contradiction,
    ambiguous, sector_memory, full_report.
    """
    q = query.lower()

    if "already researched" in q or "themes emerge" in q or "cross-cutting" in q:
        return "sector_memory"
    if "complete investment research report" in q or "full research report" in q:
        return "full_report"
    if "contradiction" in q or "apparent contradiction" in q or (
        "struggling" in q and "growth" in q
    ):
        return "contradiction"
    # "earnings" is a stronger signal than an incidental "compare ... to consensus".
    if "earnings" in q:
        return "earnings"
    if "compare" in q or "comparison" in q or " vs " in q or "versus" in q:
        return "comparison"
    if "risk" in q:
        return "risk"
    if "profile" in q:
        return "profile"

    # Short, vague queries with no resolvable ticker are ambiguous.
    if len(query.split()) <= 6 and not resolve_tickers(query):
        return "ambiguous"

    return "profile"


def sector_proxy_tickers(query: str) -> list:
    """Best-effort representative tickers for a sector-level query."""
    q = query.lower()
    if "regional bank" in q or "kre" in q:
        return SECTOR_PROXIES["regional bank"]
    if "bank" in q:
        return SECTOR_PROXIES["bank"]
    return []
