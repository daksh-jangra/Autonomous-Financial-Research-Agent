"""Build an LLM from environment variables, if a key is present.

Keeps the entry points (CLI, web app) provider-agnostic: they call
``build_llm_from_env()`` and get back a configured LangChain chat model when a
key is available, or ``None`` (deterministic live-data mode) otherwise. Missing
provider packages degrade gracefully to ``None`` rather than crashing.
"""
import os


def build_llm_from_env():
    """Return a LangChain chat model based on available env keys, else None.

    Priority: Anthropic > OpenAI > Google Gemini. Model names are overridable
    via ARA_LLM_MODEL.
    """
    override = os.getenv("ARA_LLM_MODEL")

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=override or "claude-opus-4-8", temperature=0)
        except ImportError:
            pass

    if os.getenv("OPENAI_API_KEY"):
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=override or "gpt-4o", temperature=0)
        except ImportError:
            pass

    if os.getenv("GOOGLE_API_KEY"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=override or "gemini-1.5-flash", temperature=0)
        except ImportError:
            pass

    return None


def llm_status():
    """Human-readable description of the active LLM mode."""
    llm = build_llm_from_env()
    if llm is None:
        return "deterministic live-data mode (no LLM key detected)"
    return f"LLM mode: {type(llm).__name__}"
