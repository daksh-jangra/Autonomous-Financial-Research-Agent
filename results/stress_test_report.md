# Stress Test Report — Challenge 8 (50% Tool Failure)

Challenge 8 produces a full NVIDIA research report while the financial-data and SEC-filing tools fail at a simulated 50% rate. This exercises the circuit breakers and fallback chains under sustained degradation.

## Result

- **Simulated failures injected:** 3
- **Degraded steps (resolved via fallback):** 2 of 7
- **Degradation resilience (AB-2):** 71.4%
- **Report still produced:** yes (745 words, 7 citations)
- **Completed within tool budget:** 7/20 calls

## Fallback behaviour observed

When `financial_data_api` and `sec_filing_search` fail, the FallbackManager cascades to the configured alternatives (web_search, vector_db_search). Each degraded step is recorded and surfaced in the report's **Data Gaps & Degradation** section, so the output is transparent about which figures could not be retrieved rather than fabricating them.

## Comparison vs. healthy run

Challenges 1-7 ran with a 0% failure rate and recorded 0 degraded calls. Challenge 8 is the only run with injected failures, isolating the degradation behaviour for analysis.
