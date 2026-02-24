# **Circuit Breaker \- Complete Documentation**

## **Table of Contents**

1. [Overview](#overview)  
2. [Architecture](#architecture)  
3. [Installation & Setup](#installation-&-setup)  
4. [Quick Start Guide](#quick-start-guide)  
5. [API Reference](#api-reference)  
6. [Configuration Guide](#configuration-guide)  
7. [Monitoring & Observability](#monitoring-&-observability)  
8. [Testing Guide](#testing-guide)  
9. [Performance Benchmarks](#performance-benchmarks)  
10. [Troubleshooting](#troubleshooting)  
11. [Best Practices](#best-practices)  
12. [Advanced Usage](#advanced-usage)

---

## **Overview** {#overview}

### **What Problem Does This Solve?**

In distributed systems, when a service becomes slow or unresponsive, continuing to send requests can:

* Exhaust connection pools  
* Consume threads waiting for timeouts  
* Cascade failures to upstream services  
* Degrade overall system performance

**Circuit Breaker** solves this by:

1. Detecting when a service is failing  
2. Stopping requests to that service (fail-fast)  
3. Giving the service time to recover  
4. Automatically retrying when appropriate

### **Real-World Example**

Without Circuit Breaker:  
User Request → API Gateway → Payment Service (down, 30s timeout)  
                           → Payment Service (down, 30s timeout)  
                           → Payment Service (down, 30s timeout)  
Result: 90 seconds wasted, 3 threads blocked, user frustrated

With Circuit Breaker:  
User Request → API Gateway → Circuit Breaker → OPEN (fails in \<1ms)  
Result: Instant response, no wasted resources, fallback used

### **Key Features**

|  |  |  |
| ----- | ----- | ----- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

| Feature | Description | Benefit |
| ----- | ----- | ----- |
| **Fail-Fast** | Reject requests when circuit is open | Prevent resource exhaustion |
| **Auto-Recovery** | Automatically test service health | No manual intervention needed |
| **Thread-Safe** | Safe for concurrent access | Works in multi-threaded apps |
| **Sliding Window** | Only recent failures matter | Accurate current health status |
| **Monitoring** | Real-time dashboard and metrics | Full observability |
| **Configurable** | Per-service settings | Tune for different SLAs |

## 

## 

## 

## 

## 

## 

## 

## 

## 

## 

---

## **Architecture** {#architecture}

![][image1]

### 

### **![][image2]**

![][image3]

---

## **Installation & Setup** {#installation-&-setup}

### **Prerequisites**

\# Required  
Python 3.7+

\# Optional (for HTTP client only)  
pip install requests

### **Project Structure**

circuit-breaker/  
├── circuit\_breaker.py              \# Core implementation  
├── circuit\_breaker\_tests.py        \# Unit tests  
├── circuit\_breaker\_monitoring.py   \# Monitoring & metrics  
├── circuit\_breaker\_http.py         \# HTTP client integration  
├── README.md                        \# Project overview  
├── DOCUMENTATION.md                 \# This file  
├── benchmarks.py                    \# Performance tests  
└── examples/                        \# Usage examples  
    ├── basic\_usage.py  
    ├── http\_integration.py  
    └── microservices\_demo.py

### **Quick Installation**

\# Clone repository  
git clone https://github.com/yourusername/circuit-breaker.git  
cd circuit-breaker

\# Verify installation  
python circuit\_breaker.py

\# Run tests  
python circuit\_breaker\_tests.py

\# Expected output:  
\# Ran 25 tests in 2.345s  
\# OK

---

## **Quick Start Guide** {#quick-start-guide}

### **Example 1: Protect a Flaky Function**

from circuit\_breaker import CircuitBreaker, CircuitBreakerConfig  
import random

\# Create circuit breaker  
config \= CircuitBreakerConfig(  
    failure\_threshold=3,  \# Open after 3 failures  
    success\_threshold=2,  \# Need 2 successes to close  
    timeout=10.0,         \# Wait 10 seconds before retry  
    window\_size=5         \# Track last 5 calls  
)  
cb \= CircuitBreaker(config)

\# Your flaky function  
def call\_external\_api():  
    if random.random() \< 0.3:  \# 30% failure rate  
        raise Exception("Service unavailable")  
    return {"status": "success", "data": "..."}

\# Use circuit breaker  
for i in range(10):  
    try:  
        result \= cb.call(call\_external\_api)  
        print(f"✅ Call {i+1}: {result\['status'\]}")  
    except Exception as e:  
        print(f"❌ Call {i+1}: {e}")  
      
    \# Check stats  
    stats \= cb.get\_stats()  
    print(f"   State: {stats\['state'\]}, "  
          f"Failures: {stats\['failed'\]}/{stats\['total\_requests'\]}")

### **Example 2: HTTP API with Fallback**

from circuit\_breaker\_http import ResilientHTTPClient  
from circuit\_breaker import CircuitBreakerOpenException  
import json

\# Setup  
client \= ResilientHTTPClient()  
client.register\_service(  
    service\_name='users\_api',  
    base\_url='https://api.example.com'  
)

\# Cache for fallback  
cache \= {}

def get\_user(user\_id):  
    """Get user with circuit breaker protection and cache fallback"""  
    try:  
        \# Try real API  
        response \= client.get('users\_api', f'/users/{user\_id}')  
        user\_data \= response.json()  
          
        \# Update cache  
        cache\[user\_id\] \= user\_data  
        return user\_data  
          
    except CircuitBreakerOpenException:  
        \# Circuit is open \- use cached data  
        if user\_id in cache:  
            print(f"⚠️  Using cached data for user {user\_id}")  
            return cache\[user\_id\]  
        else:  
            raise Exception("Service unavailable and no cache")

\# Usage  
user \= get\_user(123)  
print(f"User: {user\['name'\]}")

### **Example 3: Multiple Services with Monitoring**

from circuit\_breaker\_monitoring import MonitoredCircuitBreaker  
from circuit\_breaker import CircuitBreakerConfig

\# Create separate breakers for different services  
payment\_cb \= MonitoredCircuitBreaker(  
    config=CircuitBreakerConfig(  
        failure\_threshold=2,  \# Strict for payments  
        timeout=60.0  
    ),  
    service\_name="payment\_service",  
    monitoring\_port=8080  
)

analytics\_cb \= MonitoredCircuitBreaker(  
    config=CircuitBreakerConfig(  
        failure\_threshold=10,  \# Lenient for analytics  
        timeout=30.0  
    ),  
    service\_name="analytics\_service",  
    monitoring\_port=8081  
)

\# Start monitoring  
payment\_cb.start\_monitoring()  
analytics\_cb.start\_monitoring()

print("Dashboards:")  
print("  Payments:  http://localhost:8080")  
print("  Analytics: http://localhost:8081")

\# Use circuit breakers...

---

## **API Reference** {#api-reference}

### **CircuitBreakerConfig**

Configuration object for circuit breaker behavior.

@dataclass  
class CircuitBreakerConfig:  
    failure\_threshold: int \= 5  
    success\_threshold: int \= 2  
    timeout: float \= 60.0  
    window\_size: int \= 10

#### **Parameters**

| Parameter | Type | Default | Description |
| ----- | :---: | :---: | ----- |
| `failure_threshold` | int | 5 | Number of failures to trigger circuit opening |
| `success_threshold` | int | 2 | Number of successes needed to close circuit (from HALF\_OPEN) |
| `timeout` | float | 60.0 | Seconds to wait before attempting recovery (OPEN → HALF\_OPEN) |
| `window_size` | int | 10 | Number of recent calls to track in sliding window |

#### 

#### **Example**

\# Strict configuration (opens quickly)  
strict\_config \= CircuitBreakerConfig(  
    failure\_threshold=2,  
    success\_threshold=3,  
    timeout=120.0,  
    window\_size=5  
)

|  |  |  |  |
| ----- | ----- | ----- | ----- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

\# Lenient configuration (tolerates more failures)  
lenient\_config \= CircuitBreakerConfig(  
    failure\_threshold=10,  
    success\_threshold=2,  
    timeout=30.0,  
    window\_size=20  
)

---

### **CircuitBreaker**

Main circuit breaker class.

#### **Constructor**

CircuitBreaker(config: CircuitBreakerConfig \= None)

**Parameters:**

* `config` (optional): Configuration object. Uses defaults if not provided.

**Example:**

cb \= CircuitBreaker()  \# Use defaults  
\# OR  
cb \= CircuitBreaker(my\_config)  \# Use custom config

---

#### **Methods**

##### **`call(func, *args, **kwargs)`**

Execute a function through the circuit breaker.

**Parameters:**

* `func`: Callable to execute  
* `*args`: Positional arguments for the function  
* `**kwargs`: Keyword arguments for the function

**Returns:**

* Whatever `func` returns

**Raises:**

* `CircuitBreakerOpenException`: If circuit is open and request is rejected  
* Any exception raised by `func`

**Example:**

\# Simple function  
result \= cb.call(my\_function)

\# With arguments  
result \= cb.call(my\_function, arg1, arg2, key=value)

\# Lambda  
result \= cb.call(lambda x: x \* 2, 5\)  \# Returns 10

**Thread Safety:**  Safe to call from multiple threads

---

##### **`get_stats()`**

Get current circuit breaker statistics.

**Returns:** Dictionary with keys:

* `state` (str): Current state ("CLOSED", "OPEN", "HALF\_OPEN")  
* `total_requests` (int): Total calls made  
* `successful` (int): Successful calls  
* `failed` (int): Failed calls  
* `rejected` (int): Rejected calls (circuit was open)  
* `failure_rate` (str): Percentage of failures (e.g., "15.5%")  
* `state_changes` (int): Number of state transitions  
* `time_until_retry` (float): Seconds until retry (0 if not open)

**Example:**

stats \= cb.get\_stats()  
print(f"State: {stats\['state'\]}")  
print(f"Success rate: {100 \- float(stats\['failure\_rate'\].rstrip('%'))}%")

if stats\['state'\] \== 'OPEN':  
    print(f"Retry in {stats\['time\_until\_retry'\]:.0f} seconds")

---

##### **`reset()`**

Manually reset circuit breaker to CLOSED state.

**Use cases:**

* Testing  
* Manual recovery after maintenance  
* Emergency override

**Example:**

\# Force reset  
cb.reset()  
print(cb.get\_stats()\['state'\])  \# "CLOSED"

 **Warning:** Use sparingly. Let automatic recovery work in production.

---

### **CircuitBreakerOpenException**

Exception raised when the circuit is open.

try:  
    result \= cb.call(api\_function)  
except CircuitBreakerOpenException as e:  
    \# Circuit is open \- use fallback  
    print(f"Circuit open: {e}")  
    result \= get\_cached\_data()

---

### **CircuitBreakerHTTPClient**

HTTP client wrapper with circuit breaker protection.

#### **Methods**

##### **`register_service(service_name, base_url, config=None)`**

Register a downstream service.

**Parameters:**

* `service_name` (str): Unique identifier  
* `base_url` (str): Base URL (e.g., "https://api.example.com")  
* `config` (optional): Custom CircuitBreakerConfig

**Example:**

client \= CircuitBreakerHTTPClient()  
client.register\_service(  
    'payment\_api',  
    'https://api.stripe.com',  
    CircuitBreakerConfig(failure\_threshold=3)  
)

---

##### **`get(service_name, path, timeout=5.0, **kwargs)`**

Make GET request.

**Parameters:**

* `service_name` (str): Registered service name  
* `path` (str): API path (e.g., "/users/123")  
* `timeout` (float): Request timeout in seconds  
* `**kwargs`: Additional arguments for `requests.get()`

**Returns:** `requests.Response` object

**Example:**

response \= client.get('payment\_api', '/charges', timeout=10.0)  
data \= response.json()

Similar methods: `post()`, `put()`, `delete()`

---

##### **`get_service_stats(service_name)`**

Get stats for specific service.

**Returns:** Dictionary with circuit breaker statistics

**Example:**

stats \= client.get\_service\_stats('payment\_api')  
print(f"Payment API state: {stats\['state'\]}")

---

### **MonitoredCircuitBreaker**

Circuit breaker with built-in HTTP monitoring.

#### **Constructor**

MonitoredCircuitBreaker(  
    config: CircuitBreakerConfig \= None,  
    service\_name: str \= "api",  
    monitoring\_port: int \= 8080  
)

#### **Methods**

##### **`start_monitoring()`**

Start HTTP server for monitoring.

**Endpoints created:**

* `http://localhost:{port}/` \- HTML dashboard  
* `http://localhost:{port}/metrics` \- Prometheus metrics  
* `http://localhost:{port}/stats` \- JSON statistics  
* `http://localhost:{port}/health` \- Health check

**Example:**

cb \= MonitoredCircuitBreaker(monitoring\_port=8080)  
cb.start\_monitoring()  
\# Now visit http://localhost:8080 in browser

##### **`stop_monitoring()`**

Stop HTTP server.

---

## **Configuration Guide** {#configuration-guide}

### **Choosing the Right Thresholds**

| Service Type | failure\_threshold | success\_threshold | timeout | window\_size |
| ----- | :---: | :---: | :---: | :---: |
| **Critical** (payments, auth) | 2 \-3  | 3 \- 5 | 60 \- 120s | 5 \- 10 |
| **Important** (user data, orders) | 5 | 2 \- 3 | 30 \- 60s | 10 |
| **Nice-to-have** (analytics, recommendations) | 10 \- 20 | 2 | 15 \- 30s | 20 |
| **Best-effort** (tracking, logs) | 20+ | 2 | 10 \-20s | 30 |

|  |  |  |  |  |
| ----- | ----- | ----- | ----- | ----- |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

### **Configuration Examples**

#### **High Availability Service**

\# Opens quickly, recovers conservatively  
ha\_config \= CircuitBreakerConfig(  
    failure\_threshold=2,  
    success\_threshold=5,  
    timeout=120.0,  
    window\_size=5  
)

#### **Load Shedding for Non-Critical Service**

\# Tolerates many failures, recovers quickly  
shed\_config \= CircuitBreakerConfig(  
    failure\_threshold=20,  
    success\_threshold=2,  
    timeout=15.0,  
    window\_size=30  
)

#### **Testing Configuration**

\# Fast cycling for demos  
test\_config \= CircuitBreakerConfig(  
    failure\_threshold=2,  
    success\_threshold=1,  
    timeout=5.0,  
    window\_size=3  
)

### **Tuning Guidelines**

1. **Start Conservative**

   * Low `failure_threshold` (3-5)  
   * High `success_threshold` (3-5)  
   * Long `timeout` (60s)  
2. **Monitor and Adjust**

   * Too many false positives? → Increase `failure_threshold`  
   * Circuit opens but service is fine? → Increase `window_size`  
   * Takes too long to recover? → Decrease `timeout`  
   * Opens too often? → Increase both thresholds  
3. **Match Service SLA**

   * 99.99% uptime service → strict thresholds  
   * 95% uptime service → lenient thresholds

---

## **Monitoring & Observability** {#monitoring-&-observability}

### **Dashboard Overview**

Access via `http://localhost:{port}/` when using `MonitoredCircuitBreaker`.

**Features:**

* Auto-refreshes every 2 seconds  
* Color-coded state (🟢 CLOSED, 🟡 HALF\_OPEN, 🔴 OPEN)  
* Real-time metrics  
* Countdown timer when circuit is open

### **Prometheus Metrics**

Access via `http://localhost:{port}/metrics`

**Available Metrics:**

\# State (0=CLOSED, 1=HALF\_OPEN, 2=OPEN)  
circuit\_breaker\_state{service="api"} 0

\# Total requests  
circuit\_breaker\_requests\_total{service="api"} 1523

\# Successful requests  
circuit\_breaker\_requests\_successful{service="api"} 1450

\# Failed requests  
circuit\_breaker\_requests\_failed{service="api"} 50

\# Rejected requests (circuit open)  
circuit\_breaker\_requests\_rejected{service="api"} 23

\# Failure rate percentage  
circuit\_breaker\_failure\_rate\_percent{service="api"} 3.28

\# State transitions count  
circuit\_breaker\_state\_changes\_total{service="api"} 4

### **Integration with Monitoring Tools**

#### **Grafana Dashboard**

{  
  "dashboard": {  
    "title": "Circuit Breaker Monitoring",  
    "panels": \[  
      {  
        "title": "Circuit State",  
        "targets": \[  
          {  
            "expr": "circuit\_breaker\_state"  
          }  
        \]  
      },  
      {  
        "title": "Request Rate",  
        "targets": \[  
          {  
            "expr": "rate(circuit\_breaker\_requests\_total\[5m\])"  
          }  
        \]  
      },  
      {  
        "title": "Failure Rate",  
        "targets": \[  
          {  
            "expr": "circuit\_breaker\_failure\_rate\_percent"  
          }  
        \]  
      }  
    \]  
  }  
}

#### **Prometheus Alerting Rules**

groups:  
  \- name: circuit\_breaker\_alerts  
    rules:  
      \- alert: CircuitBreakerOpen  
        expr: circuit\_breaker\_state \== 2  
        for: 5m  
        annotations:  
          summary: "Circuit breaker is open for {{ $labels.service }}"  
            
      \- alert: HighFailureRate  
        expr: circuit\_breaker\_failure\_rate\_percent \> 10  
        for: 2m  
        annotations:  
          summary: "High failure rate for {{ $labels.service }}"

---

## **Testing Guide** {#testing-guide}

### **Running Tests**

\# Run all tests  
python circuit\_breaker\_tests.py

\# Verbose output  
python circuit\_breaker\_tests.py \-v

\# Run specific test class  
python \-m unittest circuit\_breaker\_tests.TestCircuitBreakerBasics

\# Run single test  
python \-m unittest circuit\_breaker\_tests.TestCircuitBreakerBasics.test\_circuit\_opens\_after\_threshold\_failures

### **Test Coverage**

Test Suite Coverage:  
├── Basic Functionality (8 tests)  
│   ├── Initial state  
│   ├── Successful calls  
│   ├── Failed calls  
│   ├── Circuit opening  
│   ├── Request rejection  
│   └── State transitions  
│  
├── Sliding Window (2 tests)  
│   ├── Old failures eviction  
│   └── Window size enforcement  
│  
├── Thread Safety (2 tests)  
│   ├── Concurrent successful calls  
│   └── Concurrent state transitions  
│  
├── Statistics (4 tests)  
│   ├── Request tracking  
│   ├── Failure rate calculation  
│   ├── Time until retry  
│   └── State change counting  
│  
└── Edge Cases (9 tests)  
    ├── Exact threshold  
    ├── Manual reset  
    ├── Zero timeout  
    ├── Large window sizes  
    └── Boundary conditions

### **Writing Custom Tests**

import unittest  
from circuit\_breaker import CircuitBreaker, CircuitBreakerConfig

class TestMyUsage(unittest.TestCase):  
    def setUp(self):  
        """Run before each test"""  
        self.cb \= CircuitBreaker(  
            CircuitBreakerConfig(failure\_threshold=2)  
        )  
      
    def test\_my\_scenario(self):  
        """Test specific scenario"""  
        \# Arrange  
        def failing\_function():  
            raise Exception("Test failure")  
          
        \# Act  
        with self.assertRaises(Exception):  
            self.cb.call(failing\_function)  
          
        \# Assert  
        stats \= self.cb.get\_stats()  
        self.assertEqual(stats\['failed'\], 1\)

if \_\_name\_\_ \== '\_\_main\_\_':  
    unittest.main()

---

## **Performance Benchmarks** {#performance-benchmarks}

### **Methodology**

Tests run on:

* Python 3.11  
* Single circuit breaker instance  
* No actual I/O (in-memory function calls)

### **Results**

Benchmark: 10,000 successful calls  
─────────────────────────────────  
Total time:        0.654 seconds  
Requests/sec:      15,290  
Overhead/request:  0.065 ms  
Peak memory:       4.2 MB  
Benchmark: 10,000 calls with 50% failures

──────────────────────────────────────────  
Total time:        0.721 seconds  
Requests/sec:      13,870  
Overhead/request:  0.072 ms

Benchmark: Concurrent (100 threads, 100 calls each)  
───────────────────────────────────────────────────  
Total time:        3.456 seconds  
Total requests:    10,000  
Requests/sec:      2,894  
Lock contention:   Minimal  
Data races:        0

### **Running Benchmarks**

\# benchmarks.py  
import time  
from circuit\_breaker import CircuitBreaker

cb \= CircuitBreaker()

def noop():  
    return "success"

\# Benchmark  
iterations \= 10\_000  
start \= time.perf\_counter()

for \_ in range(iterations):  
    cb.call(noop)

elapsed \= time.perf\_counter() \- start

print(f"Requests/sec: {iterations / elapsed:,.0f}")  
print(f"Overhead: {(elapsed / iterations) \* 1000:.3f}ms")

### **Performance Characteristics**

| Operation | Time Complexity | Space Complexity |
| ----- | ----- | ----- |
| `call()` | O(1) | O(1) |
| State check | O(1) | O(1) |
| Add to history | O(1) | O(window\_size) |
| Failure count | O(window\_size) | O(1) |
| State transition | O(1) | O(1) |

|  |  |  |
| ----- | ----- | ----- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

**Key insight:** All operations are constant time except failure counting which is O(window\_size), but window\_size is typically small (5-20).

---

## **Troubleshooting** {#troubleshooting}

### **Common Issues**

#### **Issue: Circuit Opens Too Frequently**

**Symptoms:**

* Circuit opens even though service seems healthy  
* Frequent OPEN → CLOSED → OPEN cycles

**Causes:**

1. `failure_threshold` too low  
2. `window_size` too small  
3. Legitimate intermittent failures

**Solutions:**

\# Increase thresholds  
config \= CircuitBreakerConfig(  
    failure\_threshold=10,  \# Was 3  
    window\_size=20         \# Was 5  
)

\# Or add retry logic  
result \= client.get\_with\_retry(  
    'api',  
    '/endpoint',  
    max\_retries=3  
)

---

#### **Issue: Circuit Never Opens**

**Symptoms:**

* Service clearly failing but circuit stays CLOSED  
* Many failures in stats but state is CLOSED

**Causes:**

1. Failures not raising exceptions  
2. Catching exceptions before circuit breaker sees them  
3. Window size too large

**Solutions:**

\# Ensure exceptions are raised  
def my\_api\_call():  
    response \= requests.get(url)  
    if response.status\_code \>= 500:  
        raise Exception("Server error")  \# Must raise\!  
    return response

\# Don't catch exceptions before circuit breaker  
result \= cb.call(my\_api\_call)  \# Let cb see the exception

---

#### **Issue: Circuit Takes Too Long to Recover**

**Symptoms:**

* Circuit opens correctly but stays open for long time  
* Service recovered but circuit still rejecting

**Solution:**

\# Reduce timeout  
config \= CircuitBreakerConfig(  
    timeout=15.0  \# Was 60.0  
)

\# Or manually reset in emergencies  
if manual\_intervention\_performed:  
    cb.reset()

---

#### **Issue: Thread Safety Concerns**

**Symptoms:**

* Incorrect stats under load  
* Unexpected state transitions  
* Race condition warnings

**Solution:**

* This implementation IS thread-safe  
* If seeing issues, verify you're not:  
  * Sharing state outside circuit breaker  
  * Modifying config after creation  
  * Calling private methods directly

---

### **Debugging Checklist**

\# 1\. Check current state  
stats \= cb.get\_stats()  
print(f"State: {stats\['state'\]}")  
print(f"Stats: {stats}")

\# 2\. Verify configuration  
print(f"Config: {cb.config}")

\# 3\. Check call history  
print(f"Recent calls: {list(cb.call\_history)}")

\# 4\. Monitor state changes  
initial\_changes \= cb.stats.state\_changes  
\# ... do some calls ...  
new\_changes \= cb.stats.state\_changes  
print(f"State changed {new\_changes \- initial\_changes} times")

\# 5\. Test with simple function  
def test\_func():  
    return "ok"

try:  
    result \= cb.call(test\_func)  
    print(f"Basic call works: {result}")  
except Exception as e:  
    print(f"Basic call failed: {e}")

---

## **Best Practices** {#best-practices}

### **1\. Use Separate Circuit Breakers per Service**

\# Don't share one circuit breaker  
cb \= CircuitBreaker()  
cb.call(payment\_api)  
cb.call(email\_api)  \# Payment failures affect email\!

\# Do use one per service  
payment\_cb \= CircuitBreaker()  
email\_cb \= CircuitBreaker()  
payment\_cb.call(payment\_api)  
email\_cb.call(email\_api)

### **2\. Always Provide Fallbacks**

\# Don't just fail  
try:  
    data \= cb.call(api\_call)  
except CircuitBreakerOpenException:  
    raise  \# User sees error\!

\# Do provide fallback  
try:  
    data \= cb.call(api\_call)  
except CircuitBreakerOpenException:  
    data \= cache.get('fallback\_data')  
    log\_warning("Using cached data")

### **3\. Tune Based on Service SLA**

\# Critical service (99.99% uptime expected)  
critical\_config \= CircuitBreakerConfig(  
    failure\_threshold=2,  
    success\_threshold=5,  
    timeout=120.0  
)

\# Non-critical service (95% uptime acceptable)  
noncritical\_config \= CircuitBreakerConfig(  
    failure\_threshold=15,  
    success\_threshold=2,  
    timeout=30.0  
)

### **4\. Monitor State Changes**

\# Set up alerting  
previous\_state \= cb.state

while True:  
    current\_state \= cb.state  
    if current\_state \!= previous\_state:  
        alert(f"Circuit state changed: {previous\_state} → {current\_state}")  
        previous\_state \= current\_state  
    time.sleep(1)

### **5\. Log State Transitions**

import logging

class LoggingCircuitBreaker(CircuitBreaker):  
    def \_transition\_to\_open(self):  
        logging.warning(  
            f"Circuit OPENED for {self.service\_name}. "  
            f"Failures: {self.stats.failed\_requests}"  
        )  
        super().\_transition\_to\_open()  
      
    def \_transition\_to\_closed(self):  
        logging.info(f"Circuit CLOSED for {self.service\_name}. Service recovered.")  
        super().\_transition\_to\_closed()

### **6\. Test Circuit Breaker Behavior**

\# Include in integration tests  
def test\_handles\_service\_outage():  
    \# Simulate outage  
    with mock\_service\_down():  
        \# Verify circuit opens  
        for \_ in range(config.failure\_threshold):  
            with pytest.raises(Exception):  
                cb.call(service\_call)  
          
        assert cb.state \== CircuitState.OPEN  
          
        \# Verify rejection  
        with pytest.raises(CircuitBreakerOpenException):  
            cb.call(service\_call)

### **7\. Use Health Checks**

\# Periodic health check  
def health\_check():  
    stats \= cb.get\_stats()  
      
    return {  
        "healthy": stats\['state'\] \!= 'OPEN',  
        "circuit\_state": stats\['state'\],  
        "failure\_rate": stats\['failure\_rate'\]  
    }

\# In your web framework  
@app.get("/health")  
def get\_health():  
    health \= health\_check()  
    status\_code \= 200 if health\['healthy'\] else 503  
    return JSONResponse(health, status\_code=status\_code)

### **8\. Combine with Retries**

\# Circuit breaker \+ exponential backoff  
from tenacity import retry, stop\_after\_attempt, wait\_exponential

@retry(  
    stop=stop\_after\_attempt(3),  
    wait=wait\_exponential(multiplier=1, min=2, max=10)  
)  
def resilient\_call():  
    return cb.call(api\_function)

\# Now you have both fast-fail AND retry logic

---

## **Advanced Usage** {#advanced-usage}

### **Custom State Change Callbacks**

class CallbackCircuitBreaker(CircuitBreaker):  
    def \_\_init\_\_(self, config, on\_open=None, on\_close=None):  
        super().\_\_init\_\_(config)  
        self.on\_open\_callback \= on\_open  
        self.on\_close\_callback \= on\_close  
      
    def \_transition\_to\_open(self):  
        super().\_transition\_to\_open()  
        if self.on\_open\_callback:  
            self.on\_open\_callback(self.get\_stats())  
      
    def \_transition\_to\_closed(self):  
        super().\_transition\_to\_closed()  
        if self.on\_close\_callback:  
            self.on\_close\_callback(self.get\_stats())

\# Usage  
def alert\_on\_open(stats):  
    send\_alert(f"Circuit opened\! Failure rate: {stats\['failure\_rate'\]}")

def log\_on\_close(stats):  
    logger.info(f"Circuit recovered after {stats\['state\_changes'\]} transitions")

cb \= CallbackCircuitBreaker(  
    config,  
    on\_open=alert\_on\_open,  
    on\_close=log\_on\_close  
)

### **Distributed Circuit Breaker (Redis Backend)**

import redis  
import pickle  
from datetime import timedelta

class DistributedCircuitBreaker(CircuitBreaker):  
    """Circuit breaker with shared state in Redis"""  
      
    def \_\_init\_\_(self, config, service\_name, redis\_client):  
        super().\_\_init\_\_(config)  
        self.service\_name \= service\_name  
        self.redis \= redis\_client  
        self.state\_key \= f"cb:{service\_name}:state"  
        self.stats\_key \= f"cb:{service\_name}:stats"  
      
    def \_load\_state(self):  
        """Load state from Redis"""  
        state\_data \= self.redis.get(self.state\_key)  
        if state\_data:  
            return pickle.loads(state\_data)  
        return None  
      
    def \_save\_state(self):  
        """Save state to Redis"""  
        state\_data \= {  
            'state': self.state,  
            'opened\_at': self.opened\_at,  
            'call\_history': list(self.call\_history)  
        }  
        self.redis.setex(  
            self.state\_key,  
            timedelta(seconds=self.config.timeout \* 2),  
            pickle.dumps(state\_data)  
        )  
      
    def call(self, func, \*args, \*\*kwargs):  
        \# Load shared state  
        shared\_state \= self.\_load\_state()  
        if shared\_state:  
            self.state \= shared\_state\['state'\]  
            self.opened\_at \= shared\_state\['opened\_at'\]  
          
        \# Execute normally  
        result \= super().call(func, \*args, \*\*kwargs)  
          
        \# Save state  
        self.\_save\_state()  
          
        return result

\# Usage  
redis\_client \= redis.Redis(host='localhost', port=6379)  
cb \= DistributedCircuitBreaker(config, 'api\_service', redis\_client)

### **Adaptive Thresholds**

class AdaptiveCircuitBreaker(CircuitBreaker):  
    """Automatically adjusts thresholds based on patterns"""  
      
    def \_\_init\_\_(self, config):  
        super().\_\_init\_\_(config)  
        self.baseline\_failure\_rate \= 0.05  \# 5%  
      
    def \_on\_success(self):  
        super().\_on\_success()  
          
        \# If consistently succeeding, become more sensitive  
        if self.stats.successful\_requests \> 100:  
            recent\_failures \= sum(1 for x in self.call\_history if not x)  
            failure\_rate \= recent\_failures / len(self.call\_history)  
              
            if failure\_rate \< self.baseline\_failure\_rate:  
                \# Lower threshold (open faster)  
                self.config.failure\_threshold \= max(  
                    2,  
                    self.config.failure\_threshold \- 1  
                )  
      
    def \_transition\_to\_closed(self):  
        super().\_transition\_to\_closed()  
          
        \# After recovery, reset to more conservative threshold  
        self.config.failure\_threshold \= min(  
            10,  
            self.config.failure\_threshold \+ 2  
        )

### **Metrics Export to Multiple Backends**

class MultiBackendExporter:  
    """Export metrics to multiple monitoring systems"""  
      
    def \_\_init\_\_(self, circuit\_breaker):  
        self.cb \= circuit\_breaker  
      
    def export\_to\_statsd(self, statsd\_client):  
        """Export to StatsD/Datadog"""  
        stats \= self.cb.get\_stats()  
        statsd\_client.gauge('circuit\_breaker.state',   
                           {'CLOSED': 0, 'HALF\_OPEN': 1, 'OPEN': 2}\[stats\['state'\]\])  
        statsd\_client.increment('circuit\_breaker.requests', stats\['total\_requests'\])  
        statsd\_client.increment('circuit\_breaker.failures', stats\['failed'\])  
      
    def export\_to\_cloudwatch(self, cloudwatch\_client):  
        """Export to AWS CloudWatch"""  
        stats \= self.cb.get\_stats()  
        cloudwatch\_client.put\_metric\_data(  
            Namespace='CircuitBreaker',  
            MetricData=\[  
                {  
                    'MetricName': 'FailureRate',  
                    'Value': float(stats\['failure\_rate'\].rstrip('%')),  
                    'Unit': 'Percent'  
                },  
                {  
                    'MetricName': 'StateChanges',  
                    'Value': stats\['state\_changes'\],  
                    'Unit': 'Count'  
                }  
            \]  
        )  
      
    def export\_to\_influxdb(self, influx\_client):  
        """Export to InfluxDB"""  
        stats \= self.cb.get\_stats()  
        influx\_client.write\_points(\[{  
            'measurement': 'circuit\_breaker',  
            'fields': {  
                'state': stats\['state'\],  
                'total\_requests': stats\['total\_requests'\],  
                'failure\_rate': float(stats\['failure\_rate'\].rstrip('%'))  
            }  
        }\])

---

## **Appendix**

### **Related Patterns**

|  |  |  |
| :---- | ----- | ----- |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |
|  |  |  |

### 

| Pattern | Purpose | When to Use |
| ----- | ----- | ----- |
| **Circuit Breaker** | Prevent cascading failures | External service calls |
| **Retry** | Recover from transient failures | Network hiccups |
| **Bulkhead** | Isolate resources | Prevent resource exhaustion |
| **Rate Limiter** | Control request rate | Protect from overload |
| **Timeout** | Prevent indefinite waits | Any I/O operation |
| **Fallback** | Provide alternative | User-facing services |

### 

### **Combining Patterns**

Request Flow with Multiple Patterns:

User Request  
    

*      Rate Limiter (control incoming rate)  
*      Circuit Breaker (check service health)  
*      Timeout (prevent hanging)  
*      Retry with Backoff (handle transient failures)  
*      Bulkhead (isolate thread pool)  
*       Fallback (if all else fails)

### **Performance Tuning Checklist**

* \[ \] Separate circuit breakers per service  
* \[ \] Tune thresholds based on monitoring  
* \[ \] Use appropriate window size (5-20)  
* \[ \] Set timeout based on service recovery time  
* \[ \] Monitor state change frequency  
* \[ \] Test under load (100+ threads)  
* \[ \] Measure overhead (\<1ms typical)  
* \[ \] Enable monitoring dashboard  
* \[ \] Set up alerts for OPEN state  
* \[ \] Document fallback strategies

### 

### **Glossary**

**Circuit Breaker**: Design pattern that prevents cascading failures by stopping calls to failing services.

**CLOSED State**: Normal operation, all requests pass through.

**OPEN State**: Circuit is "broken", requests are rejected immediately without calling the service.

**HALF-OPEN State**: Testing state where limited requests are allowed to check if service recovered.

**Sliding Window**: A fixed-size buffer that only remembers recent events, automatically forgetting old ones.

**Failure Threshold**: Number of failures that trigger circuit opening.

**Success Threshold**: Number of successes needed to close an open circuit.

**Timeout**: Time to wait before attempting recovery after the circuit opens.

**Fast-Fail**: Immediately reject requests instead of waiting for timeout.

**Cascading Failure**: When failure in one service causes failures in dependent services.

---

## **Support & Contributing**

### **Getting Help**

1. **Check Documentation**: You're reading it\!  
2. **Run Examples**: See `examples/` directory  
3. **Read Tests**: Best source of usage examples  
4. **Check Issues**: GitHub issues for known problems

### **Reporting Bugs**

Include:

1. Python version  
2. Configuration used  
3. Minimal reproduction code  
4. Expected vs actual behavior  
5. Stack trace if applicable

### **Contributing**

1. Fork the repository  
2. Create feature branch  
3. Write tests for new functionality  
4. Ensure all tests pass  
5. Update documentation  
6. Submit pull request

---

**Changelog**  
**v1.0.0 (Current)**

* Initial release  
* Core circuit breaker implementation  
* Thread-safe operations  
* HTTP client integration  
* Monitoring dashboard  
* Prometheus metrics  
* Comprehensive test suite  
* Full documentation

---

**Acknowledgments**

* Inspired by [Netflix Hystrix](https://github.com/Netflix/Hystrix)  
* Pattern described by [Michael Nygard](https://www.michaelnygard.com/) in "Release It\!"  
* State machine design influenced by [Martin Fowler's article](https://martinfowler.com/bliki/CircuitBreaker.html)

---

**Last Updated**: February 2026  
**Version**: 1.0.0  
**Author**: Aditya Pandey

[image1]: <data:image/png;base64,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AKAACPYAAABAARDsAQAAgAIg2AMAAAAFQLAHAAAACoBgDwAAABQAwR4AAAAoAII9AAAAUAAEewAAAKAACPYAAABAARDsAQAAgAIg2AMAAAAFQLAHAAAACqDrqaeeClhYWFhYWFhYWFhY8r3QYw8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCwBwAAAAqAYA8AAAAUAMEeAAAAKACCPQAAAFAABHsAAACgAAj2AAAAQAEQ7AEAAIACINgDAAAABUCw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>

[image2]: <data:image/png;base64,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PProo+bCCy/0ArzUueeea+69917dHEAHBHtgwOSLW/rLt1L2C7h8+RbjRrDHOMkT7m644Ybao4Zf8pKXmKuuusocO3ZMvwRAlwj2wBDZL9++8IUvLE9e7pdvv/GNb+iXAENHsMeoPfzww+a6667LHh+oe+cPHTpkHnroIf0SAH0g2AMjYr+Aq09q9gu4wKgQ7DEqDz74YPY8cH3ce8UrXpHduyw/FAhgcKIK9uvr6+bAgQNmZWVFjwKi0fbl26uvvpov32LoCPYYpvvuu88cPHjQnHfeed4x7oILLjCHDx82jzzyiH4JMHEka0rm3NjY0KMmWlTBHkiN9FZdf/31tXtNzznnHHPllVeau+66S78E2DWCPYbh7rvvzo5dundetjN5wAAQE56KA2BXQk/VkeKpOhg0gj0G5c477zSXX3652bNnT3nMkmPYRRddZG6++WbzxBNP6JcAUSDYAxgIearOJz/5ydqTdexTdeQn03myDnaDYI/destb3pI9ztfthDj11FOz45Mcw4DYEewBDIV+qo6UfbIOT9VBPwj26Mfq6qq59NJLzXOf+9zyWHTGGWeY17/+9eb222/XzYGoEexHQJ59u7a2ZjY3N/UoIHn2qTp79+71Qr59qs7Jkyf1S4Aggj268Z3vfMd86lOfMq973evMaaed5h133vSmN3GLIJImT3OSx7MuLy/rURMtqmDP4y6BnH2yjnuilbJP1gHaEOzR5lvf+pa55ZZbzCmnnOIdX84880xz2WWXmc997nP6JQAmBMEeSIQ8dcJ+Adc9Gct9sHwBFy6CPaxHH33UXHjhhbVOgnPPPdfcc889ujmACUewBxJkv3wrX7h1T9by33z5FgT76Sa3td5www21x+y+9KUvNVdddZU5duyYfgmASBDsgcTdcccdtS/g2i/ffuQjH+ELuFOIYD99Hn74YXPddddl9wzr3vlDhw6Zhx56SL8EQISiCvYAdke+gKu/fCslX8Dly7fTg2A/PR588MHsS4B6n3/FK16RfelefiQPQB1PxQEQDfvl2/PPP9872dsv395///36JUgIwT5t9913nzl48KA577zzvP37ggsuMIcPHzaPPPKIfgkAhWAPIErSY3f99dfXevTkp+GvvPJK3RwJINin6e677872W70vy99ZvlwPoHsEewBRs0/V2bdvX/aT8DYU8FSd9BDs03Hn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gWCPFBDsgbQQ7AGgDwR7pIBgD6SFYD8CS0tL2RcZ5AsNANJAsEcKCPZAWuRBLfLAlu3tbT1qokUV7HncJZAegj1SQLAHMAkI9gDGimCPFBDsAUwCgj2AsbLB/g/+4A8oKuoi2AMYt6iC/fr6ujlw4IBZWVnRowBEygZ7ikqhAKRBsqZkzo2NDT1qokUV7AGk54orrqCoZApAGngqDgAAAJAAgj0AAACQAII9AAAAkACC/QhsbW1lPxYgPxoAAAAADIP8GKr8KOry8rIeNdGiCvY87hIAAAAII9gDAAAACSDYAwAAAAmIKtgvLS1l9zvJfU8AAADAMMj3OeV7ndvb23rURIsq2AMAAADDxlNxAAAAgAQQ7AEAAIAEEOwBAACABBDsAQAAgAQQ7EeAx10CAAAAYQR7AAAAIAEEewAAACABBHsAAAAgAVEF+62trexXwOTXwAAAAIBhWFhYMHNzc2Z5eVmPmmhRBXsAAABg2HgqDgAAAJAAgj0AAACQAII9AAAAkACC/QgsLS1lX2SQLzQAAAAAwyAPapEHtmxvb+tREy2qYM/jLgEAAIAwgj0AAACQAII9AAAAkIAkgv2BAwe8es973uONF9dee63X5itf+YpuYm6//XavzR133OGNf+ihh7zxUu973/u8NuJd73qX1+ZrX/uaN16+K6CnI/dxuR544AFv/OHDh73xlp7OY4895o0/cuRIrY32pS99yRv/4Q9/WDepTUPqySef9Np89KMf9cbfe++93nixvr7utfnYxz7mjX/88ce98ba0D37wg974Y8eO6Sa1aXziE5/wxn/961/3xh88eNAbb73//e/32h0/ftwb/9nPftYbL6XJPXru+ND3RBYXF2vTOXnypNdmdXXVGy//rclr3Dbvfe97dRNzzTXXeG2ktJWVFW+8rKemp3H99dfrJtn76raR912Tv43b5s477/TG33///d54qRtvvNFrI3Qb2Z5csr3pNhsbG16be+65xxsv27Um276ezlNPPeW1+dCHPlRro33+8/9/e3eo01gUBGD44QEBAtUiIGmC6gNUVFXRJQGFoAaagKqq4gUgsw3hnrl3Kananf2+5KgZjqDcy28Iv5p5PK9ZvmPonouLi2b++PiYV36/Y7o78R7qivdUdx7n6Oio2Qnxh2Tdnaenp2Ye7818T7xbu+L9252fnp42809nZ2fN3uvrazOfzWbNPE72/PzczOP3SHZ8fNy7Z7PZNDvxT2q688Vi0czDarVqdsbjcV5p5p8nm06nzXy5XOaV3h1XV1d5pbfz9vaWV96vr6+bnfv7+2Z+d3fXuye+pivuzTvZ5eVlb+fh4aHZubm5aebxfci2223vnmw0Gu3dic+vOx/6J0T5jpOTk7zyfn5+3uys1+u88j6fz5ud+Lntenl5aeZxDumY3DBx9nXMUMOEQzom+0nH5Dvi7OuY29vbZh72dUy8n7vzz5NNJpNmPtQxf7t/Kuz/JH9QhzwQIT8U+x6IOEMPxSEPhLDfEfbtPcJ+R9h/f4+w/zqZsP86wv6LsN+doYYJh3RM9pOOyXfE2dcxwv57JcIeAAD+d8IeAAAKEPYAAFCAsAcAgAKEPQAAFCDsAQCgAGEPAAAFCHsAAChA2AMAQAHCHgAAChD2AABQgLAHAIAChD0AABQg7AEAoABhDwAABQh7AAAoQNgDAEABwh4AAAoQ9gAAUICwBwCAAoQ9AAAUIOwBAKAAYQ8AAAUIewAAKEDYAwBAAcIeAAAKEPYAAFCAsAcAgAKEPQAAFCDsAQCgAGEPAAAFCHsAAChA2AMAQAHCHgAAChD2AABQgLAHAIAChD0AABQg7AEAoABhDwAABQh7AAAoQNgDAEABwh4AAAoQ9gAAUICwBwCAAoQ9AAAUEGH/Ad6goago3cJlAAAAAElFTkSuQmCC>

[image3]: <data:image/png;base64,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>