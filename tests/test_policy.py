import pytest
from policy.models import Rule, RuleSet, RuleStatus, RuleSeverity, RuleTestCase
from policy.registry import RuleRegistry
from policy.engine import RuleEvaluator, SecurityError


@pytest.fixture
def registry():
    return RuleRegistry()


@pytest.fixture
def sample_rule():
    return Rule(
        id="R-001",
        version="1.0.0",
        name="Maioridade",
        description="Utilizador deve ter 18 ou mais anos",
        severity=RuleSeverity.HARD,
        author="alice@example.com",
        expression="idade >= 18",
        test_cases=[
            RuleTestCase(input_data={"idade": 20}, expected_result=True, description="Adulto deve passar"),
            RuleTestCase(input_data={"idade": 17}, expected_result=False, description="Menor deve falhar")
        ]
    )


def test_active_rule_must_have_positive_and_negative_tests(registry, sample_rule):
    rule_no_tests = sample_rule.model_copy(update={'id': 'R-002', 'test_cases': []})
    registry.create_rule(rule_no_tests)
    registry.review_rule('R-002', 'bob@example.com')
    registry.approve_rule('R-002', 'bob@example.com')
    
    with pytest.raises(ValueError, match="não tem casos de teste"):
        registry.activate_rule('R-002')


def test_deterministic_evaluation(registry, sample_rule):
    registry.create_rule(sample_rule)
    registry.review_rule('R-001', 'bob@example.com')
    registry.approve_rule('R-001', 'bob@example.com')
    registry.activate_rule('R-001')
    
    rule_set = registry.create_rule_set("Teste", "1.0.0", ['R-001'])
    evaluator = RuleEvaluator(rule_set)
    
    results = [evaluator.evaluate({"idade": 20}) for _ in range(100)]
    
    first_result = results[0]
    for result in results[1:]:
        assert result == first_result, "Resultados não são determinísticos"
    
    assert first_result[0]['passed'] is True


def test_maker_checker_prevents_unauthorized_activation(registry, sample_rule):
    registry.create_rule(sample_rule)
    
    with pytest.raises(ValueError, match="não está em APPROVED"):
        registry.activate_rule('R-001')
    
    registry.review_rule('R-001', 'bob@example.com')
    registry.approve_rule('R-001', 'bob@example.com')
    
    activated_rule = registry.activate_rule('R-001')
    assert activated_rule.status == RuleStatus.ACTIVE
    assert activated_rule.author != activated_rule.reviewer


# NOVO TESTE: Prova de segurança contra injeção de código
def test_ast_evaluator_blocks_malicious_injection(registry, sample_rule):
    """Teste de segurança: o avaliador AST deve bloquear chamadas de função ou importações."""
    registry.create_rule(sample_rule)
    registry.review_rule('R-001', 'bob@example.com')
    registry.approve_rule('R-001', 'bob@example.com')
    registry.activate_rule('R-001')
    
    rule_set = registry.create_rule_set("Segurança", "1.0.0", ['R-001'])
    evaluator = RuleEvaluator(rule_set)
    
    # Simular uma regra corrompida que tenta executar código do sistema
    malicious_rule = Rule(
        id="R-MALICIOSA",
        version="1.0.0",
        name="Injeção",
        description="Tentativa de injeção",
        severity=RuleSeverity.HARD,
        author="atacante",
        expression="__import__('os').system('rm -rf /')",
        status=RuleStatus.ACTIVE
    )
    
    # Injetar manualmente no conjunto de regras para teste
    rule_set.rules.append(malicious_rule)
    
    # A avaliação deve falhar com SecurityError, NÃO executar o código
    results = evaluator.evaluate({"idade": 20})
    
    # Encontrar o resultado da regra maliciosa
    malicious_result = next(r for r in results if r['rule_id'] == 'R-MALICIOSA')
    
    assert malicious_result['verdict'] == 'ERROR'
    assert 'SecurityError' in malicious_result['error'] or 'Nó não permitido' in malicious_result['error']
    assert malicious_result['passed'] is False
