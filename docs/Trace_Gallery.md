# Agent Trace Gallery

Real execution traces from the 8 validation challenges, generated from `results/run_summary.json`. Each trace shows the tools the agent actually invoked, in order, and whether any step was degraded / served by a fallback. These are produced by the deterministic (no-LLM) live-data pipeline.

## Challenge 1 — intent `profile`

**Query:** Create a comprehensive profile of Microsoft Corporation including business overview, financial summary, key executives, and recent developments.

**Tickers resolved:** MSFT  
**Tool calls:** 4/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 9.91s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `news_sentiment`
4. `web_search`

## Challenge 2 — intent `earnings`

**Query:** Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results to consensus estimates and identify key takeaways from the earnings call.

**Tickers resolved:** AAPL  
**Tool calls:** 5/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 2.09s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `earnings_transcript`
4. `news_sentiment`
5. `web_search`

## Challenge 3 — intent `risk`

**Query:** Produce a comprehensive risk assessment for Tesla Inc. covering financial risks, operational risks, regulatory risks, and competitive risks.

**Tickers resolved:** TSLA  
**Tool calls:** 5/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 3.46s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `sec_filing_search`
4. `news_sentiment`
5. `web_search`

## Challenge 4 — intent `comparison`

**Query:** Compare the cloud computing divisions of Amazon (AWS), Microsoft (Azure), and Google (GCP). Analyze revenue growth, market share, margins, and competitive advantages.

**Tickers resolved:** MSFT, AMZN, GOOGL  
**Tool calls:** 7/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 4.31s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `company_profile`
4. `financial_data_api`
5. `company_profile`
6. `financial_data_api`
7. `peer_comparison`

## Challenge 5 — intent `contradiction`

**Query:** Research Palantir Technologies. Note: Recent news reports suggest the company is struggling, but their financial statements show strong growth. Investigate and explain the apparent contradiction.

**Tickers resolved:** PLTR  
**Tool calls:** 5/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 2.13s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `sec_filing_search`
4. `news_sentiment`
5. `web_search`

## Challenge 6 — intent `ambiguous`

**Query:** What's happening with the banks?

**Tickers resolved:** JPM, BAC, USB  
**Tool calls:** 6/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 0 | **Time:** 2.77s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `news_sentiment`
4. `news_sentiment`
5. `news_sentiment`
6. `web_search`

## Challenge 7 — intent `sector_memory`

**Query:** Based on the companies you've already researched, what themes emerge across the technology sector? Identify cross-cutting risks and opportunities.

**Tickers resolved:** none  
**Tool calls:** 2/20 | **Degraded:** 0 | **Simulated failures:** 0 | **Memory hits:** 1 | **Time:** 0.03s

**Executed tool sequence:**

1. `vector_db_search`
2. `web_search`

## Challenge 8 — intent `full_report`

**Query:** Produce a complete investment research report on NVIDIA Corporation. Note: The financial data API and SEC filing search tools are currently experiencing intermittent failures (simulate 50% failure rate).

**Tickers resolved:** NVDA  
**Tool calls:** 7/20 | **Degraded:** 2 | **Simulated failures:** 3 | **Memory hits:** 0 | **Time:** 1.8s

**Executed tool sequence:**

1. `company_profile`
2. `financial_data_api`
3. `sec_filing_search`  →  ⚠️ degraded, served by `web_search`
4. `earnings_transcript`
5. `news_sentiment`
6. `web_search`
7. `financial_data_api`  →  ⚠️ degraded, served by `web_search`

