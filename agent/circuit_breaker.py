import time
import logging

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logging.warning("Circuit breaker OPENED due to repeated failures.")

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        
        if self.state == "OPEN":
            # Check if timeout has passed to move to HALF_OPEN
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
            
        # If HALF_OPEN, we allow execution to test if the service is back
        return True
