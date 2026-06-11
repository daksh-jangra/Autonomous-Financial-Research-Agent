import yfinance as yf
import json

def company_profile(ticker: str) -> str:
    """Retrieves basic company information using yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    if not info:
        return f"No company profile found for {ticker}."
        
    profile = {
        "ticker": ticker,
        "name": info.get("shortName", info.get("longName", ticker)),
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "market_cap": info.get("marketCap", "Unknown"),
        "description": info.get("longBusinessSummary", "No description available."),
        "website": info.get("website", "Unknown")
    }
    
    # Safely extract executives if available
    executives = info.get("companyOfficers", [])
    profile["executives"] = [{"name": officer.get("name"), "title": officer.get("title")} for officer in executives[:5]]
    
    return json.dumps(profile)
