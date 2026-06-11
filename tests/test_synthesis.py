from synthesis.conflict_resolver import resolve_conflict
from synthesis.engine import SynthesisEngine

def test_conflict_resolver_agreeing_sources():
    data = [
        {"value": 100, "source": "10-K"},
        {"value": 100, "source": "financial_data_api"}
    ]
    result = resolve_conflict(data)
    assert result["resolved_value"] == 100
    assert result["confidence"] == 0.99

def test_conflict_resolver_disagreeing_sources():
    data = [
        {"value": 105, "source": "news"},
        {"value": 100, "source": "10-K"}
    ]
    result = resolve_conflict(data)
    # Should prefer 10-K (Tier 1) over news (Tier 5)
    assert result["resolved_value"] == 100
    assert result["confidence"] == 0.7
    assert "10-K" in result["resolution_notes"]

def test_synthesis_engine():
    engine = SynthesisEngine()
    obs = {
        "step_0": "Fetched 10-K",
        "financials": {"revenue": 1000},
        "sentiment": {"overall_sentiment": "Positive"}
    }
    result = engine.synthesize(obs)
    assert "Financial Context" in result
    assert "Market Sentiment" in result
    assert "Positive" in result
    assert "Fetched 10-K" in result
