import json
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage

from tools.tool_registry import ToolRegistry
from agent.prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT
from agent.parser import parse_plan

class ResearchState(TypedDict):
    query: str
    plan: List[str]
    current_step: int
    gathered_data: dict
    draft_report: str
    verified_report: str
    iteration_count: int

class FinancialResearchAgent:
    def __init__(self, llm=None):
        self.registry = ToolRegistry()
        self.llm = llm # Langchain LLM instance
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(ResearchState)
        
        graph.add_node('planner', self.plan_research)
        graph.add_node('executor', self.execute_step)
        graph.add_node('synthesizer', self.synthesize_findings)
        
        graph.set_entry_point('planner')
        graph.add_edge('planner', 'executor')
        
        graph.add_conditional_edges(
            'executor',
            self.should_continue,
            {True: 'executor', False: 'synthesizer'}
        )
        
        graph.add_edge('synthesizer', END)
        return graph.compile()

    def plan_research(self, state: ResearchState):
        if not self.llm:
            # Mock behavior for testing
            return {"plan": ["Mock step 1", "Mock step 2"], "current_step": 0, "gathered_data": {}, "iteration_count": 0}
            
        tool_names = [s["name"] for s in self.registry.get_all_schemas()]
        prompt = PLANNER_PROMPT.format(tool_names=tool_names, query=state['query'])
        response = self.llm.invoke([HumanMessage(content=prompt)])
        plan = parse_plan(response.content)
        return {"plan": plan, "current_step": 0, "gathered_data": {}, "iteration_count": 0}

    def execute_step(self, state: ResearchState):
        step = state["plan"][state["current_step"]]
        # In a real implementation, the LLM would translate the step into a specific tool call.
        # For mock testing, we just use a generic web search.
        observation = self.registry.execute_tool("web_search", {"query": step})
        
        gathered_data = state.get("gathered_data", {})
        gathered_data[f"step_{state['current_step']}"] = observation
        
        return {
            "current_step": state["current_step"] + 1,
            "gathered_data": gathered_data,
            "iteration_count": state.get("iteration_count", 0) + 1
        }

    def should_continue(self, state: ResearchState):
        # Stop if we've completed all steps or hit the iteration limit
        if state["current_step"] >= len(state["plan"]):
            return False
        if state["iteration_count"] >= 20: # Constraint: Max 20 tool calls
            return False
        return True

    def synthesize_findings(self, state: ResearchState):
        if not self.llm:
            # Mock behavior for testing
            return {"draft_report": "# MOCK DRAFT REPORT\n" + str(state["gathered_data"])}
            
        prompt = SYNTHESIZER_PROMPT.format(
            query=state['query'],
            plan=json.dumps(state['plan']),
            observations=json.dumps(state['gathered_data'], indent=2)
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"draft_report": response.content}

    def run(self, query: str):
        initial_state = {"query": query}
        return self.graph.invoke(initial_state)
