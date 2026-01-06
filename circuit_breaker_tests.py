import unittest
import time
import threading
from unittest.mock import Mock
from circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerOpenException
)


class TestCircuitBreakerBasics(unittest.TestCase):
    """Test basic circuit breaker functionality"""
    
    def setUp(self):
        """Create a fresh circuit breaker for each test"""
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=1.0,  # Short timeout for faster tests
            window_size=5
        )
        self.cb = CircuitBreaker(self.config)
    
    def test_initial_state_is_closed(self):
        """Circuit breaker should start in CLOSED state"""
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
    
    def test_successful_call_passes_through(self):
        """Successful calls should work normally"""
        mock_func = Mock(return_value="success")
        
        result = self.cb.call(mock_func, "arg1", key="value")
        
        self.assertEqual(result, "success")
        mock_func.assert_called_once_with("arg1", key="value")
        self.assertEqual(self.cb.stats.successful_requests, 1)
        self.assertEqual(self.cb.stats.failed_requests, 0)
    
    def test_failed_call_records_failure(self):
        """Failed calls should be tracked"""
        mock_func = Mock(side_effect=Exception("Service down"))
        
        with self.assertRaises(Exception) as context:
            self.cb.call(mock_func)
        
        self.assertEqual(str(context.exception), "Service down")
        self.assertEqual(self.cb.stats.failed_requests, 1)
        self.assertEqual(len(self.cb.call_history), 1)
        self.assertFalse(self.cb.call_history[0])  # False = failure
    
    def test_circuit_opens_after_threshold_failures(self):
        """Circuit should open after exceeding failure threshold"""
        mock_func = Mock(side_effect=Exception("Failure"))
        
        # Cause enough failures to trip the circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        self.assertEqual(self.cb.state, CircuitState.OPEN)
        self.assertIsNotNone(self.cb.opened_at)
    
    def test_open_circuit_rejects_requests(self):
        """Open circuit should reject requests without calling function"""
        mock_func = Mock(side_effect=Exception("Failure"))
        
        # Trip the circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        # Reset mock to verify it's not called
        mock_func.reset_mock()
        
        # Try to make a call while circuit is open
        with self.assertRaises(CircuitBreakerOpenException):
            self.cb.call(mock_func)
        
        # Function should NOT have been called
        mock_func.assert_not_called()
        self.assertEqual(self.cb.stats.rejected_requests, 1)
    
    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit should enter HALF_OPEN state after timeout"""
        mock_func = Mock(side_effect=Exception("Failure"))
        
        # Open the circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        self.assertEqual(self.cb.state, CircuitState.OPEN)
        
        # Wait for timeout
        time.sleep(self.config.timeout + 0.1)
        
        # Mock successful response
        mock_func.side_effect = None
        mock_func.return_value = "success"
        
        # Next call should transition to HALF_OPEN
        result = self.cb.call(mock_func)
        
        self.assertEqual(result, "success")
        self.assertEqual(self.cb.state, CircuitState.HALF_OPEN)
    
    def test_half_open_closes_after_success_threshold(self):
        """HALF_OPEN should close after enough successes"""
        mock_func = Mock(side_effect=Exception("Failure"))
        
        # Open the circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        # Wait for timeout
        time.sleep(self.config.timeout + 0.1)
        
        # Mock successful responses
        mock_func.side_effect = None
        mock_func.return_value = "success"
        
        # Make enough successful calls to close circuit
        for _ in range(self.config.success_threshold):
            self.cb.call(mock_func)
        
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        self.assertIsNone(self.cb.opened_at)
    
    def test_half_open_reopens_on_single_failure(self):
        """HALF_OPEN should immediately reopen on any failure"""
        mock_func = Mock(side_effect=Exception("Failure"))
        
        # Open the circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        # Wait for timeout
        time.sleep(self.config.timeout + 0.1)
        
        # First call succeeds (enters HALF_OPEN)
        mock_func.side_effect = None
        mock_func.return_value = "success"
        self.cb.call(mock_func)
        self.assertEqual(self.cb.state, CircuitState.HALF_OPEN)
        
        # Second call fails
        mock_func.side_effect = Exception("Still broken")
        with self.assertRaises(Exception):
            self.cb.call(mock_func)
        
        # Should be OPEN again
        self.assertEqual(self.cb.state, CircuitState.OPEN)


class TestCircuitBreakerSlidingWindow(unittest.TestCase):
    """Test sliding window behavior"""
    
    def setUp(self):
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            window_size=5,
            timeout=1.0
        )
        self.cb = CircuitBreaker(self.config)
    
    def test_old_failures_dont_count(self):
        """Old failures should be evicted from sliding window"""
        mock_func = Mock()
        
        # Record 2 failures
        mock_func.side_effect = Exception("Fail")
        for _ in range(2):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        # Record 5 successes (fills window, evicting old failures)
        mock_func.side_effect = None
        mock_func.return_value = "success"
        for _ in range(5):
            self.cb.call(mock_func)
        
        # Circuit should still be CLOSED (old failures don't count)
        self.assertEqual(self.cb.state, CircuitState.CLOSED)
        
        # Window should only contain successes
        self.assertTrue(all(self.cb.call_history))
    
    def test_window_size_is_respected(self):
        """Call history should not exceed window size"""
        mock_func = Mock(return_value="success")
        
        # Make more calls than window size
        for _ in range(10):
            self.cb.call(mock_func)
        
        # History should be limited to window size
        self.assertEqual(len(self.cb.call_history), self.config.window_size)


class TestCircuitBreakerThreadSafety(unittest.TestCase):
    """Test thread safety under concurrent load"""
    
    def setUp(self):
        self.config = CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=1.0,
            window_size=10
        )
        self.cb = CircuitBreaker(self.config)
    
    def test_concurrent_successful_calls(self):
        """Multiple threads making successful calls"""
        mock_func = Mock(return_value="success")
        num_threads = 10
        calls_per_thread = 5
        
        def worker():
            for _ in range(calls_per_thread):
                self.cb.call(mock_func)
                time.sleep(0.01)
        
        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All calls should have been recorded
        expected_total = num_threads * calls_per_thread
        self.assertEqual(self.cb.stats.total_requests, expected_total)
        self.assertEqual(self.cb.stats.successful_requests, expected_total)
    
    def test_concurrent_calls_during_state_transition(self):
        """Multiple threads calling during circuit state changes"""
        mock_func = Mock()
        results = {"success": 0, "failure": 0, "rejected": 0}
        lock = threading.Lock()
        
        def worker(should_fail):
            try:
                if should_fail:
                    mock_func.side_effect = Exception("Fail")
                else:
                    mock_func.side_effect = None
                    mock_func.return_value = "success"
                
                self.cb.call(mock_func)
                with lock:
                    results["success"] += 1
            except CircuitBreakerOpenException:
                with lock:
                    results["rejected"] += 1
            except Exception:
                with lock:
                    results["failure"] += 1
        
        # Create mix of failing and successful threads
        threads = []
        for i in range(20):
            should_fail = i < 10  # First 10 fail, rest succeed
            threads.append(threading.Thread(target=worker, args=(should_fail,)))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no crashes and all requests accounted for
        total = results["success"] + results["failure"] + results["rejected"]
        self.assertEqual(total, 20)


class TestCircuitBreakerStatistics(unittest.TestCase):
    """Test statistics and monitoring"""
    
    def setUp(self):
        self.config = CircuitBreakerConfig(
            failure_threshold=3,
            timeout=2.0
        )
        self.cb = CircuitBreaker(self.config)
    
    def test_stats_track_all_request_types(self):
        """Statistics should track successful, failed, and rejected requests"""
        mock_func = Mock()
        
        # 2 successes
        mock_func.return_value = "success"
        self.cb.call(mock_func)
        self.cb.call(mock_func)
        
        # 3 failures (opens circuit)
        mock_func.side_effect = Exception("Fail")
        for _ in range(3):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        # 2 rejections (circuit open)
        for _ in range(2):
            with self.assertRaises(CircuitBreakerOpenException):
                self.cb.call(mock_func)
        
        stats = self.cb.get_stats()
        self.assertEqual(stats["total_requests"], 7)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 3)
        self.assertEqual(stats["rejected"], 2)
    
    def test_failure_rate_calculation(self):
        """Statistics should calculate failure rate correctly"""
        mock_func = Mock()
        
        # 7 successes
        mock_func.return_value = "success"
        for _ in range(7):
            self.cb.call(mock_func)
        
        # 3 failures
        mock_func.side_effect = Exception("Fail")
        for _ in range(3):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        stats = self.cb.get_stats()
        # 3 failures out of 10 total = 30%
        self.assertEqual(stats["failure_rate"], "30.0%")
    
    def test_time_until_retry_when_open(self):
        """Should report time remaining until retry attempt"""
        mock_func = Mock(side_effect=Exception("Fail"))
        
        # Open circuit
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        stats = self.cb.get_stats()
        
        # Should report time close to full timeout
        self.assertGreater(stats["time_until_retry"], 1.5)
        self.assertLess(stats["time_until_retry"], 2.1)
        
        # Wait a bit
        time.sleep(0.5)
        
        stats = self.cb.get_stats()
        # Time should have decreased
        self.assertGreater(stats["time_until_retry"], 1.0)
        self.assertLess(stats["time_until_retry"], 1.6)
    
    def test_state_changes_are_counted(self):
        """Should track how many times state changes"""
        mock_func = Mock(side_effect=Exception("Fail"))
        
        initial_changes = self.cb.stats.state_changes
        
        # Open circuit (1 change)
        for _ in range(self.config.failure_threshold):
            with self.assertRaises(Exception):
                self.cb.call(mock_func)
        
        self.assertEqual(self.cb.stats.state_changes, initial_changes + 1)
        
        # Wait and transition to half-open (2nd change)
        time.sleep(self.config.timeout + 0.1)
        mock_func.side_effect = None
        mock_func.return_value = "success"
        self.cb.call(mock_func)
        
        self.assertEqual(self.cb.stats.state_changes, initial_changes + 2)


class TestCircuitBreakerEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_exactly_threshold_failures_opens_circuit(self):
        """Circuit should open at exactly the threshold, not after"""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)
        mock_func = Mock(side_effect=Exception("Fail"))
        
        # First 2 failures - still closed
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(mock_func)
        self.assertEqual(cb.state, CircuitState.CLOSED)
        
        # 3rd failure - should open
        with self.assertRaises(Exception):
            cb.call(mock_func)
        self.assertEqual(cb.state, CircuitState.OPEN)
    
    def test_manual_reset_clears_state(self):
        """Manual reset should clear all state"""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)
        mock_func = Mock(side_effect=Exception("Fail"))
        
        # Open circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(mock_func)
        
        self.assertEqual(cb.state, CircuitState.OPEN)
        
        # Manual reset
        cb.reset()
        
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertIsNone(cb.opened_at)
        self.assertEqual(len(cb.call_history), 0)
    
    def test_zero_timeout_allows_immediate_retry(self):
        """Timeout of 0 should allow immediate retry"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout=0.0
        )
        cb = CircuitBreaker(config)
        mock_func = Mock(side_effect=Exception("Fail"))
        
        # Open circuit
        for _ in range(2):
            with self.assertRaises(Exception):
                cb.call(mock_func)
        
        # Should immediately transition to half-open
        mock_func.side_effect = None
        mock_func.return_value = "success"
        cb.call(mock_func)
        
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)


def run_tests():
    """Run all tests with verbose output"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerSlidingWindow))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerThreadSafety))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)