class Disambiguator:
    def __init__(self, llm=None):
        self.llm = llm

    def disambiguate(self, query: str, analysis: dict, short_term_memory: list) -> dict:
        """
        Resolves ambiguous queries using temporal or conversation context.
        If ambiguity cannot be resolved, it formulates clarifying questions or documents assumptions.
        """
        result = {
            "original_query": query,
            "resolved_query": query,
            "assumptions_made": [],
            "clarifying_questions": []
        }

        if not analysis.get("requires_disambiguation"):
            return result

        # Mock Disambiguation logic based on historical context requirement (Section A7.3)
        if "bank stress tests" in query.lower():
            if "2007" in query:
                result["resolved_query"] = "European Banking Authority stress test 2007"
                result["assumptions_made"].append("Assumed EBA based on 2007 timeline.")
            elif "2009" in query:
                result["resolved_query"] = "US Federal Reserve SCAP stress test 2009"
                result["assumptions_made"].append("Assumed SCAP based on 2009 timeline.")
            else:
                result["clarifying_questions"].append("Are you referring to the US SCAP tests, CCAR tests, or European EBA stress tests?")
        
        elif query.lower() == "apple":
            result["resolved_query"] = "Apple Inc. (AAPL) financial performance and business overview"
            result["assumptions_made"].append("Assumed user meant the publicly traded technology company Apple Inc.")

        # Rate of change detection
        if "rapid" in query.lower() or "sudden" in query.lower() or "acquisition" in query.lower():
            result["assumptions_made"].append("[FLAG] Temporal sensitivity detected. Prioritizing recent news over historical SEC filings.")

        return result
