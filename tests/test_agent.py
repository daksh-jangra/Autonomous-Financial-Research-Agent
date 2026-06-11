from agent.core import FinancialResearchAgent


def test_agent_initialization():
    agent = FinancialResearchAgent()
    assert agent.graph is not None


def test_agent_run_real_pipeline():
    """Without an LLM the agent runs the deterministic live-data pipeline and
    produces a structured report plus a trace (no 'MOCK' placeholders)."""
    agent = FinancialResearchAgent(enable_memory=False)
    result = agent.run("Create a comprehensive profile of Microsoft Corporation")

    # Report + trace are produced.
    assert "report" in result and result["report"].startswith("# Investment Research Report")
    assert "trace" in result
    assert result["trace"]["intent"] == "profile"
    assert "MSFT" in result["trace"]["tickers"]

    # The 6-node pipeline executed real tool calls.
    assert result["trace"]["total_tool_calls"] >= 2
    assert result["iteration_count"] >= 2

    # Standard analyst sections are present.
    assert "## Company Overview" in result["report"]
    assert "## Research Methodology" in result["report"]


def test_failure_injection_records_degradation():
    """Challenge-8 mode injects simulated failures and resolves via fallbacks."""
    agent = FinancialResearchAgent(failure_rate=1.0, enable_memory=False)
    result = agent.run("Produce a complete investment research report on NVIDIA Corporation")
    # With a 100% failure rate on unreliable tools, failures must be injected.
    assert result["trace"]["simulated_failures"] >= 1
    assert result["trace"]["degraded_calls"] >= 1
