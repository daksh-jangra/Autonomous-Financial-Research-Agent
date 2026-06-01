# Agent Architecture Specification
**Project:** Autonomous Financial Research Agent (ARA-1)
**Author:** Dax
**Date:** June 2026

---

## 1. Executive Summary
This document specifies the cognitive architecture, memory systems, and tool integration strategy for the Autonomous Financial Research Agent (ARA-1) developed for QuantumEdge Research. The agent is designed to autonomously replicate the workflow of a junior financial analyst by receiving queries, formulating comprehensive research plans, gathering data from 10+ financial tools, synthesizing conflicting information, and generating professional-grade investment research reports.

## 2. Primary Agent Pattern: Plan-and-Execute
### 2.1 Pattern Selection
The architecture utilizes a **Plan-and-Execute** cognitive pattern (orchestrated via LangGraph), augmented with an iterative revision loop. 

### 2.2 Rationale
While a naive ReAct loop is sufficient for simple, single-tool queries, complex financial research (e.g., cross-company sector analysis or deep-dive risk assessments) requires deliberate planning to avoid context window overflow, redundant API calls, and circular reasoning. 
1. **Efficiency:** By formulating a complete plan upfront, the agent can dispatch independent data-gathering tasks in parallel (e.g., fetching 10-K filings while simultaneously pulling historical pricing).
2. **Auditability:** The Plan-and-Execute model produces a discrete, reviewable plan that can be logged in the agent's episodic memory, aligning with the "Radical Transparency" principle observed in quantitative funds.
3. **Resilience:** The Executor node operates systematically, tracking completed versus pending steps, which provides a robust state-machine framework for error recovery.

## 3. Cognitive Loop Design
The cognitive loop is structured as a directed graph using LangGraph.

### 3.1 Node 1: Query Analyzer & Disambiguator
- **Input:** Raw user query.
- **Function:** Classifies the query type (e.g., single-company profile vs. industry comparison) and detects ambiguity. It retrieves historical context from Short-Term Memory to resolve vague terms (e.g., resolving "the bank stress tests" based on temporal context).

### 3.2 Node 2: Planner
- **Function:** Given the disambiguated query, the Planner interacts with Episodic Memory to retrieve successful plans for similar past queries. It outputs a structured, numbered execution plan (e.g., Step 1: `company_profile`, Step 2: `sec_filing_search`, etc.).

### 3.3 Node 3: Executor (The Tool Dispatcher)
- **Function:** The Executor acts as a sub-graph. It takes the current step from the plan and dispatches the appropriate tool. 
- **Tool Selection:** The LLM is provided with the full Tool Registry schema and selects the best tool based on the required information.
- **Action/Observation:** Executes the tool (wrapped in a circuit breaker and retry logic) and appends the Observation to the Short-Term Memory context window.

### 3.4 Node 4: Synthesizer
- **Function:** Once all data gathering steps are complete, the Synthesizer processes the raw observations. It applies the **Source Reliability Hierarchy** (Tier 1 SEC Filings > Tier 2 Financial APIs > Tier 5 News) to resolve conflicting data points (e.g., discrepancies between reported revenue and news reports).

### 3.5 Node 5: Fact Verification
- **Function:** A secondary LLM pass that implements the Chain-of-Verification pattern. It isolates every numerical claim and entity in the draft synthesis and traces it back to the retrieved context.

### 3.6 Node 6: Report Generator
- **Function:** Formats the verified synthesis into a structured Markdown document matching the required output format (e.g., 15-page risk assessment, 5-page earnings brief).

## 4. Memory Architecture
The agent employs a three-layer memory system to overcome context limitations and accumulate intelligence over time.

### 4.1 Short-Term Memory (Working Context)
- **Implementation:** LangGraph `StateGraph` dictionary.
- **Management:** To prevent context overflow, a Progressive Summarization node compresses older tool outputs into dense summaries while preserving exact numerical data. Only the most recent and highly relevant raw observations are kept in the active prompt.

### 4.2 Long-Term Semantic Memory
- **Implementation:** Local ChromaDB instance with `OpenAI text-embedding-3-small` embeddings.
- **Function:** Acts as the agent's proprietary research archive. 
- **Chunking Strategy:** Financial documents are semantically chunked. SEC filings are chunked by section (e.g., MD&A, Risk Factors); Earnings Transcripts are chunked by speaker turns and Q&A pairs to preserve conversational context.
- **Retrieval:** Uses Hybrid Search (Vector + Metadata filtering) to ensure that queries for specific tickers only search within that ticker's namespace, reducing cross-company contamination.

### 4.3 Episodic Memory (Experience Memory)
- **Implementation:** A separate ChromaDB collection storing entire agent trajectories (Query -> Plan -> Tool Outcomes -> Final Score).
- **Function:** Enables the agent to learn from past mistakes. If a past strategy resulted in a high hallucination rate due to over-reliance on `web_search`, the Episodic Memory retrieval will bias the Planner toward structured `financial_data_api` calls for similar future queries.

## 5. Tool Registry
The agent integrates 10+ core tools, each defined by an OpenAI-compatible JSON schema.
1. **sec_edgar:** SEC filing retrieval.
2. **financial_data_api:** Structured financials (Income, Balance, Cash Flow).
3. **web_search:** General web and news search (Tavily).
4. **news_sentiment:** NLP analysis of recent news sentiment.
5. **earnings_transcript:** Retrieval of management commentary.
6. **company_profile:** Basic entity, sector, and cap data.
7. **peer_comparison:** Identifying industry competitors.
8. **calculator:** Deterministic mathematical operations (DCF, growth rates).
9. **fact_checker:** Cross-referencing claims.
10. **vector_db_search:** Querying long-term memory.
11. **vector_db_store:** Archiving new findings.
12. **report_gen:** Formatting output.

## 6. Multi-Source Synthesis Engine
The Synthesizer employs three core techniques:
1. **Narrative Threading:** Connects quantitative data (falling margins) with qualitative commentary (management discussing supply chain issues in transcripts).
2. **Quantitative Triangulation:** If `financial_data_api`, `sec_edgar`, and `web_search` return different revenue numbers, the engine applies the Source Reliability Hierarchy, prioritizing the audited SEC filing, while explicitly documenting the discrepancy in the final report.
3. **Sentiment-Fact Alignment:** Detects and highlights divergences (e.g., positive news sentiment vs. deteriorating free cash flow).

## 7. Error Handling & Graceful Degradation
To prevent catastrophic failures during complex 15-page research tasks, the architecture implements:
- **Exponential Backoff:** Configured on all external API requests (starting at 1s, max 5 retries, with jitter).
- **Fallback Chains:** If `financial_data_api` experiences an outage (HTTP 503), the agent automatically degrades to fetching the 10-Q via `sec_edgar` and attempting to extract the data natively.
- **Graceful Degradation:** If all fallback chains fail for a specific data point, the Report Generator explicitly flags the missing data (e.g., "[DATA UNAVAILABLE: Financial API Timeout]") rather than allowing the LLM to hallucinate a plausible number.

## 8. Evaluation Framework Integration
The architecture is inherently designed to be testable against the 20+ metrics specified by QuantumEdge Research.
- **Trace Logging:** Every node execution is logged locally. This enables the calculation of the `AB-1 Tool Efficiency` metric (useful calls / total calls) and `AB-2 Error Recovery Rate`.
- **Modularity:** The fact-verification node allows for direct measurement of `FA-1 Numerical Accuracy` by comparing the draft output with the verified output prior to final generation.
