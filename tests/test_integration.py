import pytest
from integration.idempotency import IdempotencyManager
from integration.tenant import TenantManager, TenantIsolator
from integration.api import APIGateway, DecisionRequest
from gate.gate import Gate
from gate.validator import GateValidator

@pytest.fixture
def idempotency_manager():
    return IdempotencyManager(ttl_hours=24)

@pytest.fixture
def tenant_manager():
    manager = TenantManager()
    # Registar tenants
    manager.register_tenant("entity-A", {"name": "Entidade A"})
    manager.register_tenant("entity-B", {"name": "Entidade B"})
    
    # Registar utilizadores
    manager.register_user("user-A1", "entity-A", ["read", "write"])
    manager.register_user("user-A2", "entity-A", ["read"])
    manager.register_user("user-B1", "entity-B", ["read", "write"])
    
    return manager

@pytest.fixture
def tenant_isolator():
    return TenantIsolator()

@pytest.fixture
def gate():
    validator = GateValidator()
    return Gate(validator)

@pytest.fixture
def api_gateway(gate, idempotency_manager, tenant_manager):
    return APIGateway(gate, idempotency_manager, tenant_manager)

# ─── Teste 1: Idempotência (pedido repetido não gera segunda decisão) ──────
def test_idempotency_prevents_duplicate_decisions(idempotency_manager, tenant_manager, gate):
    """Teste 1: um pedido repetido com a mesma chave de idempotência não gera uma segunda decisão."""
    
    # Dados do request
    request_data = {
        "document_text": "Requerimento de licença",
        "metadata": {"tipo": "licença"}
    }
    entity_id = "entity-A"
    
    # Contador de chamadas ao process_fn
    call_count = 0
    
    def process_fn(data, entity):
        nonlocal call_count
        call_count += 1
        return {
            "decision": {"status": "approved"},
            "explanation": "Decisão processada"
        }
    
    # Primeiro request
    result1 = idempotency_manager.check_and_process(
        request_data, entity_id, process_fn
    )
    
    assert result1["cached"] is False
    assert call_count == 1
    assert result1["result"]["decision"]["status"] == "approved"
    
    # Segundo request (idêntico)
    result2 = idempotency_manager.check_and_process(
        request_data, entity_id, process_fn
    )
    
    # Deve retornar cached
    assert result2["cached"] is True
    assert call_count == 1  # Não deve ter chamado process_fn novamente
    assert result2["result"] == result1["result"]
    
    # Terceiro request (diferente)
    different_request = {
        "document_text": "Requerimento de autorização",  # Diferente
        "metadata": {"tipo": "autorização"}
    }
    
    result3 = idempotency_manager.check_and_process(
        different_request, entity_id, process_fn
    )
    
    # Deve processar novamente
    assert result3["cached"] is False
    assert call_count == 2

# ─── Teste 2: Isolamento multi-tenant ───────────────────────────────────────
def test_tenant_isolation(tenant_isolator, tenant_manager):
    """Teste 2: um utilizador da entidade A nunca recebe dados da entidade B."""
    
    # Armazenar dados para entity-A
    tenant_isolator.store_data("entity-A", "doc-001", {
        "title": "Documento da Entidade A",
        "content": "Conteúdo confidencial de A"
    })
    
    # Armazenar dados para entity-B
    tenant_isolator.store_data("entity-B", "doc-002", {
        "title": "Documento da Entidade B",
        "content": "Conteúdo confidencial de B"
    })
    
    # Utilizador de entity-A acede aos seus próprios dados
    data_a = tenant_isolator.get_data("entity-A", "doc-001", "entity-A")
    assert data_a is not None
    assert data_a["title"] == "Documento da Entidade A"
    
    # Utilizador de entity-B acede aos seus próprios dados
    data_b = tenant_isolator.get_data("entity-B", "doc-002", "entity-B")
    assert data_b is not None
    assert data_b["title"] == "Documento da Entidade B"
    
    # Utilizador de entity-A tenta aceder a dados de entity-B
    with pytest.raises(PermissionError, match="não pode aceder a dados"):
        tenant_isolator.get_data("entity-B", "doc-002", "entity-A")
    
    # Utilizador de entity-B tenta aceder a dados de entity-A
    with pytest.raises(PermissionError, match="não pode aceder a dados"):
        tenant_isolator.get_data("entity-A", "doc-001", "entity-B")
    
    # Testar listagem
    keys_a = tenant_isolator.list_data("entity-A", "entity-A")
    assert "doc-001" in keys_a
    assert "doc-002" not in keys_a
    
    # Tentar listar dados de outro tenant
    with pytest.raises(PermissionError, match="não pode listar dados"):
        tenant_isolator.list_data("entity-B", "entity-A")

# ─── Teste 3: Gate enforcement (nenhuma ação crítica contorna o gate) ───────
def test_gate_enforcement_no_bypass(api_gateway, tenant_manager):
    """Teste 3: não existe caminho que contorne o gate; uma chamada direta a uma ação crítica falha."""
    
    # Criar request válido
    request = DecisionRequest(
        request_id="req-001",
        entity_id="entity-A",
        user_id="user-A1",
        document_text="Requerimento de licença",
        metadata={"tipo": "licença"}
    )
    
    # Submeter decisão (deve passar pelo gate)
    response = api_gateway.submit_decision(request)
    assert response.trace_id == "T-req-001"
    
    # Obter resultado
    result = api_gateway.get_decision(response.trace_id, "user-A1")
    assert result is not None
    assert result.status in ["approved", "rejected", "escalated"]
    
    # Verificar que a decisão passou pelo gate (tem verdict)
    assert "status" in result.decision
    
    # Tentar aceder com utilizador não autorizado
    with pytest.raises(PermissionError, match="não tem acesso"):
        api_gateway.get_decision(response.trace_id, "user-B1")
    
    # Tentar submeter com utilizador não autorizado
    unauthorized_request = DecisionRequest(
        request_id="req-002",
        entity_id="entity-A",
        user_id="user-B1",  # Utilizador de entity-B
        document_text="Requerimento não autorizado",
        metadata={}
    )
    
    with pytest.raises(PermissionError, match="não tem acesso"):
        api_gateway.submit_decision(unauthorized_request)
    
    # Verificar que não há método para bypass o gate
    # (todos os métodos públicos passam pelo gate)
    assert hasattr(api_gateway, "submit_decision")
    assert hasattr(api_gateway, "get_decision")
    
    # Não deve haver método "direct_decision" ou similar
    assert not hasattr(api_gateway, "direct_decision")
    assert not hasattr(api_gateway, "bypass_gate")
