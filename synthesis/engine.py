from .conflict_resolver import resolve_conflict
from .narrative import create_narrative_thread

class SynthesisEngine:
    def __init__(self, llm=None):
        self.llm = llm

    def synthesize(self, observations: dict) -> str:
        """
        Synthesizes multiple observations into a cohesive report draft.
        Handles conflict resolution and narrative threading.
        """
        # Extract specific data types for threading
        financials = observations.get("financials", {})
        sentiment = observations.get("sentiment", {})
        transcripts = observations.get("transcripts", "")
        
        # Weave narrative
        narrative = create_narrative_thread(financials, sentiment, transcripts)
        
        # In a full implementation, we would extract all overlapping claims and run resolve_conflict()
        # For the architecture stub, we just return the narrative thread combined with all raw data summaries
        
        full_synthesis = f"{narrative}\n\n### Raw Data Synthesis\n"
        for step, obs in observations.items():
            if isinstance(obs, str):
                full_synthesis += f"- {obs[:100]}...\n"
            else:
                full_synthesis += f"- Data collected for {step}\n"
                
        return full_synthesis
