import logging
from tools.tool_registry import ToolRegistry

class FallbackManager:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        
        # Define fallback tool chains for primary tools
        self.fallback_chains = {
            "financial_data_api": ["sec_filing_search", "web_search", "vector_db_search"],
            "sec_filing_search": ["web_search", "vector_db_search"],
            "earnings_transcript": ["news_sentiment", "web_search"]
        }

    def execute_with_fallback(self, tool_name: str, kwargs: dict) -> dict:
        """Executes a tool and cascades through fallbacks if it fails."""
        try:
            result = self.registry.execute_tool(tool_name, kwargs)
            if not str(result).startswith("Error") and not str(result).startswith("No "):
                return {"result": result, "source_tool": tool_name, "degraded": False}
        except Exception as e:
            logging.warning(f"Primary tool {tool_name} failed: {e}")

        # Primary failed, attempt fallbacks
        fallbacks = self.fallback_chains.get(tool_name, [])
        for fallback_tool in fallbacks:
            logging.info(f"Attempting fallback: {fallback_tool} for {tool_name}")
            try:
                # Adjust kwargs for fallback tool if necessary (simplified for demo)
                fallback_kwargs = self._adapt_kwargs(tool_name, fallback_tool, kwargs)
                if not fallback_kwargs: continue
                
                result = self.registry.execute_tool(fallback_tool, fallback_kwargs)
                if not str(result).startswith("Error") and not str(result).startswith("No "):
                    return {
                        "result": result, 
                        "source_tool": fallback_tool, 
                        "degraded": True,
                        "degradation_note": f"Used {fallback_tool} as a fallback for {tool_name}."
                    }
            except Exception as e:
                logging.warning(f"Fallback tool {fallback_tool} failed: {e}")

        # All fallbacks failed: Graceful Degradation
        return {
            "result": None,
            "source_tool": None,
            "degraded": True,
            "degradation_note": f"[DATA UNAVAILABLE] Could not retrieve data using {tool_name} or any fallbacks. Proceeding with partial analysis."
        }

    def _adapt_kwargs(self, primary: str, fallback: str, kwargs: dict) -> dict:
        """Adapts arguments from a primary tool to a fallback tool."""
        # This is a complex mapping problem in real life; simplified for architecture demo
        if fallback == "web_search":
            return {"query": f"Financial data for {kwargs.get('ticker', '')}"}
        if fallback == "sec_filing_search" and "ticker" in kwargs:
            return {"ticker": kwargs["ticker"], "filing_type": "10-K"}
        if fallback == "vector_db_search":
            return {"query": f"{kwargs.get('ticker', '')}", "top_k": 3}
        return kwargs
