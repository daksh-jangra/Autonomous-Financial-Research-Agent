"""Interactive command-line interface for the Autonomous Financial Research Agent.

Usage:
    python cli.py                      # interactive prompt (type queries, Ctrl-D to quit)
    python cli.py "Profile Apple Inc." # one-shot: run a single query and exit
"""
import logging
import os
import sys
import warnings

# Keep the prompt clean: silence library logging, warnings, and HF progress bars.
logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from agent.core import FinancialResearchAgent
from agent.llm_factory import build_llm_from_env, llm_status

BANNER = r"""
========================================================
  Autonomous Financial Research Agent (ARA-1)
========================================================
"""

EXAMPLES = [
    "Create a comprehensive profile of Microsoft Corporation",
    "Produce a risk assessment for Tesla Inc.",
    "Compare the cloud divisions of Amazon, Microsoft, and Google",
    "What's happening with the banks?",
]


def run_query(agent, query):
    print("\nResearching... (this may take a few seconds)\n")
    result = agent.run(query)
    print(result.get("report", "Report generation failed."))
    t = result.get("trace", {})
    print("\n" + "-" * 56)
    print(f"intent={t.get('intent')} | tickers={t.get('tickers')} | "
          f"tool_calls={t.get('iterations')} | degraded={t.get('degraded_calls')} | "
          f"time={t.get('duration_seconds')}s")
    print("-" * 56 + "\n")


def main():
    agent = FinancialResearchAgent(llm=build_llm_from_env())

    # One-shot mode: query passed as a command-line argument.
    if len(sys.argv) > 1:
        run_query(agent, " ".join(sys.argv[1:]))
        return

    # Interactive mode.
    print(BANNER)
    print(f"Status: {llm_status()}")
    print("\nType a research question and press Enter. Examples:")
    for ex in EXAMPLES:
        print(f"  - {ex}")
    print("\nType 'exit' or press Ctrl-D to quit.\n")

    while True:
        try:
            query = input("research> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            print("Goodbye.")
            break
        try:
            run_query(agent, query)
        except Exception as e:  # never crash the REPL on a single bad query
            print(f"\n[error] {e}\n")


if __name__ == "__main__":
    main()
