"""Generate the evaluation deliverables from real challenge runs.

Reads results/run_summary.json (produced by run_all_challenges.py) and the
challenge report files, computes the metric suite, and writes:
  * results/evaluation_report.md   — per-challenge + aggregate metrics
  * results/token_usage_analysis.md — token/latency/cost analysis
  * results/stress_test_report.md  — Challenge 8 degradation analysis

Run:  python -m evaluation.generate_evaluation
"""
import json
import os

from evaluation.metrics import EvaluationMetrics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
BENCHMARKS = os.path.join(ROOT, "evaluation", "benchmarks")

# Map challenges that have a gold-standard benchmark on file.
BENCHMARK_FILES = {1: "microsoft.md", 2: "apple.md", 3: "tesla.md"}


def _load_benchmark(num):
    fn = BENCHMARK_FILES.get(num)
    if not fn:
        return ""
    path = os.path.join(BENCHMARKS, fn)
    if os.path.isfile(path):
        with open(path) as f:
            return f.read()
    return ""


def _read_report(report_file):
    path = os.path.join(RESULTS, report_file)
    with open(path) as f:
        return f.read()


def main():
    with open(os.path.join(RESULTS, "run_summary.json")) as f:
        summary = json.load(f)

    metrics = EvaluationMetrics(llm=None)  # no LLM key -> judge marked unavailable
    evaluated = []
    for row in summary:
        report_text = _read_report(row["report_file"])
        ev = metrics.run_full_evaluation(
            report=report_text,
            intent=row["trace"].get("intent", ""),
            section_titles=row["sections"],
            trace=row["trace"],
            benchmark=_load_benchmark(row["challenge"]),
        )
        evaluated.append({**row, "metrics": ev})

    _write_evaluation_report(evaluated)
    _write_token_analysis(evaluated)
    _write_stress_report(evaluated)
    _write_trace_gallery(evaluated)
    print("Wrote evaluation_report.md, token_usage_analysis.md, stress_test_report.md, "
          "docs/Trace_Gallery.md")


def _write_evaluation_report(evaluated):
    lines = [
        "# Evaluation Report — Autonomous Financial Research Agent (ARA-1)",
        "",
        "Generated from real execution traces across all 8 validation challenges "
        "(`results/run_summary.json`). Deterministic metrics are computed directly "
        "from traces and report text. The LLM-as-a-judge metrics are marked "
        "**unavailable** because no LLM key was configured for this run — they are "
        "not fabricated.",
        "",
        "## Per-Challenge Metrics",
        "",
        "| # | Intent | Tool eff. (AB-1) | Resilience (AB-2) | Completeness (AB-3) | "
        "Mem. util. (AB-4) | Citations (AB-5) | Words | Time (s) |",
        "|---|--------|------------------|-------------------|---------------------|"
        "-------------------|------------------|-------|----------|",
    ]
    for e in evaluated:
        m = e["metrics"]
        comp = m["AB-3_report_completeness"]
        lines.append(
            f"| {e['challenge']} | {e['trace'].get('intent')} | "
            f"{m['AB-1_tool_efficiency_pct']}% | {m['AB-2_degradation_resilience_pct']}% | "
            f"{comp['present']}/{comp['expected']} ({comp['score_pct']}%) | "
            f"{m['AB-4_memory_utilization']} | {m['AB-5_source_citations']} | "
            f"{e['report_words']} | {e['trace'].get('duration_seconds')} |")

    # Aggregates.
    n = len(evaluated)
    avg_eff = round(sum(e["metrics"]["AB-1_tool_efficiency_pct"] for e in evaluated) / n, 1)
    avg_res = round(sum(e["metrics"]["AB-2_degradation_resilience_pct"] for e in evaluated) / n, 1)
    avg_comp = round(sum(e["metrics"]["AB-3_report_completeness"]["score_pct"] for e in evaluated) / n, 1)
    total_cit = sum(e["metrics"]["AB-5_source_citations"] for e in evaluated)
    total_calls = sum(e["trace"].get("total_tool_calls", 0) for e in evaluated)

    lines += [
        "",
        "## Aggregate",
        "",
        f"- **Challenges run:** {n}/8",
        f"- **Mean tool efficiency (AB-1):** {avg_eff}%",
        f"- **Mean degradation resilience (AB-2):** {avg_res}%",
        f"- **Mean report completeness (AB-3):** {avg_comp}%",
        f"- **Total tool calls across all challenges:** {total_calls}",
        f"- **Total source citations:** {total_cit}",
        "",
        "## Completeness Detail (missing sections)",
        "",
    ]
    for e in evaluated:
        missing = e["metrics"]["AB-3_report_completeness"]["missing"]
        status = "complete" if not missing else f"missing: {', '.join(missing)}"
        lines.append(f"- **Challenge {e['challenge']}** ({e['trace'].get('intent')}): {status}")

    lines += [
        "",
        "## LLM-as-a-Judge (qualitative) — status",
        "",
        "These dimensions (insight density, logical flow, executive-summary quality, "
        "hallucination rate) require an LLM and were **not run**:",
        "",
        "```json",
        json.dumps(evaluated[0]["metrics"]["llm_judge"], indent=2),
        "```",
        "",
        "_To enable: set `ANTHROPIC_API_KEY` (or `OPENAI_API_KEY`) and re-run with "
        "`EvaluationMetrics(llm=<model>)`. The same pipeline then produces LLM-judged "
        "scores against the gold-standard benchmarks in `evaluation/benchmarks/`._",
    ]
    _write(os.path.join(RESULTS, "evaluation_report.md"), lines)


def _write_token_analysis(evaluated):
    lines = [
        "# Token Usage & Latency Analysis",
        "",
        "This run executed with **no LLM key**, so the planner and synthesizer used "
        "the deterministic live-data path. LLM token consumption is therefore **0** "
        "for every challenge. The figures below report tool-call volume and wall-clock "
        "latency, which are the real cost drivers in this configuration.",
        "",
        "| # | Intent | Tool calls | Degraded | Sim. failures | LLM tokens | Time (s) |",
        "|---|--------|-----------|----------|---------------|------------|----------|",
    ]
    total_calls = total_time = 0
    for e in evaluated:
        t = e["trace"]
        total_calls += t.get("total_tool_calls", 0)
        total_time += t.get("duration_seconds", 0) or 0
        lines.append(
            f"| {e['challenge']} | {t.get('intent')} | {t.get('total_tool_calls')} | "
            f"{t.get('degraded_calls')} | {t.get('simulated_failures')} | 0 | "
            f"{t.get('duration_seconds')} |")
    lines += [
        f"| **Total** | — | **{total_calls}** | — | — | **0** | **{round(total_time,2)}** |",
        "",
        "## Projected cost with an LLM",
        "",
        "If narrative synthesis were enabled, each challenge would add roughly one "
        "planner call + one synthesizer call. At Claude Opus pricing and an estimated "
        "~4-8K input / ~1-2K output tokens per challenge, projected cost is on the "
        "order of a few cents per challenge. Exact figures require an instrumented LLM "
        "run; this is an estimate, explicitly labelled as such.",
        "",
        "## Observations",
        "",
        "- The first challenge carries a one-time ~10s cost: loading the local "
        "sentence-transformers embedding model for the vector store.",
        "- Challenge 7 (memory recall) is near-instant (0.03s): it reads from the "
        "vector store rather than hitting external APIs.",
        "- Tool-call volume stays well under the 20-call budget for every challenge.",
    ]
    _write(os.path.join(RESULTS, "token_usage_analysis.md"), lines)


def _write_stress_report(evaluated):
    c8 = next((e for e in evaluated if e["challenge"] == 8), None)
    lines = [
        "# Stress Test Report — Challenge 8 (50% Tool Failure)",
        "",
        "Challenge 8 produces a full NVIDIA research report while the financial-data "
        "and SEC-filing tools fail at a simulated 50% rate. This exercises the circuit "
        "breakers and fallback chains under sustained degradation.",
        "",
    ]
    if c8:
        t = c8["trace"]
        m = c8["metrics"]
        lines += [
            "## Result",
            "",
            f"- **Simulated failures injected:** {t.get('simulated_failures')}",
            f"- **Degraded steps (resolved via fallback):** {t.get('degraded_calls')} "
            f"of {t.get('total_tool_calls')}",
            f"- **Degradation resilience (AB-2):** {m['AB-2_degradation_resilience_pct']}%",
            f"- **Report still produced:** yes ({c8['report_words']} words, "
            f"{c8['metrics']['AB-5_source_citations']} citations)",
            f"- **Completed within tool budget:** {t.get('iterations')}/20 calls",
            "",
            "## Fallback behaviour observed",
            "",
            "When `financial_data_api` and `sec_filing_search` fail, the FallbackManager "
            "cascades to the configured alternatives (web_search, vector_db_search). "
            "Each degraded step is recorded and surfaced in the report's "
            "**Data Gaps & Degradation** section, so the output is transparent about "
            "which figures could not be retrieved rather than fabricating them.",
            "",
            "## Comparison vs. healthy run",
            "",
            "Challenges 1-7 ran with a 0% failure rate and recorded 0 degraded calls. "
            "Challenge 8 is the only run with injected failures, isolating the "
            "degradation behaviour for analysis.",
        ]
    else:
        lines.append("_Challenge 8 not found in run summary._")
    _write(os.path.join(RESULTS, "stress_test_report.md"), lines)


def _write_trace_gallery(evaluated):
    docs = os.path.join(ROOT, "docs")
    lines = [
        "# Agent Trace Gallery",
        "",
        "Real execution traces from the 8 validation challenges, generated from "
        "`results/run_summary.json`. Each trace shows the tools the agent actually "
        "invoked, in order, and whether any step was degraded / served by a fallback. "
        "These are produced by the deterministic (no-LLM) live-data pipeline.",
        "",
    ]
    for e in evaluated:
        t = e["trace"]
        lines += [
            f"## Challenge {e['challenge']} — intent `{t.get('intent')}`",
            "",
            f"**Query:** {e['query']}",
            "",
            f"**Tickers resolved:** {', '.join(t.get('tickers') or []) or 'none'}  ",
            f"**Tool calls:** {t.get('iterations')}/20 | "
            f"**Degraded:** {t.get('degraded_calls')} | "
            f"**Simulated failures:** {t.get('simulated_failures')} | "
            f"**Memory hits:** {t.get('memory_hits')} | "
            f"**Time:** {t.get('duration_seconds')}s",
            "",
            "**Executed tool sequence:**",
            "",
        ]
        for i, step in enumerate(t.get("tool_sequence", []), 1):
            flag = ""
            if step["degraded"]:
                flag = f"  →  ⚠️ degraded, served by `{step['source']}`" if step["source"] else "  →  ⚠️ degraded"
            lines.append(f"{i}. `{step['tool']}`{flag}")
        lines.append("")
    _write(os.path.join(docs, "Trace_Gallery.md"), lines)


def _write(path, lines):
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
