from agent.core import FinancialResearchAgent
import json
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    
    agent = FinancialResearchAgent()
    
    query = "Analyze the impact of a 50 bps interest rate hike on the US regional banking sector, focusing on KRE constituents like USB, PNC, and TFC. Evaluate net interest margin compression risks and commercial real estate exposure."
    
    print(f"Starting Challenge 8...")
    print(f"Query: {query}")
    
    result = agent.run(query)
    
    print("\n--- Final Report ---")
    print(result.get("report", "Report generation failed."))
    
    print("\n--- Trace Metrics ---")
    print(json.dumps(result.get("trace", {}), indent=2))
    
if __name__ == "__main__":
    main()
