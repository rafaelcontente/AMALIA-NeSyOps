"""Testes do script de avaliação contínua do LLM."""
import json
import pytest
from unittest.mock import patch, Mock
from scripts.eval_llm_continuous import run_llm_evaluation

@pytest.fixture
def mock_golden_set(tmp_path):
    cases = [
        {"id": "1", "description": "Caso de teste 1 sobre João Silva em Lisboa"},
        {"id": "2", "description": "Caso de teste 2 sobre Maria em Porto"},
        {"id": "3", "description": "Caso de teste 3"},
        {"id": "4", "description": "Caso de teste 4"},
        {"id": "5", "description": "Caso de teste 5"}
    ]
    path = tmp_path / "golden_set.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    return str(path)

def test_llm_evaluation_passes_within_limits(mock_golden_set):
    """Testa que a avaliação passa quando as métricas estão dentro dos limites."""
    with patch("scripts.eval_llm_continuous.OllamaAdapter") as MockAdapter,          patch("scripts.eval_llm_continuous.HallucinationChecker") as MockChecker:
        
        mock_adapter_instance = Mock()
        mock_adapter_instance.is_healthy.return_value = True
        mock_adapter_instance.generate.return_value = {
            "status": "success",
            "content": "João Silva, Lisboa"
        }
        MockAdapter.return_value = mock_adapter_instance
        
        # Mock do checker para retornar válido (sem alucinações)
        mock_checker_instance = Mock()
        mock_checker_instance.check_entities.return_value = {
            "valid": True,
            "hallucinated": [],
            "checked_count": 2
        }
        MockChecker.return_value = mock_checker_instance
        
        result = run_llm_evaluation(golden_set_path=mock_golden_set, sample_size=5)
        
        assert result["status"] == "completed"
        assert result["passed"] is True
        assert result["total_cases_evaluated"] == 5
        assert result["hallucination_rate"] == 0.0

def test_llm_evaluation_fails_on_high_hallucination(mock_golden_set):
    """Testa que a avaliação falha quando a taxa de alucinação é alta."""
    with patch("scripts.eval_llm_continuous.OllamaAdapter") as MockAdapter:
        mock_adapter_instance = Mock()
        mock_adapter_instance.is_healthy.return_value = True
        mock_adapter_instance.generate.return_value = {
            "status": "success",
            "content": "Entidade Fictícia"
        }
        MockAdapter.return_value = mock_adapter_instance
        
        # Forçar limites muito baixos para garantir a falha no teste
        import scripts.eval_llm_continuous as eval_module
        original_limit = eval_module.MAX_HALLUCINATION_RATE
        eval_module.MAX_HALLUCINATION_RATE = 0.0 # 0% permitido
        
        try:
            result = run_llm_evaluation(golden_set_path=mock_golden_set, sample_size=5)
            assert result["passed"] is False
            assert result["hallucination_rate"] > 0.0
        finally:
            eval_module.MAX_HALLUCINATION_RATE = original_limit

def test_llm_evaluation_skips_when_unhealthy(mock_golden_set):
    """Testa que a avaliação é ignorada se o Ollama não estiver saudável."""
    with patch("scripts.eval_llm_continuous.OllamaAdapter") as MockAdapter:
        mock_adapter_instance = Mock()
        mock_adapter_instance.is_healthy.return_value = False
        MockAdapter.return_value = mock_adapter_instance
        
        result = run_llm_evaluation(golden_set_path=mock_golden_set, sample_size=5)
        
        assert result["status"] == "skipped"
        assert result["reason"] == "ollama_unavailable"
