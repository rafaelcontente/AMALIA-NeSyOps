import pytest
from core.models import TraceID
from agents.llm_client import LLMClient
from agents.tools import ToolRegistry
from agents.orchestrator import AgentOrchestrator
from agents.extractor import ExtractionAgent

@pytest.fixture
def trace_id():
    return TraceID()

@pytest.fixture
def tool_registry():
    registry = ToolRegistry(allowed_tools=["search", "validate"])
    registry.register_tool("search", lambda query: {"result": f"found: {query}"})
    registry.register_tool("validate", lambda data: {"valid": True})
    registry.register_tool("forbidden", lambda: {"secret": "data"})
    return registry

# ─── Teste 1: Taxa de sucesso >= 95% em 100 execuções ───────────────────────
def test_schema_validation_rate(trace_id):
    """Teste 1: em 100 execuções, pelo menos 95% passam validação de schema."""
    # Mock do LLM com 100 respostas válidas
    valid_responses = [
        {
            "fields": {"nome": "João Silva", "idade": 30},
            "confidence": 0.95
        }
        for _ in range(100)
    ]
    
    llm_client = LLMClient(model_name="amalia-7b-v1", responses=valid_responses)
    tool_registry = ToolRegistry(allowed_tools=[])
    agent = ExtractionAgent(llm_client, tool_registry)
    
    success_count = 0
    for _ in range(100):
        result = agent.extract("Requerimento de João Silva, 30 anos", trace_id)
        if result.get("status") == "completed":
            success_count += 1
    
    success_rate = success_count / 100
    assert success_rate >= 0.95, f"Taxa de sucesso {success_rate} < 95%"

# ─── Teste 2: Loop é interrompido e escalado ────────────────────────────────
def test_loop_detection_and_escalation(trace_id):
    """Teste 2: agente em loop é interrompido ao atingir limite de passos."""
    # Agente que repete o mesmo input (simula loop)
    def looping_agent(input_data, tid):
        return {
            "status": "continue",
            "next_input": {"loop": True}  # Sempre o mesmo
        }
    
    orchestrator = AgentOrchestrator(max_steps=5)
    result = orchestrator.run(looping_agent, {"loop": True}, trace_id)
    
    assert result["status"] == "loop_detected"
    assert result["step"] <= 5

# ─── Teste 3: Ferramenta fora da whitelist é bloqueada ──────────────────────
def test_tool_whitelist_blocks_unauthorized(tool_registry, trace_id):
    """Teste 3: chamada a ferramenta fora da whitelist é bloqueada e registada."""
    # Ferramenta permitida
    result = tool_registry.call_tool("search", {"query": "test"}, str(trace_id))
    assert result == {"result": "found: test"}
    
    # Ferramenta bloqueada
    with pytest.raises(PermissionError, match="não está na lista de permissões"):
        tool_registry.call_tool("forbidden", {}, str(trace_id))
    
    # Verificar audit log
    audit_log = tool_registry.get_audit_log()
    blocked_entries = [e for e in audit_log if e["status"] == "blocked"]
    assert len(blocked_entries) == 1
    assert blocked_entries[0]["tool_name"] == "forbidden"
