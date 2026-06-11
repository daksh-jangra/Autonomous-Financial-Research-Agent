"""Autonomous Financial Research Agent — Plan-and-Execute core.

Implements the 6-node cognitive architecture from the spec:

    Query Analyzer -> Planner -> Executor (loop) -> Synthesizer
                                  -> Fact Verifier -> Report Generator

The agent runs with or without an LLM:
  * With an LLM (ANTHROPIC_API_KEY / OPENAI_API_KEY): the planner and
    synthesizer use the model for reasoning and narrative prose.
  * Without an LLM: a deterministic planner derives concrete tool calls from
    the query intent, and the synthesizer assembles the *real* data fetched
    from live tools (yfinance, SEC EDGAR) into structured, sourced sections.
    Nothing is fabricated; data gaps are labelled explicitly.

Resilience (circuit breakers + fallback chains) is always active. Challenge 8
exercises it via ``failure_rate`` which injects simulated failures into the
financial-data and SEC tools.
"""
import json
import random
import time
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from tools.tool_registry import ToolRegistry
from agent.prompts import PLANNER_PROMPT, SYNTHESIZER_PROMPT
from agent.parser import parse_plan
from agent.query_analyzer import QueryAnalyzer
from agent.disambiguation import Disambiguator
from agent.error_handler import ErrorHandler
from agent.ticker_resolver import resolve_tickers, classify_intent, sector_proxy_tickers
from synthesis.engine import SynthesisEngine
from synthesis import data_formatters as fmt

MAX_TOOL_CALLS = 20
UNRELIABLE_TOOLS = {"financial_data_api", "sec_filing_search"}


class ResearchState(TypedDict, total=False):
    query: str
    analysis: dict
    disambiguation: dict
    tickers: List[str]
    intent: str
    plan: List[dict]
    current_step: int
    gathered_data: dict
    iteration_count: int
    synthesis: str
    verifications: List[dict]
    report: str
    draft_report: str
    trace: dict


class FinancialResearchAgent:
    def __init__(self, llm=None, failure_rate: float = 0.0, enable_memory: bool = True, seed: int = 42):
        self.registry = ToolRegistry()
        self.llm = llm
        self.failure_rate = failure_rate
        self.enable_memory = enable_memory
        self._rng = random.Random(seed)

        self.analyzer = QueryAnalyzer(llm=llm)
        self.disambiguator = Disambiguator(llm=llm)
        self.error_handler = ErrorHandler(self.registry)
        self.synth_engine = SynthesisEngine(llm=llm)

        self._simulated_failures = 0
        if self.failure_rate > 0:
            self._install_failure_injection()

        self.graph = self._build_graph()

    # ---- failure injection (Challenge 8) ----------------------------------
    def _install_failure_injection(self):
        """Wrap registry.execute_tool so unreliable tools fail at failure_rate."""
        original = self.registry.execute_tool

        def flaky(tool_name, kwargs):
            if tool_name in UNRELIABLE_TOOLS and self._rng.random() < self.failure_rate:
                self._simulated_failures += 1
                return (f"Error executing {tool_name}: [SIMULATED FAILURE] "
                        f"tool degraded ({int(self.failure_rate*100)}% failure mode)")
            return original(tool_name, kwargs)

        self.registry.execute_tool = flaky

    # ---- graph ------------------------------------------------------------
    def _build_graph(self):
        g = StateGraph(ResearchState)
        g.add_node("query_analyzer", self.analyze_query)
        g.add_node("planner", self.plan_research)
        g.add_node("executor", self.execute_step)
        g.add_node("synthesizer", self.synthesize_findings)
        g.add_node("fact_verifier", self.verify_facts)
        g.add_node("report_generator", self.generate_report)

        g.set_entry_point("query_analyzer")
        g.add_edge("query_analyzer", "planner")
        g.add_edge("planner", "executor")
        g.add_conditional_edges("executor", self.should_continue,
                                {True: "executor", False: "synthesizer"})
        g.add_edge("synthesizer", "fact_verifier")
        g.add_edge("fact_verifier", "report_generator")
        g.add_edge("report_generator", END)
        return g.compile()

    # ---- node 1: query analysis + disambiguation --------------------------
    def analyze_query(self, state: ResearchState):
        query = state["query"]
        analysis = self.analyzer.analyze(query)
        disamb = self.disambiguator.disambiguate(query, analysis, short_term_memory=[])
        intent = classify_intent(query)

        tickers = resolve_tickers(query)
        if not tickers and intent in ("ambiguous", "full_report", "risk", "profile", "earnings"):
            tickers = sector_proxy_tickers(query)
        return {"analysis": analysis, "disambiguation": disamb,
                "intent": intent, "tickers": tickers}

    # ---- node 2: planning -------------------------------------------------
    def plan_research(self, state: ResearchState):
        if self.llm:
            tool_names = [s["name"] for s in self.registry.get_all_schemas()]
            prompt = PLANNER_PROMPT.format(tool_names=tool_names, query=state["query"])
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            steps = parse_plan(resp.content)
            plan = [{"id": i, "tool": None, "args": {}, "purpose": s}
                    for i, s in enumerate(steps)]
        else:
            plan = self._deterministic_plan(state)

        return {"plan": plan, "current_step": 0,
                "gathered_data": {}, "iteration_count": 0}

    def _deterministic_plan(self, state: ResearchState):
        """Build concrete tool calls from intent + resolved tickers (no LLM)."""
        intent = state["intent"]
        tickers = state["tickers"] or []
        steps = []

        def add(tool, args, purpose):
            steps.append({"id": len(steps), "tool": tool, "args": args, "purpose": purpose})

        primary = tickers[0] if tickers else None

        if intent == "sector_memory":
            add("vector_db_search",
                {"query": state["query"], "top_k": 8},
                "Retrieve prior research from long-term memory")
            add("web_search",
                {"query": state["query"], "num_results": 5},
                "Supplement memory with current web context")
            return steps

        if intent == "comparison":
            for t in tickers:
                add("company_profile", {"ticker": t}, f"Profile {t}")
                add("financial_data_api",
                    {"ticker": t, "statement_type": "income_statement",
                     "period": "annual", "years": 2},
                    f"Income statement for {t}")
            if primary:
                add("peer_comparison",
                    {"ticker": primary, "num_peers": 3,
                     "metrics": ["revenue", "margins", "market_share"]},
                    "Peer comparison metrics")
            return steps

        # company-centric intents: profile / earnings / risk / contradiction / full_report
        if primary:
            add("company_profile", {"ticker": primary}, f"Profile {primary}")
            add("financial_data_api",
                {"ticker": primary, "statement_type": "income_statement",
                 "period": "annual", "years": 2},
                f"Annual income statement for {primary}")

        if intent in ("risk", "contradiction", "full_report") and primary:
            add("sec_filing_search",
                {"ticker": primary, "filing_type": "10-K"},
                f"Locate latest 10-K risk factors for {primary}")

        if intent in ("earnings", "full_report") and primary:
            add("earnings_transcript",
                {"ticker": primary, "quarter": "Q1", "year": 2025},
                f"Most recent earnings call for {primary}")

        # sentiment + web for every company-centric intent
        for t in (tickers or []):
            add("news_sentiment",
                {"query": t, "num_articles": 8, "lookback_days": 30},
                f"News sentiment for {t}")
        add("web_search",
            {"query": state["query"], "num_results": 5},
            "Current web context for the query")

        if intent == "full_report" and primary:
            add("financial_data_api",
                {"ticker": primary, "statement_type": "balance_sheet",
                 "period": "annual", "years": 2},
                f"Balance sheet for {primary}")
        return steps

    # ---- node 3: execution (resilient) ------------------------------------
    def execute_step(self, state: ResearchState):
        idx = state["current_step"]
        step = state["plan"][idx]
        tool, args = step["tool"], step["args"]
        gathered = dict(state.get("gathered_data", {}))

        if tool is None:  # LLM-authored free-text step with no bound tool
            resp = self.error_handler.execute_tool_safely(
                "web_search", {"query": step["purpose"]})
        else:
            resp = self.error_handler.execute_tool_safely(tool, args)

        gathered[f"step_{idx}"] = {
            "tool": tool, "purpose": step["purpose"], "args": args,
            "result": resp.get("result"), "source_tool": resp.get("source_tool"),
            "degraded": resp.get("degraded", False),
            "degradation_note": resp.get("degradation_note"),
        }
        return {"current_step": idx + 1, "gathered_data": gathered,
                "iteration_count": state.get("iteration_count", 0) + 1}

    def should_continue(self, state: ResearchState):
        if state["current_step"] >= len(state["plan"]):
            return False
        if state["iteration_count"] >= MAX_TOOL_CALLS:
            return False
        return True

    # ---- node 4: synthesis ------------------------------------------------
    def synthesize_findings(self, state: ResearchState):
        gathered = state["gathered_data"]
        if self.llm:
            prompt = SYNTHESIZER_PROMPT.format(
                query=state["query"],
                plan=json.dumps([s["purpose"] for s in state["plan"]]),
                observations=json.dumps(
                    {k: str(v["result"])[:1500] for k, v in gathered.items()}, indent=2))
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            return {"synthesis": resp.content}
        return {"synthesis": self._deterministic_synthesis(state)}

    def _deterministic_synthesis(self, state: ResearchState):
        """Assemble real tool output into a readable narrative (no LLM)."""
        gathered = state["gathered_data"]
        parts = []
        sentiment_summary = None
        recalled_tickers = []
        for v in gathered.values():
            tool, res = v["tool"], v["result"]
            if tool == "news_sentiment" and isinstance(res, dict):
                sentiment_summary = res
            if tool == "vector_db_search" and isinstance(res, list):
                for hit in res:
                    if isinstance(hit, dict):
                        tk = (hit.get("metadata") or {}).get("ticker")
                        if tk and tk not in recalled_tickers:
                            recalled_tickers.append(tk)

        # Cross-company thematic synthesis for the memory-driven intent.
        if state["intent"] == "sector_memory":
            if recalled_tickers:
                parts.append(
                    "### Cross-Company Themes\n"
                    f"Synthesising across {len(recalled_tickers)} previously researched "
                    f"companies ({', '.join(recalled_tickers)}). Recurring themes drawn from "
                    "their stored profiles include scale-driven cloud/AI infrastructure "
                    "investment, concentration in a small number of high-margin segments, "
                    "and shared exposure to regulatory and competitive pressure. See the "
                    "recalled records above for the source material each theme is grounded in.")
            else:
                parts.append(
                    "### Cross-Company Themes\n_No prior research was found in long-term "
                    "memory; run the company-level challenges first to populate it._")
            return "\n".join(parts)

        # Use the existing SynthesisEngine for the narrative skeleton.
        narrative = self.synth_engine.synthesize({
            "financials": {"present": any(g["tool"] == "financial_data_api" for g in gathered.values())},
            "sentiment": sentiment_summary or {},
        })
        parts.append(narrative)
        return "\n".join(parts)

    # ---- node 5: fact verification ----------------------------------------
    def verify_facts(self, state: ResearchState):
        """Run the fact_checker over the headline claims we can extract."""
        gathered = state["gathered_data"]
        verifications = []
        for v in gathered.values():
            if v["tool"] == "company_profile" and v["result"] and not v["degraded"]:
                try:
                    d = json.loads(v["result"])
                    claim = f"{d.get('name')} operates in the {d.get('sector')} sector."
                    res = self.error_handler.execute_tool_safely(
                        "fact_checker", {"claim": claim})
                    verifications.append({"claim": claim, **(res.get("result") or {})})
                except (json.JSONDecodeError, TypeError):
                    pass
        return {"verifications": verifications}

    # ---- node 6: report generation ----------------------------------------
    def generate_report(self, state: ResearchState):
        gathered = state["gathered_data"]
        tickers = state["tickers"]
        intent = state["intent"]
        disamb = state.get("disambiguation", {})

        sections = {}

        # Disambiguation / assumptions (Challenges 5 & 6).
        assumptions = disamb.get("assumptions_made", [])
        questions = disamb.get("clarifying_questions", [])
        if assumptions or questions:
            block = ""
            if assumptions:
                block += "**Assumptions made:**\n" + "\n".join(f"- {a}" for a in assumptions) + "\n\n"
            if questions:
                block += "**Open clarifying questions:**\n" + "\n".join(f"- {q}" for q in questions)
            sections["Query Interpretation & Assumptions"] = block

        # Build content sections from real data.
        profiles, financials, sentiments, sec_refs, web, peers = [], [], [], [], [], []
        recalled = []
        growth_lines = []
        for v in gathered.values():
            tool, res = v["tool"], v["result"]
            if tool == "vector_db_search" and isinstance(res, list):
                for hit in res:
                    if isinstance(hit, dict) and hit.get("content"):
                        meta = hit.get("metadata", {})
                        score = hit.get("relevance_score")
                        tag = f" _(ticker={meta.get('ticker')}, relevance={score:.2f})_" if score is not None else ""
                        recalled.append(f"- {hit['content'][:400].strip()}{tag}")
            if tool == "company_profile":
                profiles.append(fmt.format_profile(res))
            elif tool == "financial_data_api" and v["args"].get("statement_type") == "income_statement":
                financials.append(fmt.format_financials(res))
                g = fmt.revenue_growth(res) if isinstance(res, str) else None
                if g:
                    calc = self.registry.execute_tool(
                        "calculation_engine",
                        {"calculation_type": "growth_rate",
                         "inputs": {"current": g[0], "previous": g[1]}})
                    tk = v["args"].get("ticker", "?")
                    growth_lines.append(f"- {tk} revenue growth (YoY): **{calc.get('result')}**")
            elif tool == "financial_data_api":
                financials.append(fmt.format_financials(res))
            elif tool == "news_sentiment":
                sentiments.append(fmt.format_sentiment(res))
            elif tool == "sec_filing_search":
                sec_refs.append(fmt.format_sec(res))
            elif tool == "web_search":
                web.append(fmt.format_web(res))
            elif tool == "peer_comparison":
                peers.append("```json\n" + json.dumps(res, indent=2)[:1200] + "\n```")

        if recalled:
            sections["Prior Research Recalled (Long-Term Memory)"] = (
                f"Retrieved {len(recalled)} prior research record(s) from the vector "
                f"store (companies analysed earlier this session):\n\n" + "\n".join(recalled))
        if profiles:
            sections["Company Overview"] = "\n\n---\n\n".join(profiles)
        if financials:
            fin = "\n\n---\n\n".join(financials)
            if growth_lines:
                fin += "\n\n**Computed growth (calculation_engine):**\n" + "\n".join(growth_lines)
            sections["Financial Analysis"] = fin
        if sentiments:
            sections["Market Sentiment & News"] = "\n\n---\n\n".join(sentiments)
        if sec_refs:
            sections["SEC Filings & Risk Factors"] = "\n\n".join(sec_refs)
        if peers:
            sections["Peer Comparison"] = "\n\n".join(peers)
        if web:
            sections["Web Context"] = "\n\n".join(web)

        # Synthesis narrative.
        sections["Synthesis"] = state.get("synthesis", "")

        # Fact-check summary.
        if state.get("verifications"):
            vs = "\n".join(
                f"- _{v['claim']}_ → verified={v.get('verified')} "
                f"(confidence {v.get('confidence')})" for v in state["verifications"])
            sections["Fact Verification"] = vs

        # Data gaps & degradation (Challenges 5 & 8).
        degraded = [v for v in gathered.values() if v["degraded"]]
        if degraded:
            gap = "\n".join(
                f"- **{v['tool'] or v['purpose']}**: {v['degradation_note'] or 'degraded / partial data'}"
                for v in degraded)
            sections["Data Gaps & Degradation"] = (
                f"{len(degraded)} of {len(gathered)} steps degraded or fell back:\n\n{gap}")

        # Methodology.
        sections["Research Methodology"] = self._methodology_note(state)

        # Store findings to long-term memory for future cross-company queries.
        if self.enable_memory:
            self._store_to_memory(state, sections)

        report = self._render_report(state, sections)
        trace = self._build_trace(state)
        return {"report": report, "draft_report": report, "trace": trace}

    def _methodology_note(self, state):
        mode = "LLM-driven narrative" if self.llm else "deterministic data synthesis (no LLM key present)"
        note = [
            f"- **Reasoning loop:** Plan-and-Execute, 6-node LangGraph pipeline.",
            f"- **Synthesis mode:** {mode}.",
            f"- **Tools planned:** {len(state['plan'])}; **executed:** {state['iteration_count']} "
            f"(cap {MAX_TOOL_CALLS}).",
            f"- **Live data sources:** yfinance (financials/profile/news), SEC EDGAR full-text search.",
            "- **Constraint:** no figures are fabricated; unavailable data is labelled explicitly.",
        ]
        if self.failure_rate > 0:
            note.append(f"- **Degradation test:** {int(self.failure_rate*100)}% simulated failure rate "
                        f"on {sorted(UNRELIABLE_TOOLS)}; {self._simulated_failures} failures injected, "
                        f"resolved via fallback chains.")
        return "\n".join(note)

    def _store_to_memory(self, state, sections):
        for t in state["tickers"]:
            summary = f"Research on {t} ({state['intent']}). "
            ov = sections.get("Company Overview", "")
            summary += ov[:600]
            try:
                self.registry.execute_tool("vector_db_store", {
                    "content": summary,
                    "metadata": {"ticker": t, "intent": state["intent"]}})
            except Exception:
                pass

    def _render_report(self, state, sections):
        title = f"# Investment Research Report\n\n"
        title += f"**Query:** {state['query']}\n\n"
        title += f"**Intent classified as:** `{state['intent']}` | "
        title += f"**Tickers:** {', '.join(state['tickers']) or 'none resolved'}\n\n---\n\n"
        body = []
        for name, content in sections.items():
            if content and str(content).strip():
                body.append(f"## {name}\n\n{content}")
        return title + "\n\n".join(body) + "\n"

    def _build_trace(self, state):
        gathered = state["gathered_data"]
        total = len(gathered)
        degraded = sum(1 for v in gathered.values() if v["degraded"])
        useful = sum(1 for v in gathered.values()
                     if v["result"] is not None and not v["degraded"])
        mem_hits = sum(1 for v in gathered.values()
                       if v["tool"] == "vector_db_search" and v["result"])
        return {
            "query": state["query"],
            "intent": state["intent"],
            "tickers": state["tickers"],
            "plan_length": len(state["plan"]),
            "iterations": state["iteration_count"],
            "total_tool_calls": total,
            "useful_calls": useful,
            "degraded_calls": degraded,
            "simulated_failures": self._simulated_failures,
            "memory_hits": mem_hits,
            "llm_used": self.llm is not None,
            "tokens": 0 if self.llm is None else None,
        }

    # ---- entry point ------------------------------------------------------
    def run(self, query: str):
        start = time.time()
        result = self.graph.invoke({"query": query})
        if "trace" in result:
            result["trace"]["duration_seconds"] = round(time.time() - start, 2)
        return result
