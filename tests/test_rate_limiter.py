import pytest
import time
from decimal import Decimal
import sys
from pathlib import Path

# Add parent directory to path to import from utils - 
# Docs: https://docs.pytest.org/en/latest/explanation/pythonpath.html
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.rate_limiter_dec import rate_limiter, TokenBucketTooEarly


class TestRateLimiter:
    def test_initialization_validation(self):
        #Test that invalid parameters raise ValueError
        with pytest.raises(ValueError, match="Value must be greater than 0"):
            @rate_limiter(capacity=0, tokens_per_minute=1.0)
            def dummy():
                pass
        
        with pytest.raises(ValueError, match="Value must be greater than 0"):
            @rate_limiter(capacity=-5, tokens_per_minute=1.0)
            def dummy():
                pass
        
        with pytest.raises(ValueError, match="Value must be greater than 0"):
            @rate_limiter(capacity=5, tokens_per_minute=0.0)
            def dummy():
                pass
        
        with pytest.raises(ValueError, match="Value must be greater than 0"):
            @rate_limiter(capacity=5, tokens_per_minute=-1.0)
            def dummy():
                pass
    
    def test_first_call_succeeds(self):
        # Test that the first call succeeds (bucket starts full)
        call_count = 0
        
        @rate_limiter(capacity=2, tokens_per_minute=60.0)
        def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_func()
        print("call_count: ", call_count)
        assert result == "success"
        assert call_count == 1
    
    def test_burst_capacity(self):
        # Test that burst calls up to capacity succeed
        call_count = 0
        
        @rate_limiter(capacity=3, tokens_per_minute=60.0)
        def test_func():
            nonlocal call_count
            call_count += 1
            return call_count
        
        # Should allow 3 rapid calls (full capacity)
        assert test_func() == 1
        assert test_func() == 2
        assert test_func() == 3
        
        # 4th call should fail
        with pytest.raises(TokenBucketTooEarly):
            test_func()
    
    
    def test_at_most_one_call_per_two_seconds(self):
        # Test that the rate limiter enforces at most 1 call every 2 seconds
        call_count = 0
        call_times = []
        
        @rate_limiter(capacity=1, tokens_per_minute=30.0)  # 0.5 tokens/second = 2 seconds per token
        def test_func():
            nonlocal call_count
            call_count += 1
            call_times.append(time.monotonic())
            return call_count
        
        # First call should succeed immediately
        assert test_func() == 1
        first_call_time = call_times[0]
        
        # Immediate second call (less than 2 seconds) should fail
        with pytest.raises(TokenBucketTooEarly, match="Insufficient tokens"):
            test_func()
        
        # Wait just under 2 seconds and should still fail
        time.sleep(1.9)
        with pytest.raises(TokenBucketTooEarly):
            test_func()
        
        # Wait a bit more to cross the 2 second time gap
        time.sleep(0.2)
        assert test_func() == 2
        second_call_time = call_times[1]
        assert second_call_time - first_call_time >= 2.0
        
        # Immediate third call should fail again
        with pytest.raises(TokenBucketTooEarly):
            test_func()
        
        # Wait exactly 2 seconds and should succeed
        time.sleep(2.0)
        assert test_func() == 3
        third_call_time = call_times[2]
        assert third_call_time - second_call_time >= 2.0
        
        # Immediate fourth call should fail again
        with pytest.raises(TokenBucketTooEarly):
            test_func()
        
        # Wait 2+ seconds and should succeed
        time.sleep(2.1)
        assert test_func() == 4
        
        # Verify that we had at least 2 second time gap between each successful call
        for i in range(1, len(call_times)):
            interval = call_times[i] - call_times[i-1]
            assert interval >= 2.0, f"Interval between calls {i} and {i+1} was {interval:.3f} seconds, expected >= 2.0"
    
    
    def test_multiple_decorators_independently(self):
        # Test that multiple decorated functions have independent buckets
        call_count_1 = 0
        call_count_2 = 0
        
        @rate_limiter(capacity=2, tokens_per_minute=60.0)
        def func1():
            nonlocal call_count_1
            call_count_1 += 1
            return call_count_1
        
        @rate_limiter(capacity=2, tokens_per_minute=60.0)
        def func2():
            nonlocal call_count_2
            call_count_2 += 1
            return call_count_2
        
        # Exhaust func1's tokens to make func2 wait for the rate limiter
        func1()
        func1()
        
        # func2 should still work
        assert func2() == 1
        assert func2() == 2
    

class TestMultiThreadFunctionalities:

    def test_multi_calls_to_system(self):
        
        # call the coinbase data fetch and gemini data fetch in parallel multiple times
        from utils.data_loader import get_coinbase_data
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        COINBASE_API = os.getenv("COINBASE_API")
        
        if not COINBASE_API:
            pytest.skip("COINBASE_API not configured in .env")
        
        call_times = []
        
        # Make 3 sequential calls. For 4 it fails.
        for i in range(3):
            start_time = time.monotonic()
            try:
                data = get_coinbase_data(COINBASE_API)
                call_times.append(time.monotonic())
                print(f"Call {i+1} succeeded at {call_times[-1]:.2f}")
                assert data is not None
            except Exception as e:
                if "Insufficient tokens" in str(e):
                    print(f"Call {i+1} was rate limited as expected")
                    # This should only happen if we're calling too fast
                    assert i > 0, "First call should never be rate limited"
                else:
                    raise
        
        # Verify intervals between successful calls are at least 2 seconds
        for i in range(1, len(call_times)):
            interval = call_times[i] - call_times[i-1]
            print(f"Interval between call {i} and {i+1}: {interval:.2f} seconds")
            assert interval >= 2.0, f"Expected at least 2 seconds between calls, got {interval:.2f}"

    def test_multi_thread_calls_to_system(self):
        from utils.data_loader import get_coinbase_data
        import os
        from dotenv import load_dotenv
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        load_dotenv()
        COINBASE_API = os.getenv("COINBASE_API")
        
        if not COINBASE_API:
            pytest.skip("COINBASE_API not configured in .env")
        
        def get_coinbase_data_with_delay(delay):
            time.sleep(delay)
            data = get_coinbase_data(COINBASE_API)
            print("data length: ", len(data))
            return time.monotonic()

        with ThreadPoolExecutor(max_workers=5) as executor:
            coinbase_future_1 = executor.submit(get_coinbase_data_with_delay, 0.0)
            coinbase_future_2 = executor.submit(get_coinbase_data_with_delay, 2.5)
            coinbase_future_3 = executor.submit(get_coinbase_data_with_delay, 5.0)
            # coinbase_future_4 = executor.submit(get_coinbase_data, COINBASE_API)
            # coinbase_future_5 = executor.submit(get_coinbase_data, COINBASE_API)

            for future in as_completed([coinbase_future_1, coinbase_future_2, coinbase_future_3]):
                try:
                    data = future.result()
                    print("time taken: ", data)
                    
                except Exception as e:
                    print("Error : ", e)
                    exit(1)