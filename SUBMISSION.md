# Project 1A Submission — Autonomous Financial Research Agent (ARA-1)

**Candidate:** Daksh Jangra
**Email:** daksh.jangraxzi@gmail.com
**Project:** 1A — Autonomous Financial Research Agent with Multi-Source Synthesis

## Links
- **GitHub repository:** https://github.com/daksh-jangra/Autonomous-Financial-Research-Agent
- **Loom demo (Challenge 4, end-to-end):** <PASTE YOUR LOOM LINK HERE>

## What's included in this submission
- Full source code (`agent/`, `tools/`, `memory/`, `synthesis/`, `evaluation/`)
- All 8 challenge outputs (`results/challenge_1..8.md`)
- Evaluation deliverables (`results/evaluation_report.md`, `stress_test_report.md`,
  `token_usage_analysis.md`)
- Documentation (`docs/architecture_specification_final.md`,
  `docs/evaluation_report_final.md`, `docs/optimization_log.md`,
  `docs/Trace_Gallery.md`)
- Test suite (`tests/`, 16 passing)
- Interactive CLI (`cli.py`) and local web UI (`web_app.py`)

## How to run
```bash
python -m venv venv && source venv/bin/activate
pip install -e .
python run_all_challenges.py             # regenerate the 8 challenge reports
python -m evaluation.generate_evaluation # regenerate evaluation reports
pytest -q                                # run the test suite
python cli.py                            # interactive prompt
python web_app.py                        # local web UI at http://127.0.0.1:8000
```

## Headline results (from real execution traces)
- 8/8 challenges completed
- Mean tool efficiency 96.4% · degradation resilience 96.4% · report completeness 100%
- 41 tool calls total (all within the 20/challenge budget) · 55 source citations

## Honest notes
- Runs in deterministic live-data mode (yfinance + SEC EDGAR) — no LLM key was used,
  so reports are structured data briefs rather than LLM prose. The pipeline
  auto-upgrades to LLM narrative if an API key is added (no code change).
- LLM-as-a-judge metrics are reported as `unavailable` (require an LLM), not fabricated.
- Web-search / earnings-transcript / peer tools degrade to labelled fallbacks without
  their API keys; gaps are disclosed in each report.
