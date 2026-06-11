from agent.core import FinancialResearchAgent
import json
import logging

def main():
    logging.disable(logging.CRITICAL)

    # Challenge 8: full research report with a 50% simulated tool-failure rate.
    agent = FinancialResearchAgent(failure_rate=0.5)

    query = ("Produce a complete investment research report on NVIDIA Corporation. "
             "Note: The financial data API and SEC filing search tools are currently "
             "experiencing intermittent failures (simulate 50% failure rate).")
    
    print(f"Starting Challenge 8...")
    print(f"Query: {query}")
    
    result = agent.run(query)
    
    print("\n--- Final Report ---")
    print(result.get("report", "Report generation failed."))
    
    print("\n--- Trace Metrics ---")
    print(json.dumps(result.get("trace", {}), indent=2))
    
if __name__ == "__main__":
    main()
