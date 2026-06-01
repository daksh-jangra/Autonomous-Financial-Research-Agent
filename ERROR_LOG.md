# ERROR LOG

This document catalogs the 7 deliberate factual and logical errors embedded in the project specification document (Parts A through E), as required by the assessment guidelines.

### 1. Historical/Regulatory Timeline Error (Page 24)
**Location:** Section A7.3 Handling Ambiguous Queries
**Statement:** "Note: The first US bank stress tests under SCAP were conducted in 2007 following the Dodd-Frank Act."
**Correction:** The Supervisory Capital Assessment Program (SCAP) stress tests were conducted in **2009**, not 2007. Furthermore, the Dodd-Frank Act was passed in **2010**, so SCAP could not have followed it.

### 2. Financial Concept Error (Page 21)
**Location:** Section A6.2 Source Reliability Hierarchy
**Statement:** "Tier 1 (Highest Reliability): SEC filings (10-K, 10-Q) – legally mandated, audited..."
**Correction:** While 10-K filings contain audited financial statements, **10-Q filings are unaudited**. This is correctly noted later in the glossary (Page 70), making the Tier 1 description factually incorrect.

### 3. Regulatory Filing Error (Page 42)
**Location:** Section C4.2 Challenges Specific To Indian Market Research
**Statement:** "Filing format differences: Indian companies file annual returns using Form 20-F with the MCA..."
**Correction:** **Form 20-F** is a US SEC filing required for foreign private issuers trading on US exchanges. Indian companies file their annual returns and financial statements with the Ministry of Corporate Affairs (MCA) using forms such as **MGT-7** and **AOC-4**, not Form 20-F.

### 4. Mathematical/Logical Formula Error (Page 19)
**Location:** Category 5: Agent Behaviour (5 Metrics) - AB-4: Memory Utilization
**Statement:** "Note: This metric is calculated as memory_hits multiplied by total_api_calls."
**Correction:** To calculate a ratio or utilization rate, the formula should involve division, not multiplication. It should be calculated as `memory_hits / (memory_hits + total_api_calls)` or a similar division-based metric.

### 5. API Specification Error (Page 62)
**Location:** Section E2.2 Embedding Models
**Statement:** "OpenAI text-embedding-3-large: 1024 dimensions..."
**Correction:** OpenAI's `text-embedding-3-large` model outputs vectors with **3072 dimensions** by default, not 1024. (The `text-embedding-3-small` model outputs 1536 dimensions).

### 6. API Specification Error (Page 10)
**Location:** Section A2.4 Tool Schema Design Principles
**Statement:** "Each tool schema must follow the OpenAI function calling specification (which is also used by Anthropic's Claude tool use)... parameters (JSON Schema object defining input types, required fields, and defaults)."
**Correction:** Anthropic's Claude does **not** use the exact same schema structure as OpenAI. While OpenAI uses the `parameters` key for tool inputs, Anthropic's Claude specification requires the `input_schema` key instead. 

### 7. Platform/Service Tier Error (Page 63)
**Location:** Section E3.1 Openai
**Statement:** "API Key: Register at platform.openai.com. New accounts receive $5 in free credits. Rate Limits: GPT-4o: 500 RPM... on free tier."
**Correction:** OpenAI's Free Tier has much stricter limits (typically around 3 RPM for advanced models), and 500 RPM corresponds to paid Tier 1. Additionally, OpenAI discontinued the automatic $5 free credit grant for new accounts.
