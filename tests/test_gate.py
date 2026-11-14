import pytest
from core.models import TraceID, Proposal, Evidence
from policy.models import Rule, RuleSeverity, RuleStatus, RuleTestCase, RuleSet
from gate.validator import GateValidator
from gate.planner import FailurePlanner, FailPlan
from gate.gate import Gate
from policy.registry import RuleRegistry

@pytest.fixture
def trace_id():
    return TraceID()

@pytest.fixture
def rule_registry():
    reg = RuleRegistry()
    
    # Criar regra em estado DRAFT
    rule = Rule(
        id="R-001", version="1.0.0", name="Maioridade",
        description="Utilizador deve ter 18 ou mais anos",
        severity=RuleSeverity.HARD, author="test",
        expression="idade >= 18", status=RuleStatus.DRAFT,
        test_cases=[
            RuleTestCase(input_data={"idade": 20}, expected_result=True),
            RuleTestCase(input_data={"idade": 17}, expected_result=False)
        ]
    )
    
    # Seguir o fluxo correto: DRAFT → REVIEWED → APPROVED → ACTIVE
    reg.create_rule(rule)
    reg.review_rule("R-001", "reviewer")
    reg.approve_rule("R-001", "reviewer")
    reg.activate_rule("R-001")
    
    reg.create_rule_set("default", "1.0.0", ["R-001"])
    return reg

@pytest.fixture
def validator(rule_registry):
    return GateValidator(rule_registry)

@pytest.fixture
def gate(validator):
    return Gate(validator)

def test_defective_outputs_blocked_100_percent(trace_id, gate):
    """Teste 1: bateria de saídas defeituosas é bloqueada em 100% dos casos."""
    
    defective_proposals = [
        {"proposal": Proposal(trace_id=trace_id, agent="test", content={}, confidence=0.9),
         "context": {}, "desc": "conteúdo vazio"},
        
        {"proposal": Proposal(trace_id=trace_id, agent="test", 
                              content={"data_inicio": "2026-01-01", "data_fim": "2025-12-31"}, 
                              confidence=0.9),
         "context": {}, "desc": "data_fim < data_inicio"},
        
        {"proposal": Proposal(trace_id=trace_id, agent="test", 
                              content={"idade": 17}, confidence=0.9),
         "context": {}, "desc": "idade < 18"},
        
        {"proposal": Proposal(trace_id=trace_id, agent="test", 
                              content={"valor": 100}, confidence=0.1),
         "context": {}, "desc": "confiança baixa"},
        
        {"proposal": Proposal(trace_id=trace_id, agent="test", 
                              content={"prazo": "30 dias"}, confidence=0.9),
         "context": {
             "claims_to_verify": [{"text": "prazo de 30 dias", "source_id": "EV-MISSING", "requires_evidence": True}],
             "available_evidences": []
         },
         "desc": "afirmação sem evidência"}
    ]
    
    blocked_count = 0
    for item in defective_proposals:
        result = gate.evaluate(item["proposal"], item["context"])
        verdict = result["verdict"]
        
        is_blocked = verdict.status in {"rejected", "escalated"} or \
                     (verdict.status == "repaired" and result.get("plan", {}).get("action") == FailPlan.REPAIR)
        
        assert is_blocked, f"Proposta defeituosa ({item['desc']}) não foi bloqueada: status={verdict.status}"
        blocked_count += 1
    
    assert blocked_count == len(defective_proposals)

def test_false_positive_rate_below_5_percent(trace_id, gate):
    """Teste 2: a taxa de falsos alarmes sobre saídas corretas é <= 5%."""
    
    false_positives = 0
    for i in range(100):
        evidence = Evidence(
            source="test", content={"prazo": 30}, 
            content_hash=f"hash-{i}", metadata={}
        )
        proposal = Proposal(
            trace_id=trace_id, agent="test",
            content={"idade": 25, "valor": 100, "prazo": 30},
            confidence=0.95,
            evidence_ids=[evidence.id]
        )
        
        result = gate.evaluate(proposal, {
            "claims_to_verify": [{"text": "prazo de 30", "source_id": evidence.id, "requires_evidence": True}],
            "available_evidences": [evidence]
        })
        
        if result["verdict"].status in {"rejected", "escalated"}:
            false_positives += 1
    
    false_positive_rate = false_positives / 100
    assert false_positive_rate <= 0.05, f"Taxa de falsos positivos {false_positive_rate} > 5%"

def test_validator_failure_refuses_always(trace_id, rule_registry):
    """Teste 3: se o validador falha ou excede o tempo, o sistema recusa ou escala."""
    
    class BrokenValidator(GateValidator):
        def validate(self, proposal, context=None):
            raise RuntimeError("Validador falhou internamente")
    
    broken_gate = Gate(BrokenValidator(rule_registry))
    
    proposal = Proposal(
        trace_id=trace_id, agent="test",
        content={"idade": 25}, confidence=0.95
    )
    
    result = broken_gate.evaluate(proposal)
    
    assert result["verdict"].status == "rejected"
    assert "Erro no validador" in result["verdict"].reason
    assert result.get("validator_error") is True
