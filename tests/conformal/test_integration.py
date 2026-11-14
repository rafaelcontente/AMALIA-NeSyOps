"""Testes de integração: conformal prediction + golden set v2."""
import pytest
import json
import numpy as np
from pathlib import Path
from conformal import ConformalPredictor

@pytest.fixture
def golden_set_with_probabilities():
    """Carrega golden set v2 e gera probabilidades sintéticas."""
    with open("eval/golden_set_v2.json", "r", encoding="utf-8") as f:
        golden_set = json.load(f)
    
    np.random.seed(42)
    
    cases = []
    for case in golden_set["cases"]:
        expected = case["expected_decision"]
        
        # Gerar probabilidades
        if expected == "approved":
            if np.random.random() < 0.85:
                prob_approved = 0.7 + np.random.random() * 0.2
                prob_rejected = 0.1 + np.random.random() * 0.1
                prob_escalated = 1.0 - prob_approved - prob_rejected
            else:
                prob_rejected = 0.6 + np.random.random() * 0.2
                prob_approved = 0.2 + np.random.random() * 0.1
                prob_escalated = 1.0 - prob_approved - prob_rejected
        elif expected == "rejected":
            if np.random.random() < 0.85:
                prob_rejected = 0.7 + np.random.random() * 0.2
                prob_approved = 0.1 + np.random.random() * 0.1
                prob_escalated = 1.0 - prob_approved - prob_rejected
            else:
                prob_approved = 0.6 + np.random.random() * 0.2
                prob_rejected = 0.2 + np.random.random() * 0.1
                prob_escalated = 1.0 - prob_approved - prob_rejected
        else:  # expected == "escalated"
            if np.random.random() < 0.85:
                prob_escalated = 0.7 + np.random.random() * 0.2
                prob_approved = 0.1 + np.random.random() * 0.1
                prob_rejected = 1.0 - prob_approved - prob_escalated
            else:
                prob_approved = 0.5 + np.random.random() * 0.1
                prob_rejected = 0.3 + np.random.random() * 0.1
                prob_escalated = 1.0 - prob_approved - prob_rejected
        
        proba = {
            "approved": max(0.01, prob_approved),
            "rejected": max(0.01, prob_rejected),
            "escalated": max(0.01, prob_escalated)
        }
        
        cases.append({
            "id": case["id"],
            "category": case["category"],
            "expected": expected,
            "probabilities": proba
        })
    
    return cases

def test_conformal_coverage_on_golden_set(golden_set_with_probabilities):
    """Mede cobertura empírica do conformal predictor no golden set."""
    cases = golden_set_with_probabilities
    
    # Dividir em calibração (60%) e teste (40%)
    split_idx = int(len(cases) * 0.6)
    cal_cases = cases[:split_idx]
    test_cases = cases[split_idx:]
    
    # Calibrar
    predictor = ConformalPredictor(alpha=0.1)
    cal_preds = [c["probabilities"] for c in cal_cases]
    cal_labels = [c["expected"] for c in cal_cases]
    predictor.calibrate(cal_preds, cal_labels)
    
    # Testar
    test_preds = [c["probabilities"] for c in test_cases]
    test_labels = [c["expected"] for c in test_cases]
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    # Cobertura empírica
    covered = sum(
        1 for pred, label in zip(predictions, test_labels)
        if label in pred.prediction_set
    )
    coverage = covered / len(test_labels)
    
    print(f"\n=== Conformal Coverage on Golden Set ===")
    print(f"Calibration set: {len(cal_cases)} cases")
    print(f"Test set: {len(test_cases)} cases")
    print(f"Target coverage: 90% (alpha=0.1)")
    print(f"Actual coverage: {coverage:.2%}")
    print(f"Average set size: {np.mean([len(p.prediction_set) for p in predictions]):.2f}")
    print(f"Calibration quantile: {predictor.calibration.quantile:.3f}")
    
    # Cobertura deve ser >= 70% (ajustado para dataset pequeno)
    assert coverage >= 0.70, f"Coverage {coverage:.2%} < 70%"
    
    # Guardar resultados
    report = {
        "calibration_size": len(cal_cases),
        "test_size": len(test_cases),
        "target_coverage": 0.9,
        "actual_coverage": round(coverage, 3),
        "average_set_size": round(np.mean([len(p.prediction_set) for p in predictions]), 2),
        "quantile": round(predictor.calibration.quantile, 3),
    }
    
    Path("reports/conformal_coverage.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print("✓ Saved to reports/conformal_coverage.json")

def test_conformal_coverage_by_category(golden_set_with_probabilities):
    """Mede cobertura por categoria para detectar distribuição deslocada."""
    cases = golden_set_with_probabilities
    
    # Calibrar em todo o dataset
    predictor = ConformalPredictor(alpha=0.1)
    cal_preds = [c["probabilities"] for c in cases]
    cal_labels = [c["expected"] for c in cases]
    predictor.calibrate(cal_preds, cal_labels)
    
    # Gerar prediction sets
    predictions = [predictor.predict_set(c["probabilities"]) for c in cases]
    
    # Agrupar por categoria
    from collections import defaultdict
    by_category = defaultdict(list)
    for case, pred in zip(cases, predictions):
        by_category[case["category"]].append((pred, case["expected"]))
    
    print(f"\n=== Coverage by Category ===")
    for category, items in sorted(by_category.items()):
        covered = sum(1 for pred, label in items if label in pred.prediction_set)
        coverage = covered / len(items)
        print(f"{category:20s}: {coverage:.2%} ({covered}/{len(items)})")
        
        # Cada categoria deve ter cobertura >= 60%
        assert coverage >= 0.60, f"{category} coverage {coverage:.2%} < 60%"

def test_conformal_shifted_distribution(golden_set_with_probabilities):
    """Testa conformal sob distribuição deslocada (casos limítrofes)."""
    cases = golden_set_with_probabilities
    
    # Filtrar apenas casos limítrofes
    borderline_cases = [c for c in cases if c["category"] == "limítrofe"]
    
    # Calibrar em casos normais (não limítrofes)
    normal_cases = [c for c in cases if c["category"] != "limítrofe"]
    
    predictor = ConformalPredictor(alpha=0.1)
    cal_preds = [c["probabilities"] for c in normal_cases]
    cal_labels = [c["expected"] for c in normal_cases]
    predictor.calibrate(cal_preds, cal_labels)
    
    # Testar em casos limítrofes (distribuição deslocada)
    test_preds = [c["probabilities"] for c in borderline_cases]
    test_labels = [c["expected"] for c in borderline_cases]
    
    predictions = [predictor.predict_set(pred) for pred in test_preds]
    
    covered = sum(
        1 for pred, label in zip(predictions, test_labels)
        if label in pred.prediction_set
    )
    coverage = covered / len(test_labels) if test_labels else 0.0
    
    print(f"\n=== Shifted Distribution Test ===")
    print(f"Calibration: {len(normal_cases)} normal cases")
    print(f"Test: {len(borderline_cases)} borderline cases")
    print(f"Coverage on borderline: {coverage:.2%}")
    print(f"Average set size: {np.mean([len(p.prediction_set) for p in predictions]):.2f}")
    
    # Em distribuição deslocada, cobertura pode ser menor mas ainda razoável
    assert coverage >= 0.60, f"Shifted coverage {coverage:.2%} < 60%"
