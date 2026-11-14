"""Testes do Golden Set V3 e do CategoryEvaluator."""
import pytest
import json
import pathlib
from eval.category_evaluator import CategoryEvaluator

@pytest.fixture
def evaluator():
    return CategoryEvaluator("eval/golden_set_v3.json")

def test_golden_set_v3_has_200_cases():
    """O golden set v3 deve ter pelo menos 200 casos."""
    with open("eval/golden_set_v3.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 200, f"Esperado >= 200 casos, encontrado {len(data)}"

def test_golden_set_v3_has_4_categories():
    """O golden set deve cobrir 4 categorias distintas."""
    with open("eval/golden_set_v3.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    categories = set(case["category"] for case in data)
    assert len(categories) == 4
    assert "licenciamento_comercial" in categories
    assert "subsidios_sociais" in categories
    assert "contraordenacoes_ambientais" in categories
    assert "saude_publica" in categories

def test_category_evaluator_calculates_global_metrics(evaluator):
    """O avaliador deve calcular métricas globais corretas."""
    def perfect_decision(case):
        return {
            "decision": case["expected_decision"],
            "rules_violated": case["expected_rules_violated"]
        }
    
    report = evaluator.evaluate(perfect_decision)
    
    assert report["global_metrics"]["accuracy"] == 1.0
    assert report["global_metrics"]["f1_score"] == 1.0
    assert report["global_metrics"]["total_cases"] >= 200
    assert report["total_errors"] == 0

def test_category_evaluator_calculates_per_category_metrics(evaluator):
    """O avaliador deve calcular métricas desagregadas por categoria."""
    def perfect_decision(case):
        return {
            "decision": case["expected_decision"],
            "rules_violated": case["expected_rules_violated"]
        }
    
    report = evaluator.evaluate(perfect_decision)
    
    assert "licenciamento_comercial" in report["category_metrics"]
    assert "subsidios_sociais" in report["category_metrics"]
    
    for cat, metrics in report["category_metrics"].items():
        assert metrics["total_cases"] == 50
        assert metrics["accuracy"] == 1.0

def test_category_evaluator_detects_errors(evaluator):
    """O avaliador deve detetar quando a decisão está errada."""
    def bad_decision(case):
        return {
            "decision": "approved",
            "rules_violated": []
        }
    
    report = evaluator.evaluate(bad_decision)
    
    assert report["total_errors"] > 0
    assert report["global_metrics"]["accuracy"] < 1.0
    assert report["global_metrics"]["recall"] < 1.0
