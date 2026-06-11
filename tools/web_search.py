import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.url = "https://api.tavily.com/search"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search(self, query: str, num_results: int = 10, date_range: str = None) -> list:
        if not self.api_key:
            # Fallback to stub if no API key is provided
            return [{"url": "http://example.com/mock", "title": f"[MOCK] Search result for {query}", "snippet": "Configure TAVILY_API_KEY in .env to enable real search."}]
            
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": num_results
        }
        
        try:
            response = httpx.post(self.url, json=payload, timeout=15.0)
            response.raise_for_status()
            data = response.json()
            return [{"url": r["url"], "title": r["title"], "snippet": r["content"]} for r in data.get("results", [])]
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]

def get_web_search_tool():
    tool = WebSearchTool()
    return tool.search
