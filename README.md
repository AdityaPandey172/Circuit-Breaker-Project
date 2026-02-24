# Circuit Breaker Implementation

A production-ready Circuit Breaker pattern implementation in Python with monitoring, metrics export, and HTTP client integration.

## What is a Circuit Breaker?

A Circuit Breaker is a design pattern that prevents cascading failures in distributed systems. It wraps calls to external services and monitors for failures. When failures exceed a threshold, the circuit "opens" and blocks further requests, giving the failing service time to recover.

**Think of it like an electrical circuit breaker in your home**: when too much current flows (too many failures), the breaker trips to prevent damage.

## Architecture

```
┌─────────────────────────────────────────┐
│         Circuit Breaker States          │
├─────────────────────────────────────────┤
│                                         │
│  CLOSED ──► requests pass through       │
│     │       (normal operation)          │
│     │                                   │
│     │ (failures exceed threshold)       │
│     ▼                                   │
│  OPEN ──► requests rejected             │
│     │     (fail fast, service recovery) │
│     │                                   │
│     │ (timeout expires)                 │
│     ▼                                   │
│  HALF-OPEN ──► limited requests         │
│     │          (testing recovery)       │
│     │                                   │
│     ├──► (success) ──► CLOSED           │
│     └──► (failure) ──► OPEN             │
│                                         │
└─────────────────────────────────────────┘
```

## Features

### Core Circuit Breaker
- Thread-safe implementation with proper locking
- Sliding window failure tracking (not just total count)
- Configurable thresholds and timeouts
- Three-state state machine (CLOSED → OPEN → HALF-OPEN)
- Automatic recovery attempts
- Detailed statistics and metrics

### Monitoring & Observability
- Real-time HTML dashboard (auto-refreshing)
- Prometheus-compatible metrics endpoint
- JSON stats export
- Health check endpoint
- Color-coded state indicators

### HTTP Client Integration
- Drop-in replacement for `requests` library
- Exponential backoff retry logic
- Per-service circuit breakers
- Fast-fail when circuit is open
- Smart error handling (4xx vs 5xx)

### Testing
- Comprehensive unit test suite (25+ tests)
- Thread safety tests
- Edge case coverage
- Mock-based testing for reliability

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd circuit-breaker

# Install dependencies (only for HTTP client)
pip install requests

# Run tests
python circuit_breaker_tests.py

# Run basic demo
python circuit_breaker.py

# Run monitoring demo (opens HTTP dashboard)
python circuit_breaker_monitoring.py

# Run HTTP client demo
python circuit_breaker_http.py
```

## Quick Start

### Basic Usage

```python
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig

# Configure circuit breaker
config = CircuitBreakerConfig(
    failure_threshold=5,    # Open after 5 failures
    success_threshold=2,    # Need 2 successes to close
    timeout=60.0,           # Wait 60s before retry
    window_size=10          # Track last 10 calls
)

cb = CircuitBreaker(config)

# Wrap any function call
try:
    result = cb.call(my_api_function, arg1, arg2)
    print(f"Success: {result}")
except CircuitBreakerOpenException:
    print("Service unavailable, using fallback")
    result = get_cached_data()
```

### HTTP Client Usage

```python
from circuit_breaker_http import ResilientHTTPClient
from circuit_breaker import CircuitBreakerConfig

# Create HTTP client
client = ResilientHTTPClient()

# Register services
client.register_service(
    service_name='payment_api',
    base_url='https://api.stripe.com',
    config=CircuitBreakerConfig(
        failure_threshold=3,
        timeout=30.0
    )
)

# Make protected HTTP calls
try:
    response = client.get('payment_api', '/v1/charges')
    print(response.json())
except CircuitBreakerOpenException:
    print("Payment service unavailable")
```

### With Monitoring Dashboard

```python
from circuit_breaker_monitoring import MonitoredCircuitBreaker

cb = MonitoredCircuitBreaker(
    service_name="my_api",
    monitoring_port=8080
)

cb.start_monitoring()
# Now open http://localhost:8080 in your browser!

# Use circuit breaker normally
result = cb.call(my_function)
```

## 🧪 Running Tests

```bash
# Run all tests with verbose output
python circuit_breaker_tests.py

# Expected output:
# test_initial_state_is_closed ... ok
# test_successful_call_passes_through ... ok
# test_circuit_opens_after_threshold_failures ... ok
# ... (25+ tests)
#
# Tests run: 25
# Failures: 0
# Success rate: 100.0%
```

## Monitoring Endpoints

When using `MonitoredCircuitBreaker`, the following endpoints are available:

| Endpoint | Description | Format |
|----------|-------------|--------|
| `/` | Interactive HTML dashboard | HTML |
| `/metrics` | Prometheus-compatible metrics | Text |
| `/stats` | Detailed statistics | JSON |
| `/health` | Health check (200=healthy, 503=circuit open) | JSON |

### Example Prometheus Metrics

```
# HELP circuit_breaker_state Current state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)
# TYPE circuit_breaker_state gauge
circuit_breaker_state{service="payment_api"} 0

# HELP circuit_breaker_requests_total Total number of requests
# TYPE circuit_breaker_requests_total counter
circuit_breaker_requests_total{service="payment_api"} 1523
```

## Technical Deep Dive

### Why This Implementation Stands Out

#### 1. Sliding Window vs Fixed Window
Most naive implementations count total failures. This implementation uses a **sliding window** (implemented with Python's `deque`) that only considers recent failures. Old failures automatically evict.

**Benefit**: More accurate representation of current service health.

#### 2. Thread Safety
Uses `threading.Lock()` but releases it before making the actual function call.

**Why**: Prevents blocking other threads during slow I/O operations while still maintaining thread-safe state management.

#### 3. Smart Lock Usage
```python
with self.lock:
    # Quick state check (microseconds)
    check_state()

# Actual function call (seconds) - lock released!
result = func()

with self.lock:
    # Quick state update (microseconds)
    update_stats()
```

#### 4. Half-Open State Conservatism
Requires multiple successes to close, but single failure reopens immediately.

**Why**: Prevents premature closure due to false positives.

### Key Design Decisions

| Decision | Alternative | Why Chosen |
|----------|-------------|------------|
| `deque` with `maxlen` | Manual list management | O(1) operations, automatic eviction |
| Per-service breakers | Global breaker | Services have different SLAs |
| Fail-fast when open | Queue requests | Prevents resource exhaustion |
| Thread locks | Lock-free atomic ops | Simpler, Python GIL makes this safe |


### For Technical Discussions

1. **"How does the sliding window work?"**
   - Uses `collections.deque` with `maxlen` parameter
   - Automatically evicts oldest entry when full
   - O(1) append and count operations
   - Memory-bounded (won't grow infinitely)

2. **"Why three states instead of two?"**
   - HALF-OPEN prevents thrashing (rapid open/close cycles)
   - Allows conservative recovery testing
   - One fluke success won't immediately close circuit

3. **"How would you handle distributed systems?"**
   - Store state in Redis with TTL
   - Use distributed locks (Redis SETNX)
   - Aggregate metrics across instances
   - Consider using service mesh (Istio, Linkerd)

4. **"What about false positives?"**
   - Tunable thresholds per service
   - Distinguish client errors (4xx) from server errors (5xx)
   - Monitor state change frequency
   - Manual override capability for emergencies

5. **"Performance impact?"**
   - State check: O(1) with lock
   - Window operations: O(1) with deque
   - Lock contention: minimal (released during I/O)
   - Overhead: <1ms per request

### For System Design

1. **Rate Limiter vs Circuit Breaker**
   - Rate Limiter: Controls outgoing traffic volume
   - Circuit Breaker: Responds to downstream health
   - Often used together (rate limit → circuit breaker → service)

2. **When to Use Circuit Breakers**
   - ✅ External API calls
   - ✅ Database connections
   - ✅ Microservice communication
   - ❌ In-memory operations
   - ❌ Highly variable latency services

3. **Fallback Strategies**
   ```python
   try:
       result = cb.call(api_function)
   except CircuitBreakerOpenException:
       result = cache.get(key)  # Stale data
       # OR
       result = default_value   # Degraded experience
       # OR
       raise ServiceUnavailable("Try again later")
   ```

## Metrics to Monitor in Production

1. **State Distribution**
   - % of time in each state
   - Frequent OPEN states = upstream issues

2. **State Change Frequency**
   - Rapid transitions = threshold too sensitive
   - No transitions = might not be working

3. **Rejection Rate**
   - High rejections = adjust timeout or threshold
   - Shows how much load you're shedding

4. **Recovery Time**
   - Time from OPEN → CLOSED
   - Indicates downstream recovery speed

## Related Patterns

- **Bulkhead**: Isolate resources (thread pools) per service
- **Retry**: Attempt failed operations again (with backoff)
- **Timeout**: Prevent indefinite waits
- **Fallback**: Provide alternative responses

This implementation combines Circuit Breaker + Retry for maximum resilience.

## Further Reading

- [Martin Fowler's Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Netflix Hystrix](https://github.com/Netflix/Hystrix) (inspiration)
- [Release It! by Michael Nygard](https://pragprog.com/titles/mnee2/) (Chapter on stability patterns)

## Contributing

This is a portfolio/learning project. Feel free to:
- Add more comprehensive tests
- Implement adaptive thresholds (ML-based)
- Add integration with APM tools (Datadog, New Relic)
- Create async/await version


## 🎯 Project Status

This implementation demonstrates:
- ✅ Production-ready code quality
- ✅ Comprehensive testing
- ✅ Real-world integration
- ✅ Monitoring and observability
- ✅ Clear documentation
