import pytest
from agent.circuit_breaker import CircuitBreaker

def test_circuit_breaker_stress():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    # Simulate repeated failures
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is False
    assert cb.state == "OPEN"
