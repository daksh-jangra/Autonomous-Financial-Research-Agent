"""Evaluation metrics for the Autonomous Financial Research Agent.

Two families of metrics:
  * Deterministic metrics — computed directly from execution traces and report
    text (tool efficiency, degradation resilience, memory utilisation, report
    completeness, source grounding, token usage). These are always real.
  * LLM-as-a-judge metrics — qualitative scores (insight density, logical flow,
    hallucination rate) that genuinely require an LLM. When no LLM is supplied
    they are returned as "unavailable" rather than fabricated.
"""
import re

# Sections we expect a complete report to contain, per query intent.
EXPECTED_SECTIONS = {
    "profile": ["Company Overview", "Financial Analysis", "Market Sentiment & News",
                "Research Methodology"],
    "earnings": ["Company Overview", "Financial Analysis", "Market Sentiment & News",
                 "Research Methodology"],
    "risk": ["Company Overview", "Financial Analysis", "SEC Filings & Risk Factors",
             "Market Sentiment & News", "Research Methodology"],
    "comparison": ["Company Overview", "Financial Analysis", "Peer Comparison",
                   "Research Methodology"],
    "contradiction": ["Company Overview", "Financial Analysis", "Market Sentiment & News",
                      "Fact Verification", "Research Methodology"],
    "ambiguous": ["Query Interpretation & Assumptions", "Company Overview",
                  "Research Methodology"],
    "sector_memory": ["Prior Research Recalled (Long-Term Memory)", "Synthesis",
                      "Research Methodology"],
    "full_report": ["Company Overview", "Financial Analysis", "Data Gaps & Degradation",
                    "Research Methodology"],
}


class EvaluationMetrics:
    def __init__(self, llm=None):
        self.llm = llm

    # ---- deterministic metrics -------------------------------------------
    def calculate_tool_efficiency(self, tool_calls: int, useful_calls: int) -> float:
        """AB-1: percentage of tool calls that returned useful, non-degraded data."""
        if tool_calls == 0:
            return 100.0
        return round((useful_calls / tool_calls) * 100, 1)

    def calculate_memory_utilization(self, memory_hits: int, total_api_calls: int) -> float:
        """AB-4: share of information acts served from memory vs. external APIs.

        Note: the project document erroneously specified multiplying these two
        counts (see ERROR_LOG.md). The correct form is a ratio.
        """
        total = memory_hits + total_api_calls
        if total == 0:
            return 0.0
        return round(memory_hits / total, 3)

    def calculate_degradation_resilience(self, trace: dict) -> float:
        """AB-2: percentage of degraded/failed steps that still yielded output
        via fallback chains (i.e. the run completed despite failures)."""
        total = trace.get("total_tool_calls", 0)
        degraded = trace.get("degraded_calls", 0)
        if total == 0:
            return 100.0
        # A report is always produced; resilience = non-fatal completion rate.
        return round((1 - (degraded / total)) * 100, 1)

    def report_completeness(self, intent: str, section_titles: list) -> dict:
        """AB-3: fraction of expected sections present for the query intent."""
        expected = EXPECTED_SECTIONS.get(intent, ["Research Methodology"])
        present = [s for s in expected if any(s in t for t in section_titles)]
        missing = [s for s in expected if s not in present]
        return {
            "expected": len(expected),
            "present": len(present),
            "missing": missing,
            "score_pct": round(len(present) / len(expected) * 100, 1) if expected else 100.0,
        }

    def source_grounding(self, report_text: str) -> int:
        """AB-5: count of explicit source citations in the report."""
        # Our reports cite live sources inline (e.g. "(yfinance)", SEC accession,
        # URLs). Count distinct grounding markers.
        markers = re.findall(r"yfinance|SEC EDGAR|Accession|https?://|10-K|10-Q", report_text)
        return len(markers)

    # ---- LLM-as-a-judge (qualitative) ------------------------------------
    def llm_judge_score(self, report: str, benchmark: str = "") -> dict:
        """Qualitative judgement of report quality. Requires an LLM; returns an
        explicit 'unavailable' result when none is configured (never fabricated)."""
        if self.llm is None:
            return {
                "status": "unavailable",
                "reason": "No LLM key configured; qualitative judging is disabled. "
                          "Set ANTHROPIC_API_KEY/OPENAI_API_KEY to enable.",
                "dimensions": ["insight_density", "logical_flow",
                               "executive_summary_quality", "hallucination_rate"],
            }
        # With an LLM, prompt it with the rubric and parse a 1-5 score per dim.
        from langchain_core.messages import HumanMessage
        prompt = (
            "You are an expert financial-research reviewer. Score the REPORT 1-5 on "
            "insight_density, logical_flow, executive_summary_quality, and estimate a "
            "hallucination_rate (% of claims unsupported by sources). Compare against the "
            f"BENCHMARK if provided.\n\nBENCHMARK:\n{benchmark[:2000]}\n\nREPORT:\n{report[:6000]}\n\n"
            "Respond as compact JSON with those four keys.")
        try:
            import json as _json
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            m = re.search(r"\{.*\}", resp.content, re.DOTALL)
            return _json.loads(m.group(0)) if m else {"status": "parse_error", "raw": resp.content[:300]}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    # ---- aggregate -------------------------------------------------------
    def run_full_evaluation(self, report: str, intent: str, section_titles: list,
                            trace: dict, benchmark: str = "") -> dict:
        """Runs the full metric suite for one challenge."""
        return {
            "AB-1_tool_efficiency_pct": self.calculate_tool_efficiency(
                trace.get("total_tool_calls", 0), trace.get("useful_calls", 0)),
            "AB-2_degradation_resilience_pct": self.calculate_degradation_resilience(trace),
            "AB-3_report_completeness": self.report_completeness(intent, section_titles),
            "AB-4_memory_utilization": self.calculate_memory_utilization(
                trace.get("memory_hits", 0), trace.get("total_tool_calls", 0)),
            "AB-5_source_citations": self.source_grounding(report),
            "tokens": trace.get("tokens", 0),
            "duration_seconds": trace.get("duration_seconds"),
            "llm_judge": self.llm_judge_score(report, benchmark),
        }
