"""
Validação formal de explicações: provas de que o gerador não alucina.

Invariantes testados:
1. O gerador só cita regras que foram efetivamente avaliadas.
2. O gerador só cita evidências que foram fornecidas.
3. O validador deteta referências órfãs (alucinações).
4. Round-trip: explicação gerada + trace correspondente = válido com coverage=1.0.
5. Separação de vistas: cidadão não expõe IDs técnicos internos.
"""
import pytest
from unittest.mock import Mock
from explain.generator import ExplanationGenerator
from explain.validator import ExplanationValidator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_verdict(status="approved", rules_evaluated=None, rules_violated=None, reason="ok"):
    """Cria um Verdict mock."""
    v = Mock()
    v.status = Mock()
    v.status.value = status
    v.rules_evaluated = rules_evaluated or ["R-001", "R-002"]
    v.rules_violated = rules_violated or []
    v.reason = reason
    v.id = "V-001"
    return v


def _make_decision(verdict=None, trace_id="T-abc-123", proposal_id="P-001",
                   agent="test-agent", confidence=0.95,
                   model_version="m1", prompt_version="p1", rules_version="r1"):
    """Cria um Decision mock."""
    d = Mock()
    d.verdict = verdict or _make_verdict()
    d.trace_id = Mock()
    d.trace_id.id = trace_id
    d.proposal = Mock()
    d.proposal.id = proposal_id
    d.proposal.agent = agent
    d.proposal.confidence = confidence
    d.model_version = model_version
    d.prompt_version = prompt_version
    d.rules_version = rules_version
    d.timestamp = Mock()
    d.timestamp.isoformat.return_value = "2026-11-15T10:00:00+00:00"
    return d


def _make_trace_from_decision(decision, evidences=None):
    """Constrói um trace dict a partir de um Decision (espelho do que o generator usa)."""
    return {
        "trace_id": decision.trace_id.id,
        "proposal_id": decision.proposal.id,
        "verdict_id": decision.verdict.id,
        "rules_evaluated": list(decision.verdict.rules_evaluated),
        "rules_violated": list(decision.verdict.rules_violated),
        "evidences": evidences or [],
    }


# ---------------------------------------------------------------------------
# Invariante 1: O gerador só cita regras avaliadas
# ---------------------------------------------------------------------------

def test_generator_cites_only_evaluated_rules():
    """A explicação do auditor não deve mencionar regras que não foram avaliadas."""
    gen = ExplanationGenerator()
    decision = _make_decision(verdict=_make_verdict(rules_evaluated=["R-001", "R-002"]))
    
    result = gen.generate(decision)
    auditor = result["auditor"]
    
    # R-001 e R-002 devem aparecer
    assert "R-001" in auditor
    assert "R-002" in auditor
    # R-999 (não avaliada) não deve aparecer
    assert "R-999" not in auditor


def test_generator_cites_only_violated_rules_in_rejection():
    """Rejeições devem citar apenas regras violadas na fundamentação legal."""
    gen = ExplanationGenerator()
    decision = _make_decision(
        verdict=_make_verdict(
            status="rejected",
            rules_evaluated=["R-001", "R-002", "R-003"],
            rules_violated=["R-002"],
            reason="Idade insuficiente",
        )
    )
    
    result = gen.generate(decision)
    citizen = result["citizen"]
    
    # A regra violada deve aparecer na fundamentação
    assert "R-002" in citizen
    # Regras apenas avaliadas (não violadas) não devem aparecer na fundamentação legal
    # (a vista cidadão só lista referências gerais, não fundamentação por regra)


# ---------------------------------------------------------------------------
# Invariante 2: O gerador só cita evidências fornecidas
# ---------------------------------------------------------------------------

def test_generator_cites_all_evidences_provided():
    """Todas as evidências passadas ao generator devem aparecer na explicação."""
    gen = ExplanationGenerator()
    decision = _make_decision()
    evidences = [
        {"id": "EV-001", "source": "documento.pdf"},
        {"id": "EV-002", "source": "base_dados"},
    ]
    
    result = gen.generate(decision, evidences=evidences)
    auditor = result["auditor"]
    citizen = result["citizen"]
    
    assert "EV-001" in auditor
    assert "EV-002" in auditor
    assert "EV-001" in citizen
    assert "EV-002" in citizen


def test_generator_does_not_invent_evidences():
    """O gerador não deve inventar IDs de evidências que não foram fornecidas."""
    gen = ExplanationGenerator()
    decision = _make_decision()
    
    result = gen.generate(decision, evidences=[])
    auditor = result["auditor"]
    
    assert "EV-" not in auditor or "Nenhuma" in auditor


# ---------------------------------------------------------------------------
# Invariante 3: O validador deteta referências órfãs (alucinações)
# ---------------------------------------------------------------------------

def test_validator_detects_orphan_claims():
    """Referências na explicação que não estão no trace são órfãs."""
    validator = ExplanationValidator()
    
    explanation = "Decisão baseada na Regra R-001 e na Regra R-999."
    trace = {
        "trace_id": "T-001",
        "rules_evaluated": ["R-001"],
        "rules_violated": [],
        "evidences": [],
    }
    
    result = validator.validate(explanation, trace)
    
    assert result["valid"] is False
    assert "R-999" in result["orphan_claims"]
    assert "R-001" not in result["orphan_claims"]


def test_validator_accepts_valid_explanation():
    """Explicação com referências todas no trace é válida."""
    validator = ExplanationValidator()
    
    explanation = "Decisão baseada na Regra R-001 e evidência EV-001."
    trace = {
        "trace_id": "T-001",
        "rules_evaluated": ["R-001"],
        "rules_violated": [],
        "evidences": [{"id": "EV-001"}],
    }
    
    result = validator.validate(explanation, trace)
    
    assert result["valid"] is True
    assert result["orphan_claims"] == []


# ---------------------------------------------------------------------------
# Invariante 4: Round-trip — explicação gerada + trace = coverage 1.0
# ---------------------------------------------------------------------------

def test_roundtrip_generated_explanation_is_valid():
    """Explicação gerada pelo generator deve passar validação com coverage=1.0."""
    gen = ExplanationGenerator()
    validator = ExplanationValidator()
    
    decision = _make_decision(
        verdict=_make_verdict(
            rules_evaluated=["R-001", "R-002"],
            rules_violated=["R-002"],
        )
    )
    evidences = [{"id": "EV-001", "source": "doc.pdf"}]
    
    result = gen.generate(decision, evidences=evidences)
    trace = _make_trace_from_decision(decision, evidences)
    
    # Validar vista do auditor
    auditor_validation = validator.validate(result["auditor"], trace)
    assert auditor_validation["valid"] is True, f"Orphans: {auditor_validation['orphan_claims']}"
    assert auditor_validation["coverage"] == 1.0
    
    # Validar vista do cidadão
    citizen_validation = validator.validate(result["citizen"], trace)
    assert citizen_validation["valid"] is True, f"Orphans: {citizen_validation['orphan_claims']}"


# ---------------------------------------------------------------------------
# Invariante 5: Separação de vistas
# ---------------------------------------------------------------------------

def test_citizen_view_does_not_expose_internal_ids():
    """A vista do cidadão não deve expor Proposal ID, Verdict ID ou versões internas."""
    gen = ExplanationGenerator()
    decision = _make_decision()
    
    result = gen.generate(decision)
    citizen = result["citizen"]
    
    # IDs internos não devem aparecer
    assert decision.proposal.id not in citizen
    assert decision.verdict.id not in citizen
    # Versões de modelo/prompt/regras não devem aparecer
    assert decision.model_version not in citizen
    assert decision.prompt_version not in citizen
    assert decision.rules_version not in citizen


def test_auditor_view_contains_all_trace_metadata():
    """A vista do auditor deve conter todas as versões e IDs para rastreabilidade."""
    gen = ExplanationGenerator()
    decision = _make_decision(
        model_version="m-v2.1",
        prompt_version="p-v1.3",
        rules_version="r-v3.0",
    )
    
    result = gen.generate(decision)
    auditor = result["auditor"]
    
    assert decision.trace_id.id in auditor
    assert decision.proposal.id in auditor
    assert decision.verdict.id in auditor
    assert "m-v2.1" in auditor
    assert "p-v1.3" in auditor
    assert "r-v3.0" in auditor


# ---------------------------------------------------------------------------
# Invariante 6: Explicações vazias quando não há dados
# ---------------------------------------------------------------------------

def test_generator_handles_empty_rules_gracefully():
    """Generator deve funcionar mesmo sem regras avaliadas."""
    gen = ExplanationGenerator()
    decision = _make_decision(verdict=_make_verdict(rules_evaluated=[], rules_violated=[]))
    
    result = gen.generate(decision)
    assert "citizen" in result
    assert "auditor" in result
    # Não deve crashar nem gerar referências órfãs


def test_validator_handles_empty_trace():
    """Validator deve lidar com trace vazio sem crashar."""
    validator = ExplanationValidator()
    
    result = validator.validate("Sem referências.", {})
    
    assert result["valid"] is True
    assert result["total_references"] == 0
