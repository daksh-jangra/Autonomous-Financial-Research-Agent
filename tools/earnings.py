import os
import httpx
import logging

def earnings_transcript(ticker: str, quarter: str, year: int) -> str:
    """Retrieves earnings call transcript using Financial Modeling Prep API."""
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        return f"[MOCK] Transcript for {ticker} {quarter} {year}. (Set FMP_API_KEY for real data)"
        
    url = f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{ticker}?quarter={quarter}&year={year}&apikey={api_key}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list):
            return data[0].get("content", "No content available in the transcript.")
        return f"No transcript found for {ticker} {quarter} {year}."
    except Exception as e:
        logging.error(f"FMP API Error: {str(e)}")
        return f"Error retrieving transcript: {str(e)}"
