# Optimization Log — ARA-1

Chronological log of issues found during integration/evaluation and the changes
made in response. Each entry notes the problem, the fix, and the effect on the
evaluation metrics.

## 1. Broken virtual environment (blocker)
- **Problem:** the project directory was moved, leaving `venv/` pointing at a
  stale interpreter path; `pytest` failed with a bad-interpreter error and the
  suite could not run at all.
- **Fix:** rebuilt the venv, reinstalled `requirements.txt`, and added an
  editable install (`pip install -e .`) so the local packages resolve.
- **Effect:** test suite runnable again (now 16 passing).

## 2. SEC EDGAR tool always failed (correctness)
- **Problem:** `tools/sec_edgar.py` issued a `POST` with a JSON body keyed on
  `keys` to the EFTS full-text endpoint, which requires a `GET` with the query
  in `q`. Every call returned an HTTP error, exhausted 5 retries, and surfaced
  as a caught error string — never real data.
- **Fix:** switched to `GET` with `params={"q": ticker, "forms": filing_type, ...}`.
- **Effect:** live SEC filing references now retrieved (verified against Apple
  10-K). Improves source grounding (AB-5) on the risk/contradiction/full-report
  challenges.

## 3. Agent pipeline not wired (correctness)
- **Problem:** the compiled graph was a 3-node mock skeleton; the synthesis
  engine, query analyzer, fact checker, report generator, and memory layer
  existed but were never called. `run()` returned a `MOCK DRAFT REPORT`.
- **Fix:** rewrote `agent/core.py` as the spec's 6-node Plan-and-Execute graph
  and added a deterministic, LLM-optional planner + synthesizer driven by live
  data. Added `agent/ticker_resolver.py` and `synthesis/data_formatters.py`.
- **Effect:** all 8 challenges now produce real, sourced reports.
  Report completeness (AB-3) rose to 100% mean.

## 4. yfinance news schema change (correctness)
- **Problem:** `news_sentiment` read `article["title"]`, but yfinance moved the
  fields under a nested `content` object; sentiment ran on empty strings and
  every headline scored 0.00.
- **Fix:** read `article["content"]["title"]` with a fallback to the legacy
  flat schema; skip items with no title; average over scored items only.
- **Effect:** real headlines + publishers now analysed; sentiment is meaningful.

## 5. Earnings query misclassified (precision)
- **Problem:** "Analyze Apple's earnings. **Compare** actual results to
  consensus…" matched the `comparison` intent before `earnings` because the
  classifier checked "compare" first.
- **Fix:** reordered `classify_intent` so `earnings` outranks an incidental
  "compare".
- **Effect:** Challenge 2 now correctly plans an earnings workflow.

## 6. Memory recall not surfaced (completeness)
- **Problem:** Challenge 7 retrieved prior research from the vector store, but
  `generate_report` had no handler for `vector_db_search`, so the recalled
  records never appeared in the report.
- **Fix:** added a "Prior Research Recalled (Long-Term Memory)" section and a
  cross-company thematic synthesis path for the `sector_memory` intent.
- **Effect:** Challenge 7 now shows the 8 recalled company records it reasons over.

## 7. Ambiguous query lacked documented assumptions (completeness)
- **Problem:** "What's happening with the banks?" resolved to JPM/BAC/USB but
  did not document that interpretation, so the "Query Interpretation &
  Assumptions" section was missing (AB-3 = 66.7% for Challenge 6).
- **Fix:** when sector proxies are substituted for a vague query, record the
  interpretation as an explicit assumption.
- **Effect:** Challenge 6 completeness rose to 100%; mean AB-3 reached 100%.

## Standing optimization opportunities (not yet done)
- **LLM narrative:** wire `ANTHROPIC_API_KEY` to replace deterministic synthesis
  with analyst-grade prose and enable the LLM-as-a-judge metrics.
- **Parallel execution:** independent data-gathering steps are currently
  sequential; they could be dispatched concurrently to cut latency.
- **Tavily / FMP keys:** add keys to upgrade `web_search`, `earnings_transcript`,
  and `peer_comparison` from labelled mock fallbacks to live data.
