# Investment Research Report

**Query:** Create a comprehensive profile of Microsoft Corporation including business overview, financial summary, key executives, and recent developments.

**Intent classified as:** `profile` | **Tickers:** MSFT

---

## Company Overview

**Microsoft Corporation** (MSFT)

- **Sector:** Technology
- **Industry:** Software - Infrastructure
- **Market capitalisation:** $2.90T
- **Website:** https://www.microsoft.com
- **Key executives:**
    - Mr. Satya  Nadella — Chairman & CEO
    - Mr. Bradford L. Smith LCA — President & Vice Chairman
    - Ms. Amy E. Hood — Executive VP & CFO
    - Mr. Takeshi  Numoto — Executive VP & Chief Marketing Officer
    - Mr. Judson B. Althoff — Executive VP & CEO of Commercial Business

**Business overview:**

Microsoft Corporation develops and supports software, services, devices, and solutions worldwide. The Productivity and Business Processes segment offers Microsoft 365 commercial, enterprise mobility + security, windows commercial, power BI, exchange, sharepoint, Microsoft teams, security and compliance, and copilot; Microsoft 365 commercial products, such as Windows commercial on-premises and office licensed services; Microsoft 365 consumer products and cloud services, including Microsoft 365 consumer subscriptions, office licensed on-premises, and other consumer services; LinkedIn; dynamics products and cloud services, such as dynamics 365, cloud-based applications, and on-premises ERP and CRM applications. Its Intelligent Cloud segment provides Server products and cloud services comprising Azure and other cloud services, GitHub, Nuance Healthcare, virtual desktop offerings, and other cloud services; server products, including SQL and windows server, visual studio and system center related client access licenses, and other on-premises offerings; enterprise and partner services, such as enterprise support and nuance professional services, industry solutions, Microsoft partner network, and learning experience. The Personal Computing segment provides windows and devices, such as Windows OEM licensing and devices and surface and PC accessories; gaming services and solutions, such as Xbox hardware, content, and services, first- and third-party content Xbox game pass, subscriptions, and cloud gaming, advertising, and other cloud services; search and news advertising services that includes Bing and Copilot, Microsoft News and Edge, and third-party affiliates. It sells its products through OEMs, distributors, and resellers; and online and retail stores. The company has a strategic collaboration with Mayo Clinic, Inc. for the development of a frontier AI model for healthcare. The company was founded in 1975 and is headquartered in Redmond, Washington.

## Financial Analysis

| Line item | 2025-06-30 | 2024-06-30 |
|---|---|---|
| Total Revenue | $281.72B | $245.12B |
| Operating Revenue | $281.72B | $245.12B |
| Gross Profit | $193.89B | $171.01B |
| Operating Income | $128.53B | $109.43B |
| Net Income | $101.83B | $88.14B |
| Basic EPS | $14 | $12 |
| Diluted EPS | $14 | $12 |
| EBITDA | $160.16B | $133.01B |

_Source: MSFT annual income_statement (yfinance)._

**Computed growth (calculation_engine):**
- MSFT revenue growth (YoY): **14.93%**

## Market Sentiment & News

**Overall news sentiment:** Neutral (mean polarity -0.00)

Recent headlines analysed:

[Yahoo Finance Video] Oracle stock sinking as its AI spending climbs, debt grows (Sentiment: 0.00)
[Yahoo Finance] 'Magnificent 7' stocks have lost $2 trillion so far this month, driving the S&P 500 decline: Chart of the Day (Sentiment: 0.55)
[Investing.com] Google spurned U.S. quantum fund over conditions that would slow R&D (Sentiment: -0.30)
[24/7 Wall St.] The Stock Market Isn’t Crashing. Investors Are Just Fleeing Technology Stocks. (Sentiment: 0.00)
[Trefis] What Is Google Hiding Behind Its AI Silence? (Sentiment: -0.40)
[Bloomberg] Amazon Says Its Data Centers Use 2.5 Billion Gallons of Water (Sentiment: 0.00)
[Trefis] Oracle Just Showed Wall Street the AI Boom, Then Handed It The Bill (Sentiment: 0.00)
[Proactive] Nasdaq semis stocks lead rebound rally despite Trump warning of new Iran strikes (Sentiment: 0.14)

## Web Context

- [[MOCK] Search result for Create a comprehensive profile of Microsoft Corporation including business overview, financial summary, key executives, and recent developments.](http://example.com/mock) — Configure TAVILY_API_KEY in .env to enable real search.

## Synthesis

### Financial Context
Financial data indicates ongoing trends. 
### Market Sentiment
Overall news sentiment is Neutral. 

### Raw Data Synthesis
- Data collected for financials
- Data collected for sentiment


## Fact Verification

- _Microsoft Corporation operates in the Technology sector._ → verified=True (confidence 0.85)

## Research Methodology

- **Reasoning loop:** Plan-and-Execute, 6-node LangGraph pipeline.
- **Synthesis mode:** deterministic data synthesis (no LLM key present).
- **Tools planned:** 4; **executed:** 4 (cap 20).
- **Live data sources:** yfinance (financials/profile/news), SEC EDGAR full-text search.
- **Constraint:** no figures are fabricated; unavailable data is labelled explicitly.


---

## Execution Trace

```json
{
  "query": "Create a comprehensive profile of Microsoft Corporation including business overview, financial summary, key executives, and recent developments.",
  "intent": "profile",
  "tickers": [
    "MSFT"
  ],
  "plan_length": 4,
  "iterations": 4,
  "total_tool_calls": 4,
  "useful_calls": 4,
  "degraded_calls": 0,
  "simulated_failures": 0,
  "memory_hits": 0,
  "llm_used": false,
  "tokens": 0,
  "duration_seconds": 11.02
}
```
