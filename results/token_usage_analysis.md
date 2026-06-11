# Token Usage & Latency Analysis

This run executed with **no LLM key**, so the planner and synthesizer used the deterministic live-data path. LLM token consumption is therefore **0** for every challenge. The figures below report tool-call volume and wall-clock latency, which are the real cost drivers in this configuration.

| # | Intent | Tool calls | Degraded | Sim. failures | LLM tokens | Time (s) |
|---|--------|-----------|----------|---------------|------------|----------|
| 1 | profile | 4 | 0 | 0 | 0 | 9.91 |
| 2 | earnings | 5 | 0 | 0 | 0 | 2.09 |
| 3 | risk | 5 | 0 | 0 | 0 | 3.46 |
| 4 | comparison | 7 | 0 | 0 | 0 | 4.31 |
| 5 | contradiction | 5 | 0 | 0 | 0 | 2.13 |
| 6 | ambiguous | 6 | 0 | 0 | 0 | 2.77 |
| 7 | sector_memory | 2 | 0 | 0 | 0 | 0.03 |
| 8 | full_report | 7 | 2 | 3 | 0 | 1.8 |
| **Total** | — | **41** | — | — | **0** | **26.5** |

## Projected cost with an LLM

If narrative synthesis were enabled, each challenge would add roughly one planner call + one synthesizer call. At Claude Opus pricing and an estimated ~4-8K input / ~1-2K output tokens per challenge, projected cost is on the order of a few cents per challenge. Exact figures require an instrumented LLM run; this is an estimate, explicitly labelled as such.

## Observations

- The first challenge carries a one-time ~10s cost: loading the local sentence-transformers embedding model for the vector store.
- Challenge 7 (memory recall) is near-instant (0.03s): it reads from the vector store rather than hitting external APIs.
- Tool-call volume stays well under the 20-call budget for every challenge.
