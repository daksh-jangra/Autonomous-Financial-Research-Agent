from agent.circuit_breaker import CircuitBreaker
from agent.fallback_chains import FallbackManager
from tools.tool_registry import ToolRegistry
import logging

class ErrorHandler:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.fallback_manager = FallbackManager(registry)
        
        # Instantiate a circuit breaker for each external tool
        self.circuit_breakers = {
            name: CircuitBreaker() for name in registry.functions.keys()
        }

    def execute_tool_safely(self, tool_name: str, kwargs: dict) -> dict:
        """
        Executes a tool incorporating circuit breakers, retries, and fallbacks.
        """
        cb = self.circuit_breakers.get(tool_name)
        
        if cb and not cb.can_execute():
            logging.warning(f"Circuit breaker OPEN for {tool_name}. Skipping directly to fallback.")
            # Trigger fallback immediately
            return self.fallback_manager.execute_with_fallback(f"simulate_failure_{tool_name}", kwargs)
            
        # Try executing with fallback manager (which handles its own internal try/catch)
        response = self.fallback_manager.execute_with_fallback(tool_name, kwargs)
        
        if response["degraded"] and response["result"] is None:
            # Absolute failure
            if cb: cb.record_failure()
        else:
            if cb: cb.record_success()
            
        return response
