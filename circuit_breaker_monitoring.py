"""
Circuit Breaker with Monitoring and Metrics Export

This adds:
- HTTP endpoint for real-time stats
- Prometheus-compatible metrics format
- JSON logging for state changes
- Health check endpoint
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


class MetricsExporter:
    """Exports circuit breaker metrics in multiple formats"""
    
    def __init__(self, circuit_breaker: CircuitBreaker, service_name: str = "api"):
        self.cb = circuit_breaker
        self.service_name = service_name
    
    def to_json(self) -> str:
        """Export metrics as JSON"""
        stats = self.cb.get_stats()
        
        return json.dumps({
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "circuit_breaker": {
                "state": stats["state"],
                "metrics": {
                    "total_requests": stats["total_requests"],
                    "successful_requests": stats["successful"],
                    "failed_requests": stats["failed"],
                    "rejected_requests": stats["rejected"],
                    "failure_rate": stats["failure_rate"],
                    "state_changes": stats["state_changes"]
                },
                "timing": {
                    "time_until_retry_seconds": stats["time_until_retry"]
                }
            }
        }, indent=2)
    
    def to_prometheus(self) -> str:
        """
        Export metrics in Prometheus format
        
        Prometheus is an industry-standard monitoring system.
        This format can be scraped by Prometheus server.
        """
        stats = self.cb.get_stats()
        
        # Convert state to numeric (for graphing)
        state_value = {
            "CLOSED": 0,
            "HALF_OPEN": 1,
            "OPEN": 2
        }.get(stats["state"], -1)
        
        # Extract numeric failure rate
        failure_rate = float(stats["failure_rate"].rstrip('%'))
        
        metrics = [
            f'# HELP circuit_breaker_state Current state (0=CLOSED, 1=HALF_OPEN, 2=OPEN)',
            f'# TYPE circuit_breaker_state gauge',
            f'circuit_breaker_state{{service="{self.service_name}"}} {state_value}',
            '',
            f'# HELP circuit_breaker_requests_total Total number of requests',
            f'# TYPE circuit_breaker_requests_total counter',
            f'circuit_breaker_requests_total{{service="{self.service_name}"}} {stats["total_requests"]}',
            '',
            f'# HELP circuit_breaker_requests_successful Successful requests',
            f'# TYPE circuit_breaker_requests_successful counter',
            f'circuit_breaker_requests_successful{{service="{self.service_name}"}} {stats["successful"]}',
            '',
            f'# HELP circuit_breaker_requests_failed Failed requests',
            f'# TYPE circuit_breaker_requests_failed counter',
            f'circuit_breaker_requests_failed{{service="{self.service_name}"}} {stats["failed"]}',
            '',
            f'# HELP circuit_breaker_requests_rejected Rejected requests (circuit open)',
            f'# TYPE circuit_breaker_requests_rejected counter',
            f'circuit_breaker_requests_rejected{{service="{self.service_name}"}} {stats["rejected"]}',
            '',
            f'# HELP circuit_breaker_failure_rate_percent Current failure rate',
            f'# TYPE circuit_breaker_failure_rate_percent gauge',
            f'circuit_breaker_failure_rate_percent{{service="{self.service_name}"}} {failure_rate}',
            '',
            f'# HELP circuit_breaker_state_changes_total Number of state transitions',
            f'# TYPE circuit_breaker_state_changes_total counter',
            f'circuit_breaker_state_changes_total{{service="{self.service_name}"}} {stats["state_changes"]}',
        ]
        
        return '\n'.join(metrics)
    
    def to_html_dashboard(self) -> str:
        """Generate HTML dashboard for human viewing"""
        stats = self.cb.get_stats()
        
        # State indicator with colors
        state_colors = {
            "CLOSED": "#10b981",    # Green
            "HALF_OPEN": "#f59e0b", # Orange
            "OPEN": "#ef4444"       # Red
        }
        state = stats["state"]
        color = state_colors.get(state, "#6b7280")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Circuit Breaker Dashboard - {self.service_name}</title>
            <meta http-equiv="refresh" content="2">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 20px;
                    background: #f3f4f6;
                }}
                .header {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                h1 {{
                    margin: 0;
                    color: #1f2937;
                }}
                .state-badge {{
                    display: inline-block;
                    padding: 8px 16px;
                    border-radius: 20px;
                    color: white;
                    font-weight: bold;
                    background: {color};
                    margin-top: 10px;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
                .metric-label {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-bottom: 8px;
                }}
                .metric-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #1f2937;
                }}
                .info {{
                    background: #dbeafe;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 20px;
                }}
                .timestamp {{
                    color: #6b7280;
                    font-size: 14px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Circuit Breaker Dashboard</h1>
                <div>Service: <strong>{self.service_name}</strong></div>
                <div class="state-badge">{state}</div>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-label">Total Requests</div>
                    <div class="metric-value">{stats["total_requests"]}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Successful</div>
                    <div class="metric-value" style="color: #10b981;">{stats["successful"]}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Failed</div>
                    <div class="metric-value" style="color: #ef4444;">{stats["failed"]}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Rejected</div>
                    <div class="metric-value" style="color: #f59e0b;">{stats["rejected"]}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">Failure Rate</div>
                    <div class="metric-value" style="font-size: 24px;">{stats["failure_rate"]}</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-label">State Changes</div>
                    <div class="metric-value">{stats["state_changes"]}</div>
                </div>
            </div>
            
            {f'''
            <div class="info">
                ⏳ Circuit will attempt recovery in {stats["time_until_retry"]:.1f} seconds
            </div>
            ''' if state == "OPEN" else ''}
            
            <div class="timestamp">
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                <br>
                Auto-refreshing every 2 seconds
            </div>
        </body>
        </html>
        """
        
        return html


class CircuitBreakerHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for metrics endpoints"""
    
    circuit_breaker = None  # Will be set by server
    service_name = None
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/':
            # HTML Dashboard
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            exporter = MetricsExporter(self.circuit_breaker, self.service_name)
            self.wfile.write(exporter.to_html_dashboard().encode())
        
        elif self.path == '/metrics':
            # Prometheus format
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; version=0.0.4')
            self.end_headers()
            
            exporter = MetricsExporter(self.circuit_breaker, self.service_name)
            self.wfile.write(exporter.to_prometheus().encode())
        
        elif self.path == '/stats':
            # JSON format
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            exporter = MetricsExporter(self.circuit_breaker, self.service_name)
            self.wfile.write(exporter.to_json().encode())
        
        elif self.path == '/health':
            # Health check endpoint
            stats = self.circuit_breaker.get_stats()
            is_healthy = stats["state"] != "OPEN"
            
            status_code = 200 if is_healthy else 503
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "healthy": is_healthy,
                "state": stats["state"],
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            # 404 for unknown paths
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')


class MonitoredCircuitBreaker(CircuitBreaker):
    """
    Circuit Breaker with built-in monitoring server
    
    Extends the base CircuitBreaker with HTTP endpoints for monitoring.
    """
    
    def __init__(self, config: CircuitBreakerConfig = None, 
                 service_name: str = "api", 
                 monitoring_port: int = 8080):
        super().__init__(config)
        self.service_name = service_name
        self.monitoring_port = monitoring_port
        self.http_server = None
        self.server_thread = None
    
    def start_monitoring(self):
        """Start HTTP monitoring server in background thread"""
        
        # Set class variables for handler
        CircuitBreakerHTTPHandler.circuit_breaker = self
        CircuitBreakerHTTPHandler.service_name = self.service_name
        
        self.http_server = HTTPServer(('', self.monitoring_port), 
                                     CircuitBreakerHTTPHandler)
        
        self.server_thread = Thread(target=self.http_server.serve_forever, 
                                    daemon=True)
        self.server_thread.start()
        
        print(f"📊 Monitoring dashboard: http://localhost:{self.monitoring_port}/")
        print(f"📈 Prometheus metrics:   http://localhost:{self.monitoring_port}/metrics")
        print(f"📋 JSON stats:           http://localhost:{self.monitoring_port}/stats")
        print(f"❤️  Health check:        http://localhost:{self.monitoring_port}/health")
    
    def stop_monitoring(self):
        """Stop monitoring server"""
        if self.http_server:
            self.http_server.shutdown()
            print("🛑 Monitoring stopped")


# ============================================================================
# DEMO: Circuit Breaker with Monitoring
# ============================================================================

def demo_with_monitoring():
    """Demonstrate circuit breaker with live monitoring"""
    import random
    
    print("="*70)
    print("CIRCUIT BREAKER WITH MONITORING DEMO")
    print("="*70)
    
    # Create monitored circuit breaker
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=10.0,
        window_size=5
    )
    
    cb = MonitoredCircuitBreaker(
        config=config,
        service_name="payment_api",
        monitoring_port=8080
    )
    
    # Start monitoring server
    cb.start_monitoring()
    
    print("\n✨ Open your browser to view the dashboard!")
    print("   The dashboard auto-refreshes every 2 seconds.")
    print("\nSimulating API calls with varying failure rates...\n")
    
    # Simulate API calls with changing conditions
    def flaky_api(failure_prob):
        time.sleep(0.1)
        if random.random() < failure_prob:
            raise Exception("API Error")
        return "Success"
    
    try:
        # Phase 1: Healthy (5 seconds)
        print("📊 Phase 1: Healthy service (10 seconds)")
        end_time = time.time() + 10
        while time.time() < end_time:
            try:
                cb.call(flaky_api, failure_prob=0.1)
            except Exception:
                pass
            time.sleep(0.5)
        
        # Phase 2: Degraded (10 seconds)
        print("\n📊 Phase 2: Degraded service (10 seconds)")
        end_time = time.time() + 10
        while time.time() < end_time:
            try:
                cb.call(flaky_api, failure_prob=0.7)
            except Exception:
                pass
            time.sleep(0.5)
        
        # Phase 3: Keep running
        print("\n📊 Phase 3: Continuing... (Press Ctrl+C to stop)")
        while True:
            try:
                # Random failure rate
                cb.call(flaky_api, failure_prob=random.uniform(0.2, 0.8))
            except Exception:
                pass
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping demo...")
        cb.stop_monitoring()
        print("\nFinal stats:")
        print(json.dumps(cb.get_stats(), indent=2))


if __name__ == "__main__":
    demo_with_monitoring()