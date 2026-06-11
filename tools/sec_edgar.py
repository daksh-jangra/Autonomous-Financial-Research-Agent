import os
import httpx
import json
from tenacity import retry, stop_after_attempt, wait_exponential

class SecEdgarTool:
    def __init__(self):
        self.headers = {"User-Agent": "QuantumEdge Research Agent (contact@quantumedge.com)"}
        self.base_url = "https://efts.sec.gov/LATEST/search-index"

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    def search(self, ticker: str, filing_type: str, year: int = None) -> str:
        """Searches SEC EDGAR full-text API for a specific filing."""
        # EDGAR full-text search (EFTS) expects a GET request with query params.
        # The keyword goes in `q`; filing types in `forms`; dates in startdt/enddt.
        query_params = {
            "q": ticker,
            "forms": filing_type
        }
        if year:
            query_params["startdt"] = f"{year}-01-01"
            query_params["enddt"] = f"{year}-12-31"

        try:
            response = httpx.get(self.base_url, params=query_params, headers=self.headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("hits", {}).get("hits"):
                return f"No {filing_type} filings found for {ticker}."
                
            # Extract the top hit
            top_hit = data["hits"]["hits"][0]
            # Since this is an architectural demo, we return the metadata and snippet
            # In a full production system we would fetch the raw HTML and parse it
            return f"Found {filing_type} for {ticker} (Accession: {top_hit['_id']}). Summary snippet: {top_hit['_source'].get('display_names', '')}"
            
        except httpx.HTTPError as e:
            raise Exception(f"SEC EDGAR API Error: {str(e)}")

def get_sec_edgar_tool():
    tool = SecEdgarTool()
    return tool.search
