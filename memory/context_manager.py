import tiktoken
import logging

class ContextManager:
    def __init__(self, max_tokens: int = 100000, model_name: str = "gpt-4o"):
        self.max_tokens = max_tokens
        self.encoder = tiktoken.encoding_for_model(model_name)
        
    def count_tokens(self, text: str) -> int:
        """Counts tokens in a string using tiktoken."""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            logging.error(f"Token counting error: {e}")
            return len(text) // 4  # Rough heuristic fallback

    def compress_context(self, observations: dict, llm=None) -> dict:
        """
        Compresses observations if they exceed token limits.
        A real implementation would use the LLM to summarize older steps while keeping numerical data.
        """
        compressed_obs = {}
        total_tokens = 0
        
        # Sort by step number (assuming keys like 'step_0', 'step_1')
        sorted_steps = sorted(observations.keys(), reverse=True) # newest first
        
        for step in sorted_steps:
            content = str(observations[step])
            step_tokens = self.count_tokens(content)
            
            if total_tokens + step_tokens > self.max_tokens * 0.8:
                # Approaching limit, summarize or truncate
                if llm:
                    # In a full implementation, call LLM to summarize `content`
                    compressed_obs[step] = f"[SUMMARIZED] {content[:500]}..."
                else:
                    compressed_obs[step] = f"[TRUNCATED DUE TO CONTEXT LIMIT] {content[:500]}..."
                total_tokens += self.count_tokens(compressed_obs[step])
            else:
                compressed_obs[step] = observations[step]
                total_tokens += step_tokens
                
        return compressed_obs
