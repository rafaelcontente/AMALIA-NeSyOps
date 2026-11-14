import pytest
from review.queue import ReviewQueue, EscalatedCase
from review.interface import ReviewInterface, HumanDecision
from review.auditor import PostHocAuditor
from datetime import datetime, timezone, timedelta

@pytest.fixture
def queue():
    return ReviewQueue()

@pytest.fixture
def review_interface(queue):
    return ReviewInterface(queue)

@pytest.fixture
def auditor(queue):
    return PostHocAuditor(queue, sample_rate=0.1)

# ─── Teste 1: Maker-checker (quem gerou não aprova) ─────────────────────────
def test_maker_checker_prevents_self_approval(queue, review_interface):
    """Teste 1: o utilizador que gerou a proposta não consegue aprovar o próprio caso."""
    
    # Criar caso com proposer_id = "agent-001"
    case = EscalatedCase(
        trace_id="T-001",
        proposal={"content": "Proposta de teste"},
        evidences=[{"id": "EV-001", "source": "doc.pdf"}],
        failed_rules=["R-020"],
        risk_score=0.8,
        confidence=0.3,
        proposer_id="agent-001"
    )
    
    case_id = queue.add(case)
    
    # Tentar aprovar com o mesmo ID do proposer deve falhar
    with pytest.raises(ValueError, match="Maker-checker violado"):
        review_interface.decide(
            case_id=case_id,
            reviewer_id="agent-001",  # Mesmo ID do proposer
            decision="approved",
            justification="Aprovado pelo próprio agente"
        )
    
    # Aprovar com ID diferente deve funcionar
    decision = review_interface.decide(
        case_id=case_id,
        reviewer_id="reviewer-001",  # ID diferente
        decision="approved",
        justification="Aprovado após revisão cuidadosa dos documentos"
    )
    
    assert decision.reviewer_id == "reviewer-001"
    assert decision.decision == "approved"

# ─── Teste 2: Decisão humana grava revisor, hora e justificação ─────────────
def test_human_decision_records_metadata(queue, review_interface):
    """Teste 2: toda a decisão humana grava revisor, hora e justificação, e liga ao trace."""
    
    case = EscalatedCase(
        trace_id="T-002",
        proposal={"content": "Proposta complexa"},
        evidences=[
            {"id": "EV-001", "source": "doc1.pdf"},
            {"id": "EV-002", "source": "doc2.pdf"},
            {"id": "EV-003", "source": "api.gov"}
        ],
        failed_rules=["R-012", "R-020"],
        risk_score=0.6,
        confidence=0.4,
        proposer_id="agent-002"
    )
    
    case_id = queue.add(case)
    
    # Decisão humana
    decision = review_interface.decide(
        case_id=case_id,
        reviewer_id="jurista-001",
        decision="corrected",
        justification="Aprovado com correção do prazo de 30 para 45 dias conforme artigo 45.º",
        corrections={"prazo": 45}
    )
    
    # Verificar metadados gravados
    assert decision.reviewer_id == "jurista-001"
    assert decision.decision == "corrected"
    assert "45 dias" in decision.justification
    assert decision.corrections == {"prazo": 45}
    assert decision.timestamp is not None
    assert decision.trace_id == "T-002"
    
    # Verificar que a decisão está ligada ao trace
    decisions_by_trace = review_interface.get_decisions_by_trace("T-002")
    assert len(decisions_by_trace) == 1
    assert decisions_by_trace[0].case_id == case_id

# ─── Teste 3: Fila cheia ordena por risco (maior primeiro) ─────────────────
def test_queue_priority_by_risk(queue):
    """Teste 3: com a fila cheia, os casos de maior risco são servidos primeiro."""
    
    # Criar 5 casos com riscos diferentes
    cases = [
        EscalatedCase(
            trace_id=f"T-{i}",
            proposal={"content": f"Proposta {i}"},
            risk_score=risk,
            confidence=0.5,
            proposer_id=f"agent-{i}"
        )
        for i, risk in enumerate([0.2, 0.9, 0.5, 0.8, 0.3])
    ]
    
    # Adicionar todos à fila
    for case in cases:
        queue.add(case)
    
    # Verificar que a fila tem 5 casos
    assert queue.size() == 5
    
    # Extrair casos na ordem de prioridade
    extracted = []
    while queue.size() > 0:
        case = queue.get_next()
        extracted.append(case.risk_score)
    
    # Verificar ordem: maior risco primeiro (0.9, 0.8, 0.5, 0.3, 0.2)
    assert extracted == [0.9, 0.8, 0.5, 0.3, 0.2], f"Ordem incorreta: {extracted}"
    
    # Verificar que nenhum caso se perdeu
    assert len(extracted) == 5
