# Evaluation Report — Autonomous Financial Research Agent (ARA-1)

Generated from real execution traces across all 8 validation challenges (`results/run_summary.json`). Deterministic metrics are computed directly from traces and report text. The LLM-as-a-judge metrics are marked **unavailable** because no LLM key was configured for this run — they are not fabricated.

## Per-Challenge Metrics

| # | Intent | Tool eff. (AB-1) | Resilience (AB-2) | Completeness (AB-3) | Mem. util. (AB-4) | Citations (AB-5) | Words | Time (s) |
|---|--------|------------------|-------------------|---------------------|-------------------|------------------|-------|----------|
| 1 | profile | 100.0% | 100.0% | 4/4 (100.0%) | 0.0 | 5 | 724 | 9.91 |
| 2 | earnings | 100.0% | 100.0% | 4/4 (100.0%) | 0.0 | 5 | 751 | 2.09 |
| 3 | risk | 100.0% | 100.0% | 5/5 (100.0%) | 0.0 | 7 | 743 | 3.46 |
| 4 | comparison | 100.0% | 100.0% | 4/4 (100.0%) | 0.0 | 8 | 1317 | 4.31 |
| 5 | contradiction | 100.0% | 100.0% | 5/5 (100.0%) | 0.0 | 7 | 744 | 2.13 |
| 6 | ambiguous | 100.0% | 100.0% | 3/3 (100.0%) | 0.0 | 5 | 921 | 2.77 |
| 7 | sector_memory | 100.0% | 100.0% | 3/3 (100.0%) | 0.333 | 11 | 687 | 0.03 |
| 8 | full_report | 71.4% | 71.4% | 4/4 (100.0%) | 0.0 | 7 | 745 | 1.8 |

## Aggregate

- **Challenges run:** 8/8
- **Mean tool efficiency (AB-1):** 96.4%
- **Mean degradation resilience (AB-2):** 96.4%
- **Mean report completeness (AB-3):** 100.0%
- **Total tool calls across all challenges:** 41
- **Total source citations:** 55

## Completeness Detail (missing sections)

- **Challenge 1** (profile): complete
- **Challenge 2** (earnings): complete
- **Challenge 3** (risk): complete
- **Challenge 4** (comparison): complete
- **Challenge 5** (contradiction): complete
- **Challenge 6** (ambiguous): complete
- **Challenge 7** (sector_memory): complete
- **Challenge 8** (full_report): complete

## LLM-as-a-Judge (qualitative) — status

These dimensions (insight density, logical flow, executive-summary quality, hallucination rate) require an LLM and were **not run**:

```json
{
  "status": "unavailable",
  "reason": "No LLM key configured; qualitative judging is disabled. Set ANTHROPIC_API_KEY/OPENAI_API_KEY to enable.",
  "dimensions": [
    "insight_density",
    "logical_flow",
    "executive_summary_quality",
    "hallucination_rate"
  ]
}
```

_To enable: set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) and re-run with `EvaluationMetrics(llm=<model>)`. The same pipeline then produces LLM-judged scores against the gold-standard benchmarks in `evaluation/benchmarks/`._
