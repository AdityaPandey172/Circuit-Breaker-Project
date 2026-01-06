"""
Production-Ready HTTP Client with Circuit Breaker

This demonstrates real-world usage:
- Wraps HTTP requests with circuit breaker protection
- Handles timeouts and connection errors
- Provides retry logic with exponential backoff
- Supports multiple downstream services
"""

import requests
import time
from typing import Optional, Dict, Any
from circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenException


class CircuitBreakerHTTPClient:
    """
    HTTP Client with Circuit Breaker protection
    
    Use this to make resilient HTTP calls to external services.
    Each downstream service gets its own circuit breaker.
    """
    
    def __init__(self):
        # Store separate circuit breaker for each service
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Default configuration
        self.default_config = CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=30.0,
            window_size=10
        )
    
    def register_service(self, service_name: str, 
                        base_url: str, 
                        config: Optional[CircuitBreakerConfig] = None):
        """
        Register a downstream service with its own circuit breaker
        
        Args:
            service_name: Unique identifier for the service
            base_url: Base URL for the service (e.g., "https://api.example.com")
            config: Custom circuit breaker configuration
        """
        self.circuit_breakers[service_name] = {
            'breaker': CircuitBreaker(config or self.default_config),
            'base_url': base_url.rstrip('/')
        }
        print(f"✅ Registered service: {service_name} at {base_url}")
    
    def get(self, service_name: str, path: str, 
            timeout: float = 5.0, **kwargs) -> requests.Response:
        """
        Make GET request through circuit breaker
        
        Args:
            service_name: Name of registered service
            path: API path (e.g., "/users/123")
            timeout: Request timeout in seconds
            **kwargs: Additional arguments passed to requests.get()
        
        Returns:
            Response object
            
        Raises:
            CircuitBreakerOpenException: If circuit is open
            requests.RequestException: If request fails
        """
        return self._make_request(service_name, 'GET', path, timeout, **kwargs)
    
    def post(self, service_name: str, path: str, 
             timeout: float = 5.0, **kwargs) -> requests.Response:
        """Make POST request through circuit breaker"""
        return self._make_request(service_name, 'POST', path, timeout, **kwargs)
    
    def put(self, service_name: str, path: str, 
            timeout: float = 5.0, **kwargs) -> requests.Response:
        """Make PUT request through circuit breaker"""
        return self._make_request(service_name, 'PUT', path, timeout, **kwargs)
    
    def delete(self, service_name: str, path: str, 
               timeout: float = 5.0, **kwargs) -> requests.Response:
        """Make DELETE request through circuit breaker"""
        return self._make_request(service_name, 'DELETE', path, timeout, **kwargs)
    
    def _make_request(self, service_name: str, method: str, path: str,
                     timeout: float, **kwargs) -> requests.Response:
        """Internal method to make HTTP request through circuit breaker"""
        
        if service_name not in self.circuit_breakers:
            raise ValueError(f"Service '{service_name}' not registered. "
                           f"Call register_service() first.")
        
        service = self.circuit_breakers[service_name]
        breaker = service['breaker']
        url = f"{service['base_url']}{path}"
        
        # Define the function that will be protected by circuit breaker
        def make_http_call():
            response = requests.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            # Consider 5xx errors as failures (should trip circuit)
            # 4xx errors are client errors (don't trip circuit)
            if response.status_code >= 500:
                raise requests.HTTPError(
                    f"Server error: {response.status_code}",
                    response=response
                )
            
            return response
        
        # Execute through circuit breaker
        return breaker.call(make_http_call)
    
    def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """Get circuit breaker stats for a specific service"""
        if service_name not in self.circuit_breakers:
            raise ValueError(f"Service '{service_name}' not registered")
        
        return self.circuit_breakers[service_name]['breaker'].get_stats()
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get stats for all registered services"""
        return {
            name: service['breaker'].get_stats()
            for name, service in self.circuit_breakers.items()
        }


class ResilientHTTPClient(CircuitBreakerHTTPClient):
    """
    Enhanced HTTP client with retry logic and exponential backoff
    
    This adds another layer of resilience on top of circuit breaker.
    """
    
    def get_with_retry(self, service_name: str, path: str,
                      max_retries: int = 3,
                      backoff_factor: float = 2.0,
                      timeout: float = 5.0,
                      **kwargs) -> requests.Response:
        """
        Make GET request with exponential backoff retry
        
        Args:
            service_name: Name of registered service
            path: API path
            max_retries: Maximum number of retry attempts
            backoff_factor: Multiplier for retry delay (delay = backoff_factor ^ attempt)
            timeout: Request timeout
            **kwargs: Additional request arguments
        
        Returns:
            Response object
            
        The retry logic works like this:
        - Attempt 1: immediate
        - Attempt 2: wait 2^1 = 2 seconds
        - Attempt 3: wait 2^2 = 4 seconds
        - Attempt 4: wait 2^3 = 8 seconds
        """
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.get(service_name, path, timeout, **kwargs)
                
            except CircuitBreakerOpenException as e:
                # Circuit is open - don't retry, fail fast
                print(f"❌ Circuit open for {service_name}, not retrying")
                raise e
                
            except requests.Timeout as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = backoff_factor ** attempt
                    print(f"⏱️  Timeout on attempt {attempt + 1}, "
                          f"retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"❌ All {max_retries} attempts failed for {service_name}")
                    
            except requests.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = backoff_factor ** attempt
                    print(f"⚠️  Request failed on attempt {attempt + 1}, "
                          f"retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    print(f"❌ All {max_retries} attempts failed for {service_name}")
        
        # All retries exhausted
        raise last_exception


# ============================================================================
# DEMO: Real HTTP Client with Circuit Breaker
# ============================================================================

def demo_http_circuit_breaker():
    """Demonstrate HTTP client with circuit breaker protection"""
    
    print("="*70)
    print("HTTP CLIENT WITH CIRCUIT BREAKER DEMO")
    print("="*70)
    
    # Create resilient HTTP client
    client = ResilientHTTPClient()
    
    # Register services with different configurations
    
    # Strict configuration for critical payment service
    payment_config = CircuitBreakerConfig(
        failure_threshold=2,  # Open after just 2 failures
        success_threshold=3,  # Need 3 successes to close
        timeout=60.0,
        window_size=5
    )
    client.register_service(
        service_name='payment_api',
        base_url='https://api.stripe.com',
        config=payment_config
    )
    
    # Lenient configuration for non-critical analytics
    analytics_config = CircuitBreakerConfig(
        failure_threshold=10,  # More tolerant of failures
        success_threshold=2,
        timeout=30.0,
        window_size=20
    )
    client.register_service(
        service_name='analytics_api',
        base_url='https://api.example.com',
        config=analytics_config
    )
    
    # Register a test service (JSONPlaceholder - free test API)
    test_config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=20.0,
        window_size=5
    )
    client.register_service(
        service_name='test_api',
        base_url='https://jsonplaceholder.typicode.com',
        config=test_config
    )
    
    print("\n" + "="*70)
    print("TEST 1: Successful API Calls")
    print("="*70)
    
    # Make some successful calls to test API
    for i in range(1, 4):
        try:
            response = client.get('test_api', f'/posts/{i}', timeout=10.0)
            print(f"✅ Request {i}: Status {response.status_code} - "
                  f"Got post with id={response.json()['id']}")
        except Exception as e:
            print(f"❌ Request {i} failed: {e}")
        time.sleep(0.5)
    
    # Show stats
    print("\n📊 Test API Stats:")
    stats = client.get_service_stats('test_api')
    print(f"   State: {stats['state']}")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Successful: {stats['successful']}")
    print(f"   Failed: {stats['failed']}")
    
    print("\n" + "="*70)
    print("TEST 2: Simulating Service Failures")
    print("="*70)
    
    # Try to access a non-existent endpoint (will get 404, not counted as failure)
    # Then try invalid domain (will fail and trip circuit)
    
    print("\nRegistering a flaky test service...")
    client.register_service(
        service_name='flaky_api',
        base_url='https://this-domain-does-not-exist-12345.com',
        config=CircuitBreakerConfig(
            failure_threshold=2,
            timeout=5.0,
            window_size=5
        )
    )
    
    print("Making requests to non-existent service...")
    for i in range(5):
        try:
            response = client.get('flaky_api', '/data', timeout=2.0)
            print(f"✅ Request {i+1}: Success")
        except CircuitBreakerOpenException as e:
            print(f"⚡ Request {i+1}: Circuit OPEN - {e}")
        except Exception as e:
            print(f"❌ Request {i+1}: Failed - {type(e).__name__}")
        time.sleep(0.3)
    
    print("\n📊 Flaky API Stats:")
    stats = client.get_service_stats('flaky_api')
    print(f"   State: {stats['state']}")
    print(f"   Rejected: {stats['rejected']}")
    
    print("\n" + "="*70)
    print("TEST 3: Retry with Exponential Backoff")
    print("="*70)
    
    print("\nAttempting request with auto-retry...")
    try:
        response = client.get_with_retry(
            'test_api',
            '/posts/1',
            max_retries=3,
            backoff_factor=1.5,
            timeout=10.0
        )
        print(f"✅ Success after retries: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed after all retries: {e}")
    
    print("\n" + "="*70)
    print("ALL SERVICES STATS")
    print("="*70)
    
    all_stats = client.get_all_stats()
    for service_name, stats in all_stats.items():
        print(f"\n{service_name}:")
        print(f"   State: {stats['state']}")
        print(f"   Requests: {stats['total_requests']} "
              f"(✓ {stats['successful']} / ✗ {stats['failed']} / "
              f"⚡ {stats['rejected']})")
        print(f"   Failure rate: {stats['failure_rate']}")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("1. Each service has its own circuit breaker")
    print("2. Circuit opens after threshold failures")
    print("3. Requests are rejected while circuit is open (fail-fast)")
    print("4. Retry logic works with circuit breaker")
    print("5. 4xx errors don't trip circuit (client errors)")
    print("6. 5xx errors DO trip circuit (server errors)")


if __name__ == "__main__":
    # Check if requests library is available
    try:
        import requests
        demo_http_circuit_breaker()
    except ImportError:
        print("❌ Error: 'requests' library not found")
        print("\nInstall it with: pip install requests")
        print("\nOr run a simpler demo without HTTP:")
        print("   python circuit_breaker.py")