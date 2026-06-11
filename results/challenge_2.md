# Investment Research Report

**Query:** Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results to consensus estimates and identify key takeaways from the earnings call.

**Intent classified as:** `earnings` | **Tickers:** AAPL

---

## Company Overview

**Apple Inc.** (AAPL)

- **Sector:** Technology
- **Industry:** Consumer Electronics
- **Market capitalisation:** $4.26T
- **Website:** https://www.apple.com
- **Key executives:**
    - Mr. Timothy D. Cook — CEO & Director
    - Mr. Kevan  Parekh — Senior VP & CFO
    - Mr. Sabih  Khan — Senior VP & Chief Operating Officer
    - Ms. Deirdre  O'Brien — Senior Vice President of Retail & People
    - Ms. Katherine L. Adams — Senior VP of Government Affairs & Secretary

**Business overview:**

Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple Vision Pro, Apple TV, Apple Watch, Beats products, and HomePod, as well as Apple branded and third-party accessories. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts, as well as advertising services include third-party licensing arrangements and its own advertising platforms. In addition, the company offers various subscription-based services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV, which offers exclusive original content and live sports; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers and resellers. The company was formerly known as Apple Computer, Inc. and changed its name to Apple Inc. in January 2007. Apple Inc. was founded in 1976 and is headquartered in Cupertino, California.

## Financial Analysis

| Line item | 2025-09-30 | 2024-09-30 |
|---|---|---|
| Total Revenue | $416.16B | $391.04B |
| Operating Revenue | $416.16B | $391.04B |
| Gross Profit | $195.20B | $180.68B |
| Operating Income | $133.05B | $123.22B |
| Net Income | $112.01B | $93.74B |
| Basic EPS | $7 | $6 |
| Diluted EPS | $7 | $6 |
| EBITDA | $144.75B | $134.66B |

_Source: AAPL annual income_statement (yfinance)._

**Computed growth (calculation_engine):**
- AAPL revenue growth (YoY): **6.43%**

## Market Sentiment & News

**Overall news sentiment:** Neutral (mean polarity +0.00)

Recent headlines analysed:

[Yahoo Finance] 'Magnificent 7' stocks have lost $2 trillion so far this month, driving the S&P 500 decline: Chart of the Day (Sentiment: 0.55)
[GuruFocus.com] Intel Stock Jumps After BofA Surprise Double Upgrade (Sentiment: 0.00)
[Motley Fool] Apple Just Delivered Bad News for OpenAI and Anthropic, but Alphabet Could Be a Winner (Sentiment: -0.70)
[Trefis] What Is Google Hiding Behind Its AI Silence? (Sentiment: -0.40)
[Bloomberg] DoorDash Built an AI Chatbot to Help With Orders, Reservations and Grocery Lists (Sentiment: 0.00)
[The Wall Street Journal] Retail Investors Are Selling Stocks to Raise Money for SpaceX (Sentiment: 0.00)
[Motley Fool] Wall Street Is Ignoring This Part of the Market. That's Why I'm Interested. (Sentiment: 0.25)
[Stocktwits] AMD, ARM, INTC, NVDA Get A Fresh AI Tailwind - BofA Sees Agentic AI Expanding Server CPU Market To $170B (Sentiment: 0.30)

## Web Context

- [[MOCK] Search result for Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results to consensus estimates and identify key takeaways from the earnings call.](http://example.com/mock) — Configure TAVILY_API_KEY in .env to enable real search.

## Synthesis

### Financial Context
Financial data indicates ongoing trends. 
### Market Sentiment
Overall news sentiment is Neutral. 

### Raw Data Synthesis
- Data collected for financials
- Data collected for sentiment


## Fact Verification

- _Apple Inc. operates in the Technology sector._ → verified=True (confidence 0.85)

## Research Methodology

- **Reasoning loop:** Plan-and-Execute, 6-node LangGraph pipeline.
- **Synthesis mode:** deterministic data synthesis (no LLM key present).
- **Tools planned:** 5; **executed:** 5 (cap 20).
- **Live data sources:** yfinance (financials/profile/news), SEC EDGAR full-text search.
- **Constraint:** no figures are fabricated; unavailable data is labelled explicitly.


---

## Execution Trace

```json
{
  "query": "Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results to consensus estimates and identify key takeaways from the earnings call.",
  "intent": "earnings",
  "tickers": [
    "AAPL"
  ],
  "plan_length": 5,
  "tool_sequence": [
    {
      "tool": "company_profile",
      "source": "company_profile",
      "degraded": false
    },
    {
      "tool": "financial_data_api",
      "source": "financial_data_api",
      "degraded": false
    },
    {
      "tool": "earnings_transcript",
      "source": "earnings_transcript",
      "degraded": false
    },
    {
      "tool": "news_sentiment",
      "source": "news_sentiment",
      "degraded": false
    },
    {
      "tool": "web_search",
      "source": "web_search",
      "degraded": false
    }
  ],
  "iterations": 5,
  "total_tool_calls": 5,
  "useful_calls": 5,
  "degraded_calls": 0,
  "simulated_failures": 0,
  "memory_hits": 0,
  "llm_used": false,
  "tokens": 0,
  "duration_seconds": 2.09
}
```
