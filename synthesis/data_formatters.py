"""Turn raw live-tool output into human-readable, sourced report sections.

These functions are the no-LLM synthesis path: every number they emit is parsed
directly from a real tool response (yfinance, SEC EDGAR, TextBlob sentiment), so
nothing is fabricated. When an LLM is wired in it can replace or augment these.
"""
import json

# Financial-statement line items worth surfacing, in display order.
_KEY_LINE_ITEMS = [
    "Total Revenue",
    "Operating Revenue",
    "Gross Profit",
    "Operating Income",
    "Net Income",
    "Basic EPS",
    "Diluted EPS",
    "EBITDA",
    "Total Assets",
    "Total Debt",
    "Cash And Cash Equivalents",
]


def _fmt_money(v):
    """Format a raw number as a human-readable currency magnitude."""
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    a = abs(v)
    if a >= 1e12:
        return f"${v/1e12:.2f}T"
    if a >= 1e9:
        return f"${v/1e9:.2f}B"
    if a >= 1e6:
        return f"${v/1e6:.2f}M"
    return f"${v:,.0f}"


def format_profile(raw: str) -> str:
    """Company overview section from company_profile JSON."""
    try:
        d = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return f"_Company profile unavailable: {str(raw)[:200]}_"
    if "name" not in d:
        return f"_Company profile unavailable: {str(raw)[:200]}_"

    lines = [
        f"**{d.get('name')}** ({d.get('ticker')})",
        "",
        f"- **Sector:** {d.get('sector', 'Unknown')}",
        f"- **Industry:** {d.get('industry', 'Unknown')}",
        f"- **Market capitalisation:** {_fmt_money(d.get('market_cap'))}",
        f"- **Website:** {d.get('website', 'Unknown')}",
    ]
    execs = d.get("executives") or []
    if execs:
        lines.append("- **Key executives:**")
        for e in execs:
            if e.get("name"):
                lines.append(f"    - {e.get('name')} — {e.get('title', 'N/A')}")
    desc = d.get("description")
    if desc and desc != "No description available.":
        lines += ["", "**Business overview:**", "", desc]
    return "\n".join(lines)


def format_financials(raw: str) -> str:
    """Financial-analysis section from financial_data_api JSON (multi-period)."""
    try:
        d = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return f"_Financial data unavailable: {str(raw)[:200]}_"
    data = d.get("data")
    if not isinstance(data, dict) or not data:
        return f"_Financial data unavailable: {str(raw)[:200]}_"

    periods = list(data.keys())  # e.g. ["2025-06-30", "2024-06-30"]
    header = "| Line item | " + " | ".join(periods) + " |"
    sep = "|" + "---|" * (len(periods) + 1)
    rows = [header, sep]

    for item in _KEY_LINE_ITEMS:
        cells = []
        present = False
        for p in periods:
            val = data[p].get(item)
            if val is not None:
                present = True
                cells.append(_fmt_money(val))
            else:
                cells.append("—")
        if present:
            rows.append(f"| {item} | " + " | ".join(cells) + " |")

    note = f"\n\n_Source: {d.get('ticker')} {d.get('period')} {d.get('statement_type')} (yfinance)._"
    if len(rows) == 2:
        return f"_No standard line items parsed for {d.get('ticker')}._" + note
    return "\n".join(rows) + note


def revenue_growth(raw: str):
    """Extract (current, previous) Total Revenue for a growth calc; None if absent."""
    try:
        d = json.loads(raw)
        data = d.get("data", {})
        periods = list(data.keys())
        if len(periods) < 2:
            return None
        cur = data[periods[0]].get("Total Revenue") or data[periods[0]].get("Operating Revenue")
        prev = data[periods[1]].get("Total Revenue") or data[periods[1]].get("Operating Revenue")
        if cur is None or prev is None:
            return None
        return float(cur), float(prev)
    except (json.JSONDecodeError, TypeError, AttributeError):
        return None


def format_sentiment(obs) -> str:
    """Market-sentiment section from news_sentiment dict."""
    if not isinstance(obs, dict):
        return f"_Sentiment data unavailable: {str(obs)[:200]}_"
    overall = obs.get("overall_sentiment", "Neutral")
    score = obs.get("sentiment_score", 0.0)
    summary = obs.get("summary", "")
    lines = [
        f"**Overall news sentiment:** {overall} (mean polarity {score:+.2f})",
        "",
        "Recent headlines analysed:",
        "",
    ]
    if summary:
        lines.append(summary)
    else:
        lines.append("_No recent headlines retrieved._")
    return "\n".join(lines)


def format_sec(obs) -> str:
    """SEC-filing reference section."""
    s = str(obs)
    if s.startswith("Error") or s.startswith("No ") or "[DATA UNAVAILABLE]" in s:
        return f"_SEC filing lookup degraded: {s[:200]}_"
    return s


def format_web(obs) -> str:
    """Web-search section (list of result dicts)."""
    if not isinstance(obs, list):
        return f"_Web search unavailable: {str(obs)[:150]}_"
    lines = []
    for r in obs:
        if "error" in r:
            return f"_Web search degraded: {r['error']}_"
        lines.append(f"- [{r.get('title', 'result')}]({r.get('url', '')}) — {r.get('snippet', '')[:160]}")
    return "\n".join(lines) if lines else "_No web results._"
