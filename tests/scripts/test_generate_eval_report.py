"""Testes do script de geração de relatório de avaliação."""
import json
import pathlib
import pytest
from eval.category_evaluator import CategoryEvaluator
from scripts.generate_eval_report import generate_evaluation_report

@pytest.fixture
def temp_reports_dir(tmp_path):
    return tmp_path / "reports"

def test_generate_report_creates_json_and_md(temp_reports_dir):
    evaluator = CategoryEvaluator("eval/golden_set_v3.json")
    
    def perfect_decision(case):
        return {
            "decision": case["expected_decision"],
            "rules_violated": case["expected_rules_violated"]
        }
        
    json_path, md_path = generate_evaluation_report(evaluator, perfect_decision, output_dir=str(temp_reports_dir))
    
    assert json_path.exists()
    assert md_path.exists()
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert "git_commit" in data
    assert "generated_at" in data
    assert "delta_accuracy" in data
    assert data["global_metrics"]["accuracy"] == 1.0

def test_generate_report_calculates_delta(temp_reports_dir):
    evaluator = CategoryEvaluator("eval/golden_set_v3.json")
    
    def perfect_decision(case):
        return {"decision": case["expected_decision"], "rules_violated": case["expected_rules_violated"]}
        
    # Primeira execução (sem baseline)
    generate_evaluation_report(evaluator, perfect_decision, output_dir=str(temp_reports_dir))
    
    # Segunda execução (com baseline)
    json_path, md_path = generate_evaluation_report(evaluator, perfect_decision, output_dir=str(temp_reports_dir))
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["delta_accuracy"] == 0.0 # Mesma accuracy

def test_report_md_contains_expected_sections(temp_reports_dir):
    evaluator = CategoryEvaluator("eval/golden_set_v3.json")
    
    def perfect_decision(case):
        return {"decision": case["expected_decision"], "rules_violated": case["expected_rules_violated"]}
        
    json_path, md_path = generate_evaluation_report(evaluator, perfect_decision, output_dir=str(temp_reports_dir))
    
    md_content = md_path.read_text(encoding="utf-8")
    
    assert "# Relatório de Avaliação - AMALIA-NeSyOps" in md_content
    assert "**Commit Git:**" in md_content
    assert "## Métricas Globais" in md_content
    assert "## Métricas por Categoria" in md_content
    assert "licenciamento_comercial" in md_content
