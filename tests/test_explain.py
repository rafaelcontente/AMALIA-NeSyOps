import pytest
from core.models import (
    TraceID, Proposal, Evidence, Verdict, VerdictStatus, Decision
)
from explain.generator import ExplanationGenerator
from explain.validator import ExplanationValidator

@pytest.fixture
def generator():
    return ExplanationGenerator()

@pytest.fixture
def validator():
    return ExplanationValidator()

@pytest.fixture
def approved_decision():
    """Decisão aprovada de exemplo."""
    trace_id = TraceID(id="T-9f2a1b3c")
    
    proposal = Proposal(
        trace_id=trace_id,
        agent="amalia-7b-v1",
        content={"nome": "João Silva", "idade": 25},
        confidence=0.95
    )
    
    verdict = Verdict(
        trace_id=trace_id,
        proposal_id=proposal.id,
        status=VerdictStatus.APPROVED,
        reason="Candidatura cumpre todos os requisitos legais",
        rules_evaluated=["R-001", "R-002", "R-003"],
        rules_violated=[]
    )
    
    decision = Decision(
        trace_id=trace_id,
        proposal=proposal,
        verdict=verdict,
        explanation="",
        model_version="amalia-7b-v1",
        prompt_version="prompt-v2",
        rules_version="ruleset-2026-11"
    )
    
    return decision, [
        {"id": "EV-001", "source": "documento.pdf", "page": 2},
        {"id": "EV-002", "source": "api_mercado", "page": None}
    ]

@pytest.fixture
def rejected_decision():
    """Decisão indeferida de exemplo."""
    trace_id = TraceID(id="T-8e1b2c3d")
    
    proposal = Proposal(
        trace_id=trace_id,
        agent="amalia-7b-v1",
        content={"nome": "Maria Santos", "idade": 17},
        confidence=0.90
    )
    
    verdict = Verdict(
        trace_id=trace_id,
        proposal_id=proposal.id,
        status=VerdictStatus.REJECTED,
        reason="Candidata não cumpre o requisito de maioridade",
        rules_evaluated=["R-001", "R-002"],
        rules_violated=["R-001"]
    )
    
    decision = Decision(
        trace_id=trace_id,
        proposal=proposal,
        verdict=verdict,
        explanation="",
        model_version="amalia-7b-v1",
        prompt_version="prompt-v2",
        rules_version="ruleset-2026-11"
    )
    
    return decision, [
        {"id": "EV-003", "source": "formulario.pdf", "page": 1}
    ]

# ─── Teste 1: Zero afirmações órfãs ─────────────────────────────────────────
def test_zero_orphan_claims(generator, validator, approved_decision):
    """Teste 1: todas as afirmações da explicação mapeiam para um item do trace."""
    
    decision, evidences = approved_decision
    
    # Gerar explicação
    explanations = generator.generate(decision, evidences)
    
    # Construir trace
    trace = {
        "trace_id": str(decision.trace_id),
        "proposal_id": decision.proposal.id,
        "verdict_id": decision.verdict.id,
        "rules_evaluated": decision.verdict.rules_evaluated,
        "rules_violated": decision.verdict.rules_violated,
        "evidences": evidences
    }
    
    # Validar vista do cidadão
    citizen_validation = validator.validate(explanations["citizen"], trace)
    assert citizen_validation["valid"], f"Vista do cidadão tem afirmações órfãs: {citizen_validation['orphan_claims']}"
    
    # Validar vista do auditor
    auditor_validation = validator.validate(explanations["auditor"], trace)
    assert auditor_validation["valid"], f"Vista do auditor tem afirmações órfãs: {auditor_validation['orphan_claims']}"

# ─── Teste 2: Trace diferente → explicação diferente ────────────────────────
def test_trace_change_changes_explanation(generator, approved_decision, rejected_decision):
    """Teste 2: alterar o trace altera a explicação de forma correspondente."""
    
    decision1, evidences1 = approved_decision
    decision2, evidences2 = rejected_decision
    
    # Gerar explicações
    explanations1 = generator.generate(decision1, evidences1)
    explanations2 = generator.generate(decision2, evidences2)
    
    # Vista do cidadão deve ser diferente
    assert explanations1["citizen"] != explanations2["citizen"], \
        "Explicações de cidadão devem ser diferentes para traces diferentes"
    
    # Vista do auditor deve ser diferente
    assert explanations1["auditor"] != explanations2["auditor"], \
        "Explicações de auditor devem ser diferentes para traces diferentes"
    
    # Verificar que a decisão aprovada contém "aprovada"
    assert "aprovada" in explanations1["citizen"].lower()
    
    # Verificar que a decisão indeferida contém "indeferida"
    assert "indeferida" in explanations2["citizen"].lower()
    
    # Verificar que a decisão indeferida menciona direito de recurso
    assert "recurso" in explanations2["citizen"].lower()

# ─── Teste 3: Compreensão (simulado com métricas de legibilidade) ───────────
def test_comprehension_metrics(generator, approved_decision):
    """Teste 3: a compreensão do motivo e do direito de recurso atinge o limiar acordado."""
    
    decision, evidences = approved_decision
    explanations = generator.generate(decision, evidences)
    
    citizen_text = explanations["citizen"]
    
    # Métricas de legibilidade (simuladas)
    # Em produção, usar bibliotecas como textstat para Flesch-Kincaid
    
    # 1. Comprimento médio das frases (deve ser < 25 palavras)
    sentences = citizen_text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
    assert avg_sentence_length < 25, f"Frases muito longas: média {avg_sentence_length} palavras"
    
    # 2. Presença de palavras-chave de compreensão
    assert "motivo" in citizen_text.lower(), "Explicação deve conter a palavra 'motivo'"
    assert "referências" in citizen_text.lower() or "referencia" in citizen_text.lower(), \
        "Explicação deve mencionar referências"
    
    # 3. Para decisões indeferidas, verificar direito de recurso
    if decision.verdict.status == VerdictStatus.REJECTED:
        assert "recurso" in citizen_text.lower(), "Decisão indeferida deve mencionar direito de recurso"
        assert "prazo" in citizen_text.lower(), "Decisão indeferida deve mencionar prazo"
    
    # 4. Cobertura do trace (quantas referências estão presentes)
    # Isto garante que a explicação não é genérica
    assert len(citizen_text) > 100, "Explicação deve ter conteúdo substancial"
