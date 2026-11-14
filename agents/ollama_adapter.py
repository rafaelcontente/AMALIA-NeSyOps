"""Ollama LLM adapter with circuit breaker and retry."""
import os
import time
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from integration.resilience import RetryManager, TimeoutHandler


class CircuitBreaker:
    """Circuit breaker para proteger contra falhas repetidas do LLM."""
    
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
    
    def allow_request(self) -> bool:
        """Verifica se o request pode prosseguir."""
        if self.state == self.CLOSED:
            return True
        elif self.state == self.OPEN:
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Regista sucesso e reseta o circuit breaker."""
        self.failure_count = 0
        self.state = self.CLOSED
    
    def record_failure(self):
        """Regista falha e possivelmente abre o circuito."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN


class OllamaAdapter:
    """
    Adapter para Ollama LLM com resiliência.
    
    Configuração via env vars:
    - OLLAMA_HOST: http://localhost:11434 (default)
    - OLLAMA_MODEL: qwen2.5:7b (default)
    - OLLAMA_TIMEOUT: 30 (default, seconds)
    """
    
    def __init__(
        self,
        model: str = None,
        host: str = None,
        timeout: float = None,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
    ):
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = timeout or float(os.getenv("OLLAMA_TIMEOUT", "30"))
        self.circuit_breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        self.retry_manager = RetryManager(max_retries=2, base_delay=1.0)
        self.timeout_handler = TimeoutHandler(timeout_seconds=self.timeout)
    
    def generate(self, prompt: str, trace_id: str) -> Dict[str, Any]:
        """
        Gera resposta do LLM com resiliência.
        
        Returns:
            {"status": "success", "content": "...", "model": "...", "duration_ms": ...}
            ou {"status": "error", "error": "...", "circuit_state": "..."}
        """
        if not self.circuit_breaker.allow_request():
            return {
                "status": "error",
                "error": "Circuit breaker open",
                "circuit_state": self.circuit_breaker.state,
            }
        
        try:
            result = self.retry_manager.execute_with_retry(
                lambda: self.timeout_handler.execute_with_timeout(
                    lambda: self._call_ollama(prompt)
                )
            )
            self.circuit_breaker.record_success()
            return result
        except Exception as e:
            self.circuit_breaker.record_failure()
            return {
                "status": "error",
                "error": str(e),
                "circuit_state": self.circuit_breaker.state,
            }
    
    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Chama a API do Ollama."""
        start_time = time.time()
        
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        
        data = response.json()
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "content": data.get("response", ""),
            "model": self.model,
            "duration_ms": round(duration_ms, 2),
        }
    
    def is_healthy(self) -> bool:
        """Verifica se o Ollama está acessível."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
