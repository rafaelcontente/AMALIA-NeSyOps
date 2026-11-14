"""Testes do Ollama adapter com circuit breaker."""
import pytest
import os
from unittest.mock import Mock, patch
from agents.ollama_adapter import OllamaAdapter, CircuitBreaker


@pytest.fixture
def adapter():
    return OllamaAdapter(model="test-model", timeout=5.0)


@pytest.fixture
def circuit_breaker():
    return CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)


def test_circuit_breaker_starts_closed(circuit_breaker):
    assert circuit_breaker.state == CircuitBreaker.CLOSED
    assert circuit_breaker.allow_request() is True


def test_circuit_breaker_opens_after_failures(circuit_breaker):
    for _ in range(3):
        circuit_breaker.record_failure()
    assert circuit_breaker.state == CircuitBreaker.OPEN
    assert circuit_breaker.allow_request() is False


def test_circuit_breaker_recovers_after_timeout(circuit_breaker):
    for _ in range(3):
        circuit_breaker.record_failure()
    assert circuit_breaker.state == CircuitBreaker.OPEN
    circuit_breaker.last_failure_time -= 2.0
    assert circuit_breaker.allow_request() is True
    assert circuit_breaker.state == CircuitBreaker.HALF_OPEN


def test_circuit_breaker_resets_on_success(circuit_breaker):
    circuit_breaker.record_failure()
    circuit_breaker.record_success()
    assert circuit_breaker.failure_count == 0
    assert circuit_breaker.state == CircuitBreaker.CLOSED


def test_ollama_adapter_generate_mocked(adapter):
    mock_response = Mock()
    mock_response.json.return_value = {"response": "Test response", "model": "test-model"}
    mock_response.raise_for_status = Mock()
    
    with patch("requests.post", return_value=mock_response):
        result = adapter.generate("test prompt", "trace-1")
    
    assert result["status"] == "success"
    assert result["content"] == "Test response"
    assert result["model"] == "test-model"
    assert "duration_ms" in result


def test_ollama_adapter_handles_timeout(adapter):
    def slow_request(*args, **kwargs):
        import time
        time.sleep(10)
    
    with patch("requests.post", side_effect=slow_request):
        result = adapter.generate("test prompt", "trace-1")
    
    assert result["status"] == "error"
    assert "timeout" in result["error"].lower() or "timed out" in result["error"].lower()


def test_ollama_adapter_circuit_breaker_opens_on_failures(adapter):
    with patch("requests.post", side_effect=Exception("Connection refused")):
        for _ in range(3):
            adapter.generate("test", "trace-1")
    
    assert adapter.circuit_breaker.state == CircuitBreaker.OPEN
    result = adapter.generate("test", "trace-1")
    assert result["status"] == "error"
    assert "Circuit breaker open" in result["error"]


def test_ollama_adapter_is_healthy(adapter):
    mock_response = Mock()
    mock_response.status_code = 200
    with patch("requests.get", return_value=mock_response):
        assert adapter.is_healthy() is True


def test_ollama_adapter_is_unhealthy(adapter):
    with patch("requests.get", side_effect=Exception("Connection refused")):
        assert adapter.is_healthy() is False


def test_ollama_adapter_skip_if_no_model():
    if not os.getenv("OLLAMA_MODEL"):
        pytest.skip("OLLAMA_MODEL not set, skipping real LLM test")
    adapter = OllamaAdapter()
    if not adapter.is_healthy():
        pytest.skip("Ollama not available")
    result = adapter.generate("Diz olá em português.", "trace-test")
    assert result["status"] == "success"
    assert len(result["content"]) > 0
