"""
Testes de carga e performance do Gate de decisão.

Invariantes de performance (em ambiente de CI):
1. Throughput > 500 req/s para decisões determinísticas.
2. Latência p95 < 50ms por avaliação.
3. O overhead de validação não deve crescer linearmente com o tamanho do payload (até 10KB).
"""
import time
import pytest
from core.models import Proposal, TraceID, VerdictStatus
from gate.gate import Gate
from gate.validator import GateValidator


@pytest.fixture
def gate():
    return Gate(GateValidator())


@pytest.fixture
def valid_proposal():
    return Proposal(
        trace_id=TraceID(),
        agent="benchmark-agent",
        content={"idade": 25, "documento": "valido.pdf", "valor": 1000},
        confidence=0.95,
    )


@pytest.fixture
def invalid_proposal():
    return Proposal(
        trace_id=TraceID(),
        agent="benchmark-agent",
        content={"idade": 15, "documento": "injetar<script>", "valor": -500},
        confidence=0.95,
    )


def test_gate_throughput_and_latency_valid(gate, valid_proposal):
    """Mede throughput e latência p95 para o caminho feliz (aprovação)."""
    iterations = 5000
    latencies_ms = []
    
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        # Criar novo trace_id para simular requests únicos
        p = Proposal(
            trace_id=TraceID(),
            agent=valid_proposal.agent,
            content=valid_proposal.content,
            confidence=valid_proposal.confidence,
        )
        
        # Medir apenas a avaliação
        t0 = time.perf_counter()
        gate.evaluate(p)
        t1 = time.perf_counter()
        
        latencies_ms.append((t1 - t0) * 1000)
        
    end_time = time.perf_counter()
    total_time_sec = end_time - start_time
    
    # Calcular métricas
    throughput_rps = iterations / total_time_sec
    avg_latency_ms = sum(latencies_ms) / len(latencies_ms)
    p95_latency_ms = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    
    # Invariantes de performance (limites conservadores para CI)
    assert throughput_rps > 500, f"Throughput muito baixo: {throughput_rps:.2f} req/s"
    assert p95_latency_ms < 50.0, f"Latência p95 muito alta: {p95_latency_ms:.2f} ms"
    
    # Log para debugging em caso de falha no CI
    print(f"\n[PERF] Valid Path: {throughput_rps:.2f} req/s, avg: {avg_latency_ms:.2f}ms, p95: {p95_latency_ms:.2f}ms")


def test_gate_throughput_and_latency_invalid(gate, invalid_proposal):
    """Mede throughput e latência p95 para o caminho de rejeição (falha rápida)."""
    iterations = 5000
    latencies_ms = []
    
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        p = Proposal(
            trace_id=TraceID(),
            agent=invalid_proposal.agent,
            content=invalid_proposal.content,
            confidence=invalid_proposal.confidence,
        )
        
        t0 = time.perf_counter()
        gate.evaluate(p)
        t1 = time.perf_counter()
        
        latencies_ms.append((t1 - t0) * 1000)
        
    end_time = time.perf_counter()
    total_time_sec = end_time - start_time
    
    throughput_rps = iterations / total_time_sec
    avg_latency_ms = sum(latencies_ms) / len(latencies_ms)
    p95_latency_ms = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    
    # O caminho de rejeição deve ser ainda mais rápido (fail-fast)
    assert throughput_rps > 500, f"Throughput muito baixo: {throughput_rps:.2f} req/s"
    assert p95_latency_ms < 50.0, f"Latência p95 muito alta: {p95_latency_ms:.2f}ms"
    
    print(f"\n[PERF] Invalid Path: {throughput_rps:.2f} req/s, avg: {avg_latency_ms:.2f}ms, p95: {p95_latency_ms:.2f}ms")


def test_gate_latency_with_large_payload(gate):
    """Garante que payloads maiores (até 10KB) não degradam a performance linearmente."""
    # Criar payload de ~10KB
    large_content = {"data": "x" * 10000, "idade": 25}
    
    iterations = 1000
    latencies_ms = []
    
    for _ in range(iterations):
        p = Proposal(
            trace_id=TraceID(),
            agent="benchmark-agent",
            content=large_content,
            confidence=0.95,
        )
        
        t0 = time.perf_counter()
        gate.evaluate(p)
        t1 = time.perf_counter()
        
        latencies_ms.append((t1 - t0) * 1000)
        
    p95_latency_ms = sorted(latencies_ms)[int(len(latencies_ms) * 0.95)]
    
    # A latência não deve explodir com 10KB de dados
    assert p95_latency_ms < 100.0, f"Latência p95 com payload grande muito alta: {p95_latency_ms:.2f}ms"
    
    print(f"\n[PERF] Large Payload (10KB): p95: {p95_latency_ms:.2f}ms")
