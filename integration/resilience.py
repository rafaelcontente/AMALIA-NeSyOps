"""Padrões de resiliência: retry com backoff e timeout."""
import time
import threading
from typing import Callable, List, Type, Any

class RetryManager:
    """Retry com exponential backoff e jitter."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 0.1,
        retryable_exceptions: List[Type[Exception]] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retryable_exceptions = tuple(retryable_exceptions or [Exception])
    
    def execute_with_retry(self, fn: Callable[..., Any]) -> Any:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return fn()
            except self.retryable_exceptions as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise
        raise last_error  # type: ignore


class TimeoutHandler:
    """Executa funções com timeout."""
    
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds
    
    def execute_with_timeout(self, fn: Callable[..., Any]) -> Any:
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = fn()
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=self.timeout_seconds)
        
        if thread.is_alive():
            raise TimeoutError(f"Operation timed out after {self.timeout_seconds}s")
        
        if error[0]:
            raise error[0]
        
        return result[0]
