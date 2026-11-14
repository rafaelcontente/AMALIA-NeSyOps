"""Testes de rate limiting para APIGateway."""
import pytest
import time
from integration.api import APIGateway, DecisionRequest
from integration.idempotency import IdempotencyManager
from integration.tenant import TenantManager
from gate.gate import Gate
from gate.validator import GateValidator

def test_rate_limiting_blocks_excessive_requests():
    """Rate limit deve bloquear requests excessivos."""
    tm = TenantManager()
    tm.register_tenant("tenant-1", {"name": "Test"})
    tm.register_user("user-1", "tenant-1", ["read", "write"])
    
    gateway = APIGateway(Gate(GateValidator()), IdempotencyManager(), tm)
    gateway.max_requests_per_second = 5  # Limite baixo para teste
    
    # Fazer 5 requests (deve passar)
    for i in range(5):
        req = DecisionRequest(
            request_id=f"req-{i}",
            entity_id="tenant-1",
            user_id="user-1",
            document_text=f"Request {i}",
            metadata={}
        )
        res = gateway.submit_decision(req)
        # Os primeiros 5 devem ser processados (não failed por rate limit)
        if i < 5:
            assert gateway.requests[res.trace_id]["status"] != "failed" or "Rate limit" not in gateway.requests[res.trace_id].get("error", "")
    
    # 6º request deve ser bloqueado
    req = DecisionRequest(
        request_id="req-6",
        entity_id="tenant-1",
        user_id="user-1",
        document_text="Request 6",
        metadata={}
    )
    res = gateway.submit_decision(req)
    assert gateway.requests[res.trace_id]["status"] == "failed"
    assert "Rate limit" in gateway.requests[res.trace_id]["error"]

def test_rate_limiting_resets_after_window():
    """Rate limit deve resetar após a janela de tempo."""
    tm = TenantManager()
    tm.register_tenant("tenant-1", {"name": "Test"})
    tm.register_user("user-1", "tenant-1", ["read", "write"])
    
    gateway = APIGateway(Gate(GateValidator()), IdempotencyManager(), tm)
    gateway.max_requests_per_second = 2
    
    # Fazer 2 requests (limite atingido)
    for i in range(2):
        req = DecisionRequest(
            request_id=f"req-{i}",
            entity_id="tenant-1",
            user_id="user-1",
            document_text=f"Request {i}",
            metadata={}
        )
        gateway.submit_decision(req)
    
    # 3º request deve ser bloqueado
    req = DecisionRequest(
        request_id="req-3",
        entity_id="tenant-1",
        user_id="user-1",
        document_text="Request 3",
        metadata={}
    )
    res = gateway.submit_decision(req)
    assert "Rate limit" in gateway.requests[res.trace_id]["error"]
    
    # Aguardar 1.1 segundos (janela é 1 segundo)
    time.sleep(1.1)
    
    # Novo request deve passar
    req = DecisionRequest(
        request_id="req-4",
        entity_id="tenant-1",
        user_id="user-1",
        document_text="Request 4",
        metadata={}
    )
    res = gateway.submit_decision(req)
    # Não deve ter erro de rate limit
    if gateway.requests[res.trace_id]["status"] == "failed":
        assert "Rate limit" not in gateway.requests[res.trace_id]["error"]

def test_rate_limiting_per_entity():
    """Rate limit deve ser por entity_id, não global."""
    tm = TenantManager()
    tm.register_tenant("tenant-1", {"name": "Tenant 1"})
    tm.register_tenant("tenant-2", {"name": "Tenant 2"})
    tm.register_user("user-1", "tenant-1", ["read", "write"])
    tm.register_user("user-2", "tenant-2", ["read", "write"])
    
    gateway = APIGateway(Gate(GateValidator()), IdempotencyManager(), tm)
    gateway.max_requests_per_second = 2
    
    # Tenant 1 atinge o limite
    for i in range(3):
        req = DecisionRequest(
            request_id=f"t1-req-{i}",
            entity_id="tenant-1",
            user_id="user-1",
            document_text=f"T1 Request {i}",
            metadata={}
        )
        gateway.submit_decision(req)
    
    # Tenant 2 deve continuar a funcionar
    req = DecisionRequest(
        request_id="t2-req-1",
        entity_id="tenant-2",
        user_id="user-2",
        document_text="T2 Request 1",
        metadata={}
    )
    res = gateway.submit_decision(req)
    # Não deve ter erro de rate limit (tenant diferente)
    if gateway.requests[res.trace_id]["status"] == "failed":
        assert "Rate limit" not in gateway.requests[res.trace_id]["error"]
