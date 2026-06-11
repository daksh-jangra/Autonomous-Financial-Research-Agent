# Final Evaluation Report — Autonomous Financial Research Agent (ARA-1)

**Author:** Dax · **Date:** June 2026

This is the consolidated final writeup for Project 1A. It summarises the
architecture as built, the evaluation results across all 8 validation
challenges, and an honest statement of limitations.

---

## 1. What was built

ARA-1 is an autonomous financial research agent implementing a **6-node
Plan-and-Execute** loop on LangGraph:

```
Query Analyzer → Planner → Executor (loop) → Synthesizer → Fact Verifier → Report Generator
```

- **Tool registry:** 12 tools (exceeds the 10 minimum), JSON-schema validated.
- **3-layer memory:** short-term graph state, long-term semantic (ChromaDB),
  episodic trajectory log.
- **Multi-source synthesis** with a source-reliability hierarchy
  (SEC > financial APIs > news) for conflict resolution.
- **Resilience:** circuit breakers + multi-step fallback chains on every tool.
- **LLM-optional:** with an API key the planner/synthesizer use an LLM for
  reasoning and prose; without one, a deterministic planner derives concrete
  tool calls from query intent and a synthesizer assembles live data
  (yfinance, SEC EDGAR) into structured, sourced sections. **No figure is
  fabricated**; unavailable data is labelled.

## 2. Challenge results

All 8 challenges were executed and saved to `results/challenge_1..8.md`, each
with a full execution trace. Metrics were computed from the real traces by
`evaluation/generate_evaluation.py`.

| Metric | Result |
|--------|--------|
| Challenges completed | 8 / 8 |
| Mean tool efficiency (AB-1) | 96.4% |
| Mean degradation resilience (AB-2) | 96.4% |
| Mean report completeness (AB-3) | 100% |
| Total tool calls | 41 (all within the 20/challenge budget) |
| Total source citations | 55 |

Highlights:
- **Challenge 7 (memory):** recalled 8 prior company records from the vector
  store and synthesised cross-company themes — the long-term memory works
  end-to-end across challenges.
- **Challenge 8 (degradation):** under a 50% simulated failure rate on the
  financial-data and SEC tools, 3 failures were injected and resolved via
  fallback chains; a complete report was still produced, with the gaps
  transparently disclosed.

See `results/evaluation_report.md`, `results/stress_test_report.md`, and
`results/token_usage_analysis.md` for the detail, and `docs/Trace_Gallery.md`
for the per-challenge tool sequences.

## 3. Limitations (stated honestly)

1. **No LLM key in this run.** Reports are well-structured data briefs rather
   than flowing analyst prose. The pipeline auto-upgrades to LLM narrative when
   `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` is set — no code change required.
2. **LLM-as-a-judge metrics not run.** Insight density, logical flow,
   executive-summary quality, and hallucination rate require an LLM; they are
   reported as `unavailable`, not fabricated.
3. **Some tools are key-gated.** `web_search` (Tavily), `earnings_transcript`
   and `peer_comparison` (FMP) return labelled mock fallbacks without keys.
   This is surfaced in each report's "Data Gaps & Degradation" section.
4. **Benchmarks are machine-drafted.** The gold-standard files in
   `evaluation/benchmarks/` are factual baselines from live data, not
   independent human references.

## 4. How to reproduce

```bash
python -m venv venv && ./venv/bin/pip install -e .
./venv/bin/python run_all_challenges.py            # writes results/challenge_1..8.md
./venv/bin/python -m evaluation.generate_evaluation # writes eval + trace gallery
./venv/bin/pytest -q                                # 16 tests
```

To enable LLM narrative + qualitative judging, add a key to `.env` and re-run.
