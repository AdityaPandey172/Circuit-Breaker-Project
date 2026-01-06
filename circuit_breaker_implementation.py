import time
import threading
from enum import Enum
from collections import deque
from typing import Callable, Any, Optional
from dataclasses import dataclass, field


class CircuitState(Enum):
    """Three possible states of the circuit breaker"""
    CLOSED = "CLOSED"      # Normal operation, requests pass through
    OPEN = "OPEN"          # Circuit is broken, fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 2  # Successes needed in half-open to close
    timeout: float = 60.0  # Seconds before attempting recovery (open -> half-open)
    window_size: int = 10  # Number of recent calls to track
    
    
@dataclass
class CircuitStats:
    """Statistics for monitoring circuit health"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0  # Rejected due to open circuit
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: Optional[float] = None


class CircuitBreakerOpenException(Exception):
    """Raised when circuit is open and request is rejected"""
    pass


class CircuitBreaker:
    """
    A Circuit Breaker that monitors service health and prevents cascading failures.
    
    Key Concepts:
    - Tracks recent call results in a sliding window
    - Opens circuit when failure rate exceeds threshold
    - Automatically attempts recovery after timeout
    - Provides detailed health metrics
    """
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        
        # Thread-safe operations
        self.lock = threading.Lock()
        
        # Sliding window of recent call results (True = success, False = failure)
        self.call_history = deque(maxlen=self.config.window_size)
        
        # Track when circuit opened (for timeout calculation)
        self.opened_at: Optional[float] = None
        
        # In half-open state, count consecutive successes
        self.half_open_successes = 0
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: The function to call (typically an API call or service method)
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Result from the function
            
        Raises:
            CircuitBreakerOpenException: If circuit is open
            Exception: Any exception raised by the wrapped function
        """
        with self.lock:
            self.stats.total_requests += 1
            
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed to transition to half-open
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    self.stats.rejected_requests += 1
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker is OPEN. Service unavailable. "
                        f"Retry after {self._time_until_retry():.1f}s"
                    )
        
        # Execute the actual function call (outside lock to avoid blocking)
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            self.stats.successful_requests += 1
            self.call_history.append(True)
            
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_successes += 1
                
                # If enough successes in half-open, close the circuit
                if self.half_open_successes >= self.config.success_threshold:
                    self._transition_to_closed()
    
    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.stats.failed_requests += 1
            self.stats.last_failure_time = time.time()
            self.call_history.append(False)
            
            # In half-open, single failure reopens circuit immediately
            if self.state == CircuitState.HALF_OPEN:
                self._transition_to_open()
            
            # In closed, check if we've exceeded failure threshold
            elif self.state == CircuitState.CLOSED:
                if self._failure_threshold_exceeded():
                    self._transition_to_open()
    
    def _failure_threshold_exceeded(self) -> bool:
        """Check if recent failures exceed threshold"""
        if len(self.call_history) < self.config.failure_threshold:
            return False
        
        # Count recent failures
        recent_failures = sum(1 for success in self.call_history if not success)
        return recent_failures >= self.config.failure_threshold
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        if self.opened_at is None:
            return False
        return (time.time() - self.opened_at) >= self.config.timeout
    
    def _time_until_retry(self) -> float:
        """Calculate seconds until retry attempt"""
        if self.opened_at is None:
            return 0.0
        elapsed = time.time() - self.opened_at
        return max(0.0, self.config.timeout - elapsed)
    
    def _transition_to_open(self):
        """Open the circuit (service is down)"""
        self.state = CircuitState.OPEN
        self.opened_at = time.time()
        self.stats.state_changes += 1
        self.stats.last_state_change = time.time()
        print(f"⚠️  Circuit OPENED at {time.strftime('%H:%M:%S')}")
    
    def _transition_to_half_open(self):
        """Enter half-open state (testing recovery)"""
        self.state = CircuitState.HALF_OPEN
        self.half_open_successes = 0
        self.stats.state_changes += 1
        self.stats.last_state_change = time.time()
        print(f"🔄 Circuit HALF-OPEN at {time.strftime('%H:%M:%S')}")
    
    def _transition_to_closed(self):
        """Close the circuit (service recovered)"""
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.half_open_successes = 0
        self.call_history.clear()  # Reset history on recovery
        self.stats.state_changes += 1
        self.stats.last_state_change = time.time()
        print(f"✅ Circuit CLOSED at {time.strftime('%H:%M:%S')}")
    
    def get_stats(self) -> dict:
        """Get current circuit breaker statistics"""
        with self.lock:
            failure_rate = 0.0
            if self.stats.total_requests > 0:
                failure_rate = (self.stats.failed_requests / 
                              self.stats.total_requests) * 100
            
            return {
                "state": self.state.value,
                "total_requests": self.stats.total_requests,
                "successful": self.stats.successful_requests,
                "failed": self.stats.failed_requests,
                "rejected": self.stats.rejected_requests,
                "failure_rate": f"{failure_rate:.1f}%",
                "state_changes": self.stats.state_changes,
                "time_until_retry": (self._time_until_retry() 
                                   if self.state == CircuitState.OPEN else 0),
            }
    
    def reset(self):
        """Manually reset circuit breaker (for testing/admin)"""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.opened_at = None
            self.half_open_successes = 0
            self.call_history.clear()
            print("🔧 Circuit manually reset")


# ============================================================================
# DEMO: Simulating a Flaky API Service
# ============================================================================

def simulate_flaky_api(fail_probability: float = 0.0) -> str:
    """
    Simulates an API call that might fail.
    
    Args:
        fail_probability: Chance of failure (0.0 to 1.0)
    """
    import random
    time.sleep(0.1)  # Simulate network delay
    
    if random.random() < fail_probability:
        raise Exception("Service unavailable")
    return "Success: Data retrieved"


def demo_circuit_breaker():
    """Demonstrate circuit breaker in action"""
    
    # Configure circuit breaker
    config = CircuitBreakerConfig(
        failure_threshold=3,    # Open after 3 failures
        success_threshold=2,    # Need 2 successes to close
        timeout=5.0,            # Wait 5 seconds before retry
        window_size=5           # Track last 5 calls
    )
    
    cb = CircuitBreaker(config)
    
    print("=" * 70)
    print("CIRCUIT BREAKER DEMO")
    print("=" * 70)
    
    # Phase 1: Normal operation (service healthy)
    print("\n📊 Phase 1: Service is healthy (0% failure rate)")
    for i in range(5):
        try:
            result = cb.call(simulate_flaky_api, fail_probability=0.0)
            print(f"  Request {i+1}: {result}")
        except Exception as e:
            print(f"  Request {i+1}: Failed - {e}")
        time.sleep(0.2)
    
    print(f"\n📈 Stats: {cb.get_stats()}")
    
    # Phase 2: Service degradation (circuit should open)
    print("\n📊 Phase 2: Service degrading (80% failure rate)")
    for i in range(8):
        try:
            result = cb.call(simulate_flaky_api, fail_probability=0.8)
            print(f"  Request {i+1}: {result}")
        except CircuitBreakerOpenException as e:
            print(f"  Request {i+1}: REJECTED - {e}")
        except Exception as e:
            print(f"  Request {i+1}: Failed - {e}")
        time.sleep(0.2)
    
    print(f"\n📈 Stats: {cb.get_stats()}")
    
    # Phase 3: Wait for timeout
    print(f"\n⏳ Phase 3: Waiting {config.timeout} seconds for timeout...")
    time.sleep(config.timeout + 0.5)
    
    # Phase 4: Recovery attempt (service healthy again)
    print("\n📊 Phase 4: Service recovered, testing with half-open state")
    for i in range(5):
        try:
            result = cb.call(simulate_flaky_api, fail_probability=0.0)
            print(f"  Request {i+1}: {result}")
        except CircuitBreakerOpenException as e:
            print(f"  Request {i+1}: REJECTED - {e}")
        except Exception as e:
            print(f"  Request {i+1}: Failed - {e}")
        time.sleep(0.2)
    
    print(f"\n📈 Final Stats: {cb.get_stats()}")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo_circuit_breaker()