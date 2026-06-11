from agent.core import FinancialResearchAgent

def test_agent_initialization():
    agent = FinancialResearchAgent()
    assert agent.graph is not None

def test_agent_run_mock():
    agent = FinancialResearchAgent()
    # When no LLM is provided, it uses mock behavior
    result = agent.run("Create a comprehensive profile of Microsoft Corporation")
    
    # Verify the mock outputs
    assert "draft_report" in result
    assert "MOCK DRAFT REPORT" in result["draft_report"]
    assert "gathered_data" in result
    assert "step_0" in result["gathered_data"]
    assert "step_1" in result["gathered_data"]
    assert result["current_step"] == 2
    assert result["iteration_count"] == 2
