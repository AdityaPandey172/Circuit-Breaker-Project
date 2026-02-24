# **Circuit Breaker \- Setup Guide**

Complete step-by-step guide to get the Circuit Breaker running on your machine in under 5 minutes.

---

## **Prerequisites**

### **Required**

**Python 3.7 or higher**

 Check your version:

 python \--version  
\# or  
python3 \--version

*  If you don't have Python:

  * **macOS**: `brew install python3`  
  * **Ubuntu/Debian**: `sudo apt install python3 python3-pip`  
  * **Windows**: Download from [python.org](https://www.python.org/downloads/)

### **Optional (for HTTP client features)**

**requests library**  
 pip install requests\# orpip3 install requests

---

## **Quick Start (60 seconds)**

### **1\. Download the Files**

Option A: Clone repository (if on GitHub)

git clone https://github.com/yourusername/circuit-breaker.git  
cd circuit-breaker

Option B: Download individual files

* Download all `.py` files to a folder  
* Make sure they're in the same directory

### **2\. Verify Installation**

\# Navigate to project directory  
cd circuit-breaker

\# Check files are present  
ls \-la  
\# You should see:  
\# circuit\_breaker.py  
\# circuit\_breaker\_tests.py  
\# circuit\_breaker\_monitoring.py  
\# circuit\_breaker\_http.py

### **3\. Run Your First Demo**

python circuit\_breaker.py

**Expected output:**

\======================================================================  
CIRCUIT BREAKER DEMO  
\======================================================================

Phase 1: Service is healthy (0% failure rate)  
  Request 1: Success: Data retrieved  
  Request 2: Success: Data retrieved  
  ...

 Circuit OPENED at 14:23:45

Phase 2: Service degrading (80% failure rate)  
 Request 1: Failed \- Service unavailable  
  ...

**If you see this, everything is working\!**

---

## **Running Tests**

### **Basic Test Run**

python circuit\_breaker\_tests.py

**Expected output:**

test\_circuit\_opens\_after\_threshold\_failures ... ok  
test\_circuit\_transitions\_to\_half\_open ... ok  
test\_concurrent\_successful\_calls ... ok  
...  
\----------------------------------------------------------------------  
Ran 25 tests in 2.345s

OK

\====================================================================  
Tests run: 25  
Failures: 0  
Errors: 0  
Success rate: 100.0%  
\====================================================================

### **Verbose Test Run**

python circuit\_breaker\_tests.py \-v

This shows each test name as it runs.

### **Run Specific Test**

\# Run only thread safety tests  
python \-m unittest circuit\_breaker\_tests.TestCircuitBreakerThreadSafety

\# Run single test  
python \-m unittest circuit\_breaker\_tests.TestCircuitBreakerBasics.test\_circuit\_opens\_after\_threshold\_failures

---

## **Running Monitoring Dashboard**

### **1\. Start the Monitoring Demo**

python circuit\_breaker\_monitoring.py

**Expected output:**

\======================================================================  
CIRCUIT BREAKER WITH MONITORING DEMO  
\======================================================================

Monitoring dashboard: http://localhost:8080/  
Prometheus metrics:   http://localhost:8080/metrics  
JSON stats:           http://localhost:8080/stats  
Health check:        http://localhost:8080/health

Open your browser to view the dashboard\!  
The dashboard auto-refreshes every 2 seconds.

### **2\. Open the Dashboard**

1. **Open your web browser**  
2. **Go to**: `http://localhost:8080/`  
3. **You should see**: A colorful dashboard with real-time metrics

### **3\. View Different Endpoints**

* **HTML Dashboard**: `http://localhost:8080/`  
* **Prometheus Metrics**: `http://localhost:8080/metrics`  
* **JSON Stats**: `http://localhost:8080/stats`  
* **Health Check**: `http://localhost:8080/health`

### **4\. Stop the Server**

Press `Ctrl+C` in the terminal

---

## **Running HTTP Client Demo**

### **1\. Install requests library (if not already)**

pip install requests

### **2\. Run the HTTP demo**

python circuit\_breaker\_http.py

**Expected output:**

\======================================================================  
HTTP CLIENT WITH CIRCUIT BREAKER DEMO  
\======================================================================

Registered service: payment\_api at https://api.stripe.com  
Registered service: analytics\_api at https://api.example.com  
Registered service: test\_api at https://jsonplaceholder.typicode.com

\======================================================================  
TEST 1: Successful API Calls  
\======================================================================

Request 1: Status 200 \- Got post with id=1  
Request 2: Status 200 \- Got post with id=2

---

**Troubleshooting**

### **Issue: "Python not found"**

**Solution:**

\# Try python3 instead of python  
python3 circuit\_breaker.py

\# Or create an alias (add to \~/.bashrc or \~/.zshrc)  
alias python=python3

### **Issue: "ModuleNotFoundError: No module named 'circuit\_breaker'"**

**Cause:** Files not in same directory or running from wrong location

**Solution:**

\# Make sure you're in the project directory  
pwd  \# Should show /path/to/circuit-breaker

\# Check files are present  
ls \-la circuit\_breaker.py

\# Run from project root  
python circuit\_breaker.py

### **Issue: "ModuleNotFoundError: No module named 'requests'"**

**Solution:**

\# Install requests  
pip install requests

\# If pip doesn't work, try pip3  
pip3 install requests

\# Or use python \-m pip  
python \-m pip install requests

### **Issue: "Address already in use" (Port 8080\)**

**Cause:** Another program is using port 8080

**Solution 1:** Kill the process using that port

\# Find process using port 8080  
lsof \-i :8080  \# macOS/Linux  
netstat \-ano | findstr :8080  \# Windows

\# Kill the process  
kill \-9 \<PID\>  \# Replace \<PID\> with actual process ID

**Solution 2:** Use a different port

\# Edit circuit\_breaker\_monitoring.py  
cb \= MonitoredCircuitBreaker(  
    monitoring\_port=8081  \# Change to 8081 or any free port  
)

### **Issue: Tests fail with "AssertionError"**

**Cause:** Timing-related test failures (rare)

**Solution:**

\# Run tests again (timing issues are usually transient)  
python circuit\_breaker\_tests.py

\# If specific test fails consistently, run it alone  
python \-m unittest circuit\_breaker\_tests.TestCircuitBreakerBasics.test\_name

### **Issue: "Permission denied" when running scripts**

**Solution:**

\# Make scripts executable  
chmod \+x \*.py

\# Or run with python explicitly  
python circuit\_breaker.py

---

## **Project Structure**

After setup, your directory should look like:

circuit-breaker/  
├── circuit\_breaker.py              \# Core implementation (800 lines)  
├── circuit\_breaker\_tests.py        \# Unit tests (600 lines)  
├── circuit\_breaker\_monitoring.py   \# Monitoring dashboard (400 lines)  
├── circuit\_breaker\_http.py         \# HTTP client integration (350 lines)  
├── README.md                        \# Project overview  
├── DOCUMENTATION.md                 \# Complete documentation  
├── SETUP\_GUIDE.md                   \# This file  
└── examples/                        \# (Optional) Usage examples  
    ├── basic\_usage.py  
    ├── http\_integration.py  
    └── microservices\_demo.py

---

## **Quick Reference**

### **Run Commands**

| Command | Purpose |
| ----- | ----- |
| `python circuit_breaker.py` | Basic demo with state transitions |
| `python circuit_breaker_tests.py` | Run all unit tests |
| `python circuit_breaker_monitoring.py` | Start monitoring dashboard |
| `python circuit_breaker_http.py` | HTTP client demo |

### **Import in Your Code**

\# Basic usage  
from circuit\_breaker import CircuitBreaker, CircuitBreakerConfig

\# HTTP client  
from circuit\_breaker\_http import ResilientHTTPClient

\# With monitoring

|  |  |
| :---- | ----- |
|  |  |
|  |  |
|  |  |
|  |  |

from circuit\_breaker\_monitoring import MonitoredCircuitBreaker

\# Exceptions  
from circuit\_breaker import CircuitBreakerOpenException

### **Minimal Working Example**

from circuit\_breaker import CircuitBreaker

\# Create circuit breaker  
cb \= CircuitBreaker()

\# Your function  
def my\_api\_call():  
    \# Your code here  
    return "success"

\# Protected call  
try:  
    result \= cb.call(my\_api\_call)  
    print(result)  
except Exception as e:  
    print(f"Failed: {e}")

---

**Getting Help**

### **Documentation**

* **README.md** \- Overview and quick start  
* **DOCUMENTATION.md** \- Complete API reference  
* **SETUP\_GUIDE.md** \- This file

### **Code Examples**

* Check `examples/` directory  
* Look at test cases in `circuit_breaker_tests.py`  
* Read inline comments in `circuit_breaker.py`

### **Common Questions**

**Q: Do I need to install any dependencies?**  
 A: Only if you want to use the HTTP client features. Core functionality has no dependencies.

**Q: Can I use this in production?**  
 A: The code is production-quality, but you should:

1. Add proper logging  
2. Integrate with your monitoring system  
3. Tune thresholds for your services  
4. Add comprehensive tests for your use cases

**Q: How do I integrate with my existing code?**  
 A: Wrap any function call that makes external requests:

\# Before  
result \= my\_external\_api\_call()

\# After  
result \= cb.call(my\_external\_api\_call)

**Q: What Python versions are supported?**  
 A: Python 3.7+ (tested on 3.7, 3.9, 3.11)

**Q: Is it thread-safe?**  
 A: Yes\! The implementation uses `threading.Lock()` for thread safety.

---

**Verification Checklist**  
Before considering setup complete:

* \[ \] Python 3.7+ installed  
* \[ \] All `.py` files in same directory  
* \[ \] `python circuit_breaker.py` runs without errors  
* \[ \] Tests pass: `python circuit_breaker_tests.py`  
* \[ \] Can access monitoring dashboard at `http://localhost:8080/`  
* \[ \] HTTP client works (if requests installed)  
* \[ \] Understand basic usage from examples  
* \[ \] Read README.md

---

## **Setup Complete\!**

You're ready to:

* Run demos and see circuit breaker in action  
* Integrate into your own projects  
* Modify and experiment with configurations  
* Use in portfolio/GitHub  
* Discuss in technical interviews

**Next recommended action:** Run the monitoring demo and watch the dashboard while the circuit breaker operates\!

python circuit\_breaker\_monitoring.py  
\# Then open http://localhost:8080/ in your browser

---

**Questions?** Check `DOCUMENTATION.md` for detailed API reference and advanced usage  
