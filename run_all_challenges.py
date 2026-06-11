"""Run all 8 validation challenges and write outputs to results/.

Challenges run in order so that long-term memory (ChromaDB) accumulates: by the
time Challenge 7 ("themes across companies you've already researched") runs, the
earlier company analyses are in the vector store. Challenge 8 runs with a 50%
simulated failure rate on the financial-data and SEC tools to exercise the
fallback chains.

Without an LLM key the agent uses its deterministic live-data synthesis path
(yfinance + SEC EDGAR). Set ANTHROPIC_API_KEY / OPENAI_API_KEY to upgrade the
narrative to LLM-written prose using the same pipeline.
"""
import json
import logging
import os
import shutil

from agent.core import FinancialResearchAgent

logging.disable(logging.CRITICAL)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

CHALLENGES = [
    (1, "Create a comprehensive profile of Microsoft Corporation including business "
        "overview, financial summary, key executives, and recent developments."),
    (2, "Analyze Apple Inc.'s most recent quarterly earnings. Compare actual results "
        "to consensus estimates and identify key takeaways from the earnings call."),
    (3, "Produce a comprehensive risk assessment for Tesla Inc. covering financial "
        "risks, operational risks, regulatory risks, and competitive risks."),
    (4, "Compare the cloud computing divisions of Amazon (AWS), Microsoft (Azure), and "
        "Google (GCP). Analyze revenue growth, market share, margins, and competitive "
        "advantages."),
    (5, "Research Palantir Technologies. Note: Recent news reports suggest the company "
        "is struggling, but their financial statements show strong growth. Investigate "
        "and explain the apparent contradiction."),
    (6, "What's happening with the banks?"),
    (7, "Based on the companies you've already researched, what themes emerge across "
        "the technology sector? Identify cross-cutting risks and opportunities."),
    (8, "Produce a complete investment research report on NVIDIA Corporation. Note: The "
        "financial data API and SEC filing search tools are currently experiencing "
        "intermittent failures (simulate 50% failure rate)."),
]


def make_agent(num):
    """Challenge 8 gets the degradation harness; all share memory."""
    failure_rate = 0.5 if num == 8 else 0.0
    return FinancialResearchAgent(failure_rate=failure_rate, enable_memory=True)


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # Fresh memory for a clean, reproducible accumulation across challenges.
    if os.path.isdir(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)

    summary_rows = []
    for num, query in CHALLENGES:
        print(f"\n{'='*70}\nChallenge {num}\n{query}\n{'='*70}")
        agent = make_agent(num)
        result = agent.run(query)
        report = result.get("report", "Report generation failed.")
        trace = result.get("trace", {})

        out_path = os.path.join(RESULTS_DIR, f"challenge_{num}.md")
        with open(out_path, "w") as f:
            f.write(report)
            f.write("\n\n---\n\n## Execution Trace\n\n```json\n")
            f.write(json.dumps(trace, indent=2))
            f.write("\n```\n")

        print(f"-> wrote {out_path}")
        print(f"   intent={trace.get('intent')} tickers={trace.get('tickers')} "
              f"calls={trace.get('total_tool_calls')} degraded={trace.get('degraded_calls')} "
              f"sim_failures={trace.get('simulated_failures')} mem_hits={trace.get('memory_hits')}")
        summary_rows.append((num, trace))

    # Token-usage / run summary used by the evaluation report.
    print("\n\nAll challenges complete. Summary:")
    for num, t in summary_rows:
        print(f"  Challenge {num}: {t.get('iterations')} tool calls, "
              f"{t.get('degraded_calls')} degraded, {t.get('duration_seconds')}s")


if __name__ == "__main__":
    main()
