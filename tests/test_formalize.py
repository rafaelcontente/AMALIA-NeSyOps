import pytest
from policy.registry import RuleRegistry
from policy.models import RuleStatus
from formalize.proposer import LLMProposer
from formalize.pipeline import FormalizationPipeline

@pytest.fixture
def registry():
    return RuleRegistry()

@pytest.fixture
def pipeline(registry):
    return FormalizationPipeline(registry, max_retries=3)

def test_fidelity_against_golden_set(registry, pipeline):
    normative_text = "O requerente deve ter residência fiscal em Portugal há mais de 12 meses."
    
    mock_llm = LLMProposer(responses=[
        {
            "expression": "meses_residencia > 12",
            "test_cases": [
                {"input": {"meses_residencia": 11}, "expected": False, "description": "11 meses (falha)"},
                {"input": {"meses_residencia": 12}, "expected": False, "description": "12 meses (falha, tem de ser >)"},
                {"input": {"meses_residencia": 13}, "expected": True, "description": "13 meses (passa)"},
            ]
        }
    ])
    
    rule = pipeline.formalize(normative_text, mock_llm, "Residencia_Fiscal", "llm-agent")
    
    assert rule.status == RuleStatus.DRAFT
    assert rule.expression == "meses_residencia > 12"
    assert len(rule.test_cases) == 3
    assert rule.test_cases[0].expected_result is False
    assert rule.test_cases[1].expected_result is False
    assert rule.test_cases[2].expected_result is True

def test_syntax_error_recovery_and_escalation(registry, pipeline):
    normative_text = "Artigo com sintaxe complexa..."
    
    # Mock do LLM falha 2 vezes (sintaxe) e acerta na 3ª
    mock_llm = LLMProposer(responses=[
        {"expression": "idade >= 18 &&", "test_cases": []},  # SyntaxError
        {"expression": "idade >= 18 &", "test_cases": []},   # SyntaxError
        {"expression": "idade >= 18", "test_cases": [{"input": {"idade": 18}, "expected": True}]}  # Correto
    ])
    
    rule = pipeline.formalize(normative_text, mock_llm, "Maioridade", "llm-agent")
    assert rule.expression == "idade >= 18"
    assert mock_llm.call_count == 3
    
    # Mock do LLM falha 3 vezes (sintaxe e segurança) -> deve escalar
    mock_llm_fail = LLMProposer(responses=[
        {"expression": "idade >= 18 &&", "test_cases": []},          # SyntaxError
        {"expression": "idade >= 18 &", "test_cases": []},           # SyntaxError
        {"expression": "__import__('os').system('rm -rf /')", "test_cases": []}  # SecurityError
    ])
    
    with pytest.raises(RuntimeError, match="Falha na formalização após 3 tentativas"):
        pipeline.formalize(normative_text, mock_llm_fail, "Regra_Falha", "llm-agent")

def test_activation_without_human_approval_fails(registry, pipeline):
    normative_text = "Regra que precisa de aprovação."
    
    mock_llm = LLMProposer(responses=[
        {"expression": "valor > 0", "test_cases": [{"input": {"valor": 1}, "expected": True}]}
    ])
    
    rule = pipeline.formalize(normative_text, mock_llm, "Valor_Positivo", "llm-agent")
    
    assert rule.status == RuleStatus.DRAFT
    
    with pytest.raises(ValueError, match="não está em APPROVED"):
        registry.activate_rule(rule.id)
    
    with pytest.raises(ValueError, match="não está em REVIEWED"):
        registry.approve_rule(rule.id, "jurista@example.com")
