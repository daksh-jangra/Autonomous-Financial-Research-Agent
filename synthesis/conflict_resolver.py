from typing import List, Dict

# Tier 1: SEC filings
# Tier 2: Financial Data APIs
# Tier 3: Earnings Call Transcripts
# Tier 4: Social Media / Forums (not used here)
# Tier 5: News Outlets
TIER_WEIGHTS = {
    "10-K": 1,
    "10-Q": 1,
    "8-K": 1,
    "financial_data_api": 2,
    "earnings_transcript": 3,
    "news": 5
}

def resolve_conflict(data_points: List[Dict]) -> Dict:
    """
    Resolves conflicts across multiple data sources reporting on the same metric.
    Expects data_points to be a list of dicts like:
    [{"value": 1000, "source": "10-K", "date": "2023-12-31"}, ...]
    """
    if not data_points:
        return {"resolved_value": None, "confidence": 0, "resolution_notes": "No data points provided."}
        
    if len(data_points) == 1:
        return {"resolved_value": data_points[0]["value"], "confidence": 0.9, "resolution_notes": "Single source."}
        
    # Check if all values are equal
    values = [dp["value"] for dp in data_points]
    if len(set(values)) == 1:
        return {"resolved_value": values[0], "confidence": 0.99, "resolution_notes": "All sources agree."}
        
    # Conflicts exist. Sort by tier weight (lower is better)
    sorted_points = sorted(data_points, key=lambda x: TIER_WEIGHTS.get(x.get("source", "news"), 99))
    
    best_point = sorted_points[0]
    
    return {
        "resolved_value": best_point["value"],
        "confidence": 0.7,
        "resolution_notes": f"Conflict detected among sources: {set(dp['source'] for dp in data_points)}. Resolved by trusting the highest-tier source: {best_point['source']}."
    }
