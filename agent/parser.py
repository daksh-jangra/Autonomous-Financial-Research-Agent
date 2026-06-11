import json
import re

def parse_plan(llm_output: str) -> list:
    """Parses the JSON array of plan steps from the planner LLM output."""
    try:
        # Extract json array from markdown
        match = re.search(r'\[.*\]', llm_output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(llm_output)
    except json.JSONDecodeError:
        # Fallback if the LLM fails to return strict JSON
        return [step.strip('- ') for step in llm_output.split('\n') if step.strip()]

def parse_tool_call(llm_output: str) -> dict:
    """Parses a tool call from the executor LLM. Assuming ReAct style text format or JSON."""
    # Simplified parser: if using OpenAI function calling, this is handled natively by LangChain.
    # This acts as a fallback for raw text parsing.
    pass
