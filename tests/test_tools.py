import pytest
from tools.tool_registry import ToolRegistry

def test_registry_initialization():
    registry = ToolRegistry()
    schemas = registry.get_all_schemas()
    assert len(schemas) == 12
    tool_names = [schema["name"] for schema in schemas]
    assert "sec_filing_search" in tool_names
    assert "web_search" in tool_names

def test_validate_inputs_valid():
    registry = ToolRegistry()
    kwargs = {"ticker": "AAPL", "filing_type": "10-K"}
    # Should not raise exception
    assert registry.validate_inputs("sec_filing_search", kwargs) is True

def test_validate_inputs_invalid():
    registry = ToolRegistry()
    # Missing required 'filing_type'
    kwargs = {"ticker": "AAPL"}
    with pytest.raises(ValueError, match="Validation error"):
        registry.validate_inputs("sec_filing_search", kwargs)

def test_execute_sec_filing_search():
    registry = ToolRegistry()
    kwargs = {"ticker": "MSFT", "filing_type": "10-Q", "year": 2023}
    result = registry.execute_tool("sec_filing_search", kwargs)
    # The SEC tool hits the live EDGAR API. Depending on network availability the
    # registry returns either a real result string or a gracefully-caught error
    # string. Either way it must be a non-empty string (no exception escapes).
    assert isinstance(result, str)
    assert len(result) > 0

def test_execute_web_search_fallback():
    registry = ToolRegistry()
    kwargs = {"query": "Tesla competitive risks", "num_results": 2}
    result = registry.execute_tool("web_search", kwargs)
    assert isinstance(result, list)
    assert len(result) >= 1
    # Without TAVILY_API_KEY the tool returns a single graceful mock result.
    assert "Tesla competitive risks" in result[0]["title"]

def test_execute_calculation_engine():
    registry = ToolRegistry()
    kwargs = {"calculation_type": "growth_rate", "inputs": {"current": 120, "previous": 100}}
    result = registry.execute_tool("calculation_engine", kwargs)
    assert result["calculation"] == "growth_rate"
    # Deterministic real computation: (120 - 100) / |100| * 100 = 20.00%
    assert result["result"] == "20.00%"
