"""Testes de retry e timeout."""
import pytest
from integration.resilience import RetryManager, TimeoutHandler


def test_retry_succeeds_after_failures():
    mgr = RetryManager(max_retries=3, base_delay=0.01)
    count = [0]
    def fn():
        count[0] += 1
        if count[0] < 3:
            raise ValueError("temporary")
        return "ok"
    assert mgr.execute_with_retry(fn) == "ok"
    assert count[0] == 3


def test_retry_fails_after_max_retries():
    mgr = RetryManager(max_retries=2, base_delay=0.01)
    count = [0]
    def fn():
        count[0] += 1
        raise ValueError("permanent")
    with pytest.raises(ValueError):
        mgr.execute_with_retry(fn)
    assert count[0] == 3  # 1 + 2 retries


def test_retry_respects_retryable_exceptions():
    mgr = RetryManager(max_retries=3, base_delay=0.01, retryable_exceptions=[ValueError])
    count = [0]
    def fn():
        count[0] += 1
        if count[0] == 1:
            raise ValueError("retryable")
        raise TypeError("not retryable")
    with pytest.raises(TypeError):
        mgr.execute_with_retry(fn)
    assert count[0] == 2


def test_timeout_cancels_slow_operation():
    import time
    handler = TimeoutHandler(timeout_seconds=0.1)
    def slow():
        time.sleep(1.0)
        return "done"
    with pytest.raises(TimeoutError):
        handler.execute_with_timeout(slow)


def test_timeout_allows_fast_operation():
    handler = TimeoutHandler(timeout_seconds=1.0)
    assert handler.execute_with_timeout(lambda: 42) == 42


def test_timeout_propagates_exception():
    handler = TimeoutHandler(timeout_seconds=1.0)
    def failing():
        raise RuntimeError("oops")
    with pytest.raises(RuntimeError, match="oops"):
        handler.execute_with_timeout(failing)
