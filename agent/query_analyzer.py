import json

class QueryAnalyzer:
    def __init__(self, llm=None):
        self.llm = llm

    def analyze(self, query: str) -> dict:
        """
        Classifies the type, complexity, and ambiguity level of an incoming query.
        Also handles edge cases like private companies or recent IPOs.
        """
        # In a real implementation, this would use the LLM with a specific classification prompt
        # Mock logic for architecture demonstration
        analysis = {
            "query": query,
            "type": "company_analysis" if "company" in query.lower() or "inc" in query.lower() else "general_research",
            "complexity": "high" if "compare" in query.lower() or "evaluate" in query.lower() else "medium",
            "ambiguity_level": "low",
            "requires_disambiguation": False,
            "edge_cases_detected": []
        }

        # Edge case detection heuristics
        if "private" in query.lower():
            analysis["edge_cases_detected"].append("private_company")
        if "ipo" in query.lower():
            analysis["edge_cases_detected"].append("recent_ipo")
            
        # Ambiguity detection heuristic
        if len(query.split()) < 4 and not query.isupper():
            # Very short query like "Apple" or "bank stress tests"
            analysis["ambiguity_level"] = "high"
            analysis["requires_disambiguation"] = True

        return analysis
